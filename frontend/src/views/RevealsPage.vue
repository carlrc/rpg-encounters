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

<script setup>
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { serializeError } from 'serialize-error'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import RevealCard from '../components/RevealCard.vue'
  import RevealForm from '../components/RevealForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useRevealStore } from '../stores/reveals.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useWorldStore } from '@/stores/world'
  import { applyCharacterFilters, applyCharacterAttributeFilters } from '../utils/filterUtils.js'
  import { getCharacters } from '../services/api.js'

  const route = useRoute()

  // Initialize stores
  const revealStore = useRevealStore()
  const gameDataStore = useGameDataStore()
  const worldStore = useWorldStore()

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
      console.error('Error loading characters:', JSON.stringify(serializeError(err)))
    }
  }

  const handleCreateSave = async (formData) => {
    try {
      await createEntity(formData)
    } catch (err) {
      console.error('Reveal entity creation error:', JSON.stringify(serializeError(err)))
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
    await gameDataStore.load()
    await loadEntities()
    await loadCharacters()

    // Auto-select reveal if ID is provided in query params
    const revealId = route.query.id
    if (revealId) {
      const id = parseInt(revealId)
      if (!isNaN(id) && entities.value.length > 0) {
        selectEntity(id)
      }
    }
  })

  // Watch for changes in entities to handle auto-selection after data loads
  watch(entities, (newEntities) => {
    const revealId = route.query.id
    if (revealId && newEntities.length > 0 && !selectedEntityId.value) {
      const id = parseInt(revealId)
      if (!isNaN(id) && newEntities.some((reveal) => reveal.id === id)) {
        selectEntity(id)
      }
    }
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
  /* Page-specific styles only - form styles are handled by RevealForm.vue */
</style>
