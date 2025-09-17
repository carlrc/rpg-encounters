<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Memories"
    create-button-text="Add Memory"
    empty-message="No memories yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="memoryFilterTabs"
        :characters="characters"
      />
    </template>
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading memories...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedMemory && !showCreateForm"
        icon="🧠"
        title="No Memory Selected"
        message="Select a memory from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <MemoryForm
          :characters="characters"
          :is-editing="false"
          @save="handleCreateSave"
          @cancel="handleCancelCreate"
        />
      </div>

      <MemoryCard
        v-else-if="selectedMemory"
        :memory="selectedMemory"
        :characters="characters"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import MemoryCard from '../components/MemoryCard.vue'
  import MemoryForm from '../components/MemoryForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useMemoryStore } from '../stores/memories.js'
  import { useWorldStore } from '@/stores/world'
  import { applyCharacterFilters, applyCharacterAttributeFilters } from '../utils/filterUtils.js'
  import { getCharacters } from '../services/api.js'
  import { useGameDataStore } from '../stores/gameData.js'

  // Initialize stores
  const memoryStore = useMemoryStore()
  const gameDataStore = useGameDataStore()
  const worldStore = useWorldStore()

  // Reactive refs from stores
  const {
    entities,
    loading,
    error,
    selectedEntityId,
    selectedEntity: selectedMemory,
    showCreateForm,
  } = storeToRefs(memoryStore)

  // Actions
  const {
    loadEntities,
    createEntity,
    updateEntity,
    deleteEntity,
    selectEntity,
    startCreate,
    cancelCreate,
  } = memoryStore

  const characters = ref([])

  // Memory filter tabs configuration
  const memoryFilterTabs = [
    { id: 'characters', label: 'Characters' },
    { id: 'race', label: 'Race' },
    { id: 'alignment', label: 'Alignment' },
  ]

  // Character filtering state
  const activeFilters = ref({
    characterIds: [],
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
      // Error handling is done in memory store
    }
  }

  const handleCancelCreate = () => {
    cancelCreate()
  }

  // Watch for world changes to reload characters
  watch(
    () => worldStore.currentWorldId,
    () => {
      characters.value = []
      loadCharacters()
    }
  )

  onMounted(async () => {
    await loadEntities()
    await gameDataStore.load()
    await loadCharacters()
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
</script>

<style scoped>
  /* Page-specific styles only - shared styles handled globally */
  .content-field {
    margin-bottom: var(--spacing-xxl);
  }

  .required {
    color: var(--danger-color);
    font-weight: var(--font-weight-bold);
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
