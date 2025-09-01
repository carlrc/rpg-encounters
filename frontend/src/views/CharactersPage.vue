<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Characters"
    create-button-text="Add Character"
    empty-message="No characters yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="characterFilterTabs"
      />
    </template>
    <template #footer-actions>
      <ImportButton entity-type="Character" :importing="importing" @import="handleImportFile" />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading characters...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedCharacter && !showCreateForm"
        icon="👤"
        title="No Character Selected"
        message="Select a character from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <CharacterForm :is-editing="false" @save="handleCreateSave" @cancel="handleCancelCreate" />
      </div>

      <CharacterCard
        v-else-if="selectedCharacter"
        :character="selectedCharacter"
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
  import CharacterCard from '../components/CharacterCard.vue'
  import CharacterForm from '../components/CharacterForm.vue'
  import ImportButton from '../components/ui/ImportButton.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useCharacterStore } from '../stores/characters.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useFileImport } from '../utils/useFileImport.js'
  import { applyFilters } from '../utils/filterUtils.js'

  export default {
    name: 'CharactersPage',
    components: {
      SplitViewLayout,
      EmptyState,
      CharacterCard,
      CharacterForm,
      ImportButton,
      FilterPanel,
    },
    setup() {
      const route = useRoute()

      // Initialize stores
      const characterStore = useCharacterStore()
      const gameDataStore = useGameDataStore()

      // Reactive refs from stores
      const {
        entities,
        loading,
        error,
        selectedEntityId,
        selectedEntity: selectedCharacter,
        showCreateForm,
      } = storeToRefs(characterStore)

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
      } = characterStore

      const { importing, handleImportFile: handleFileImport } = useFileImport('Character')

      // Character filter tabs configuration
      const characterFilterTabs = [
        { id: 'race', label: 'Race' },
        { id: 'alignment', label: 'Alignment' },
        { id: 'size', label: 'Size' },
        { id: 'gender', label: 'Gender' },
        { id: 'class', label: 'Class' },
      ]

      // Filter state management (tabbed filtering - search is handled by SplitViewLayout)
      const activeFilters = ref({
        race: [],
        alignment: [],
        size: [],
        gender: [],
        class: [],
      })

      // Computed filtered entities (only apply FilterBar filters, search is handled by SplitViewLayout)
      const filteredEntities = computed(() => {
        return applyFilters(entities.value, activeFilters.value)
      })

      const handleCreateSave = async (formData) => {
        try {
          await createEntity(formData)
        } catch (err) {
          // Error handling is done in character store
        }
      }

      const handleCancelCreate = () => {
        cancelCreate()
      }

      const handleImportFile = (event) => {
        handleFileImport(
          event,
          createEntity,
          (message) => {
            // Success message - could emit to parent or use toast
            console.log('Import success:', message)
          },
          (errorMessage) => {
            error.value = errorMessage
          }
        )
      }

      // Handle world changes
      const handleWorldChange = (event) => {
        clearEntities()
        loadEntities()
      }

      onMounted(async () => {
        await gameDataStore.load()
        await loadEntities()

        // Listen for world changes
        window.addEventListener('world-changed', handleWorldChange)

        // Auto-select character if ID is provided in query params
        const characterId = route.query.id
        if (characterId) {
          const id = parseInt(characterId, 10)
          if (entities.value.some((char) => char.id === id)) {
            selectEntity(id)
          }
        }
      })

      // Clean up event listener on unmount
      onUnmounted(() => {
        window.removeEventListener('world-changed', handleWorldChange)
      })

      // Watch for changes in entities to handle auto-selection after data loads
      watch(entities, (newEntities) => {
        const characterId = route.query.id
        if (characterId && newEntities.length > 0 && !selectedEntityId.value) {
          const id = parseInt(characterId, 10)
          if (newEntities.some((char) => char.id === id)) {
            selectEntity(id)
          }
        }
      })

      return {
        gameData,
        entities,
        filteredEntities,
        activeFilters,
        characterFilterTabs,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedCharacter,
        importing,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        handleCreateSave,
        handleCancelCreate,
        handleImportFile,
      }
    },
  }
</script>

<style scoped>
  .import-characters-btn {
    width: 100%;
    padding: 10px 16px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85em;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
    margin-top: 8px;
  }

  .import-characters-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #0056b3, #004085);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
  }

  .import-characters-btn:disabled {
    background: #6c757d;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }
</style>
