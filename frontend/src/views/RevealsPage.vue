<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Reveals"
    create-button-text="Add Reveal"
    empty-message="No reveals yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="revealFilterTabs"
        :characters="characters"
      />
    </template>
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading reveals...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedReveal && !showCreateForm"
        icon="🧠"
        title="No Reveal Selected"
        message="Select an influence reveal from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <RevealForm
          :characters="characters"
          :is-editing="false"
          @save="handleCreateSave"
          @cancel="handleCancelCreate"
        />
      </div>

      <RevealCard
        v-else-if="selectedReveal"
        :reveal="selectedReveal"
        :characters="characters"
        :current-influence-level="18"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import RevealCard from '../components/RevealCard.vue'
  import RevealForm from '../components/RevealForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useRevealStore } from '../stores/reveals.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { applyCharacterFilters, applyCharacterAttributeFilters } from '../utils/filterUtils.js'
  import { getCharacters } from '../services/api.js'

  export default {
    name: 'RevealsPage',
    components: {
      SplitViewLayout,
      EmptyState,
      RevealCard,
      RevealForm,
      FilterPanel,
    },
    setup() {
      const route = useRoute()

      // Initialize stores
      const revealStore = useRevealStore()
      const gameDataStore = useGameDataStore()

      // Reactive refs from stores
      const {
        entities,
        loading,
        error,
        selectedEntityId,
        selectedEntity: selectedReveal,
        showCreateForm,
      } = storeToRefs(revealStore)

      const { data: gameData } = storeToRefs(gameDataStore)

      // Actions
      const {
        loadEntities,
        createEntity,
        updateEntity,
        deleteEntity,
        selectEntity,
        startCreate,
        cancelCreate,
        clearEntities,
      } = revealStore

      const characters = ref([])

      // Reveal filter tabs configuration
      const revealFilterTabs = [
        { id: 'characters', label: 'Characters' },
        { id: 'race', label: 'Race' },
        { id: 'alignment', label: 'Alignment' },
      ]

      // Character filtering state
      const activeFilters = ref({
        characters: [], // Use 'characters' to match the tab id
        characterIds: [], // Keep for compatibility with applyCharacterFilters
        showUnassigned: false,
        race: [],
        alignment: [],
      })

      const loadCharacters = async () => {
        try {
          characters.value = await getCharacters()
        } catch (err) {
          console.error('Error loading characters:', err)
        }
      }

      const handleCreateSave = async (formData) => {
        try {
          await createEntity(formData)
        } catch (err) {
          // Error handling is done in reveal store
        }
      }

      const handleCancelCreate = () => {
        cancelCreate()
      }

      // Handle world changes
      const handleWorldChange = (event) => {
        clearEntities()
        characters.value = []
        loadEntities()
        loadCharacters()
      }

      onMounted(async () => {
        await gameDataStore.load()
        await loadEntities()
        await loadCharacters()

        // Listen for world changes
        window.addEventListener('world-changed', handleWorldChange)

        // Auto-select reveal if ID is provided in query params
        const revealId = route.query.id
        if (revealId) {
          const id = parseInt(revealId)
          if (!isNaN(id) && entities.value.length > 0) {
            selectEntity(id)
          }
        }
      })

      // Clean up event listener on unmount
      onUnmounted(() => {
        window.removeEventListener('world-changed', handleWorldChange)
      })

      // Filtered entities based on character filters and character attributes
      const filteredEntities = computed(() => {
        // First apply character ID filters (existing functionality)
        let filtered = applyCharacterFilters(entities.value, activeFilters.value)

        // Then apply character attribute filters (new functionality)
        filtered = applyCharacterAttributeFilters(filtered, activeFilters.value, characters.value)

        return filtered
      })

      const hasActiveCharacterFilters = computed(() => {
        return (
          activeFilters.value.characterIds.length > 0 ||
          activeFilters.value.showUnassigned ||
          activeFilters.value.race.length > 0 ||
          activeFilters.value.alignment.length > 0
        )
      })

      const clearCharacterFilters = () => {
        activeFilters.value.characterIds = []
        activeFilters.value.showUnassigned = false
        activeFilters.value.race = []
        activeFilters.value.alignment = []
      }

      return {
        gameData,
        entities,
        filteredEntities,
        activeFilters,
        revealFilterTabs,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedReveal,
        characters,
        hasActiveCharacterFilters,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        handleCreateSave,
        handleCancelCreate,
        clearCharacterFilters,
      }
    },
  }
</script>

<style scoped>
  .character-field {
    margin-bottom: 1.5rem;
  }

  .character-selection {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    max-height: 150px;
    overflow-y: auto;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
  }

  .character-checkbox {
    display: flex;
    align-items: center;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    width: 100%;
    font-size: 0.9rem;
  }

  .character-option:hover {
    background-color: #e9ecef;
  }

  .character-option input[type='checkbox'] {
    margin: 0;
    transform: scale(0.9);
  }

  .character-option span {
    font-weight: 500;
    color: #495057;
  }

  /* Level toggle styles */
  .level-toggle {
    margin-bottom: 1rem;
  }

  .level-toggle-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    font-weight: 500;
    color: #495057;
  }

  .level-toggle-option:hover {
    border-color: #007bff;
    background: #e3f2fd;
  }

  .level-toggle-option input[type='checkbox'] {
    margin: 0;
    transform: scale(1.1);
  }

  /* Threshold section styles using shared design tokens */
  .threshold-section {
    margin-bottom: var(--spacing-xl);
  }

  .threshold-slider {
    margin-bottom: var(--spacing-lg);
  }

  .threshold-slider:last-child {
    margin-bottom: 0;
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--border-default);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
    border: none;
  }

  .required {
    color: #dc3545;
    font-weight: bold;
  }

  /* Level 3 divider toggle styles */
  .level-toggle-in-divider {
    position: relative;
    margin: var(--spacing-xl) 0 var(--spacing-lg) 0;
  }

  .level-toggle-in-divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--border-default);
    z-index: 1;
  }

  .level-toggle-in-divider .level-toggle-option {
    position: relative;
    z-index: 2;
    background: var(--bg-white);
    margin: 0 auto;
    width: fit-content;
    padding: var(--spacing-sm) var(--spacing-lg);
  }

  /* Ensure text areas take full width */
  .shared-field-full-width :deep(.shared-word-counter-field) {
    width: 100% !important;
  }

  .shared-field-full-width :deep(.shared-textarea) {
    width: 100% !important;
    box-sizing: border-box;
    min-width: 100%;
  }
</style>
