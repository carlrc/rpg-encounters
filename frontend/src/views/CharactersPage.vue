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
        :available-tabs="CHARACTER_FILTER_TABS"
      />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading characters...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedEntity && !showCreateForm"
        icon="👤"
        title="No Character Selected"
        message="Select a character from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <CharacterForm :is-editing="false" @save="handleCreateSave" @cancel="handleCancelCreate" />
      </div>

      <CharacterCard
        v-else-if="selectedEntity"
        :character="selectedEntity"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import { ref, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import CharacterCard from '../components/CharacterCard.vue'
  import CharacterForm from '../components/CharacterForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useCharacterStore } from '../stores/characters'
  import { useGameDataStore } from '../stores/gameData'
  import { applyFilters } from '../utils/filterUtils'
  import { useCrudSplitViewPage } from '../composables/ui/useCrudSplitViewPage'
  import { CHARACTER_FILTER_TABS, createCharacterFilterState } from '../constants/uiFilters'

  const route = useRoute()
  const characterStore = useCharacterStore()
  const gameDataStore = useGameDataStore()

  const activeFilters = ref(createCharacterFilterState())

  const parseRouteSelection = (entityList) => {
    const characterId = route.query.id
    if (!characterId) {
      return null
    }

    const id = parseInt(characterId, 10)
    if (entityList.some((char) => char.id === id)) {
      return id
    }

    return null
  }

  const {
    entities,
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
    trySelectFromRoute,
    updateEntity,
    deleteEntity,
  } = useCrudSplitViewPage({
    store: characterStore,
    createErrorLabel: 'Character',
    loadDeps: async () => {
      await gameDataStore.load()
    },
    parseRouteSelection,
    applyEntityFilters: (entityList) => applyFilters(entityList, activeFilters.value),
  })

  watch(entities, () => {
    if (!selectedEntityId.value) {
      trySelectFromRoute()
    }
  })
</script>

<style scoped>
  /* Page-specific styles only - shared styles handled globally */
  /* No additional styles needed - ImportButton component handles its own styling */
</style>
