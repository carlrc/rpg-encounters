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
        :available-tabs="MEMORY_FILTER_TABS"
        :characters="characters"
      />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading memories...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedEntity && !showCreateForm"
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
        v-else-if="selectedEntity"
        :memory="selectedEntity"
        :characters="characters"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import { ref } from 'vue'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import MemoryCard from '../components/MemoryCard.vue'
  import MemoryForm from '../components/MemoryForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useMemoryStore } from '../stores/memories'
  import { useCharacterStore } from '../stores/characters'
  import { applyCharacterFilters, applyCharacterAttributeFilters } from '../utils/filterUtils'
  import { useGameDataStore } from '../stores/gameData'
  import { useCrudSplitViewPage } from '../composables/ui/useCrudSplitViewPage'
  import { MEMORY_FILTER_TABS, createMemoryFilterState } from '../constants/uiFilters'

  const memoryStore = useMemoryStore()
  const characterStore = useCharacterStore()
  const gameDataStore = useGameDataStore()

  const { entities: characters } = storeToRefs(characterStore)

  const activeFilters = ref(createMemoryFilterState())

  const {
    filteredEntities,
    loading,
    error,
    selectedEntityId,
    selectedEntity,
    showCreateForm,
    selectEntity,
    startCreate,
    handleCreateSave,
    handleCancelCreate,
    updateEntity,
    deleteEntity,
  } = useCrudSplitViewPage({
    store: memoryStore,
    createErrorLabel: 'Memory',
    loadDeps: async () => {
      await gameDataStore.load()
      await characterStore.loadEntities()
    },
    applyEntityFilters: (entityList) => {
      const byCharacter = applyCharacterFilters(entityList, activeFilters.value)
      return applyCharacterAttributeFilters(byCharacter, activeFilters.value, characters.value)
    },
  })
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
