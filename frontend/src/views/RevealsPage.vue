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
        :available-tabs="REVEAL_FILTER_TABS"
        :characters="characters"
      />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading reveals...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedEntity && !showCreateForm"
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
        v-else-if="selectedEntity"
        :reveal="selectedEntity"
        :characters="characters"
        :current-influence-level="18"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import { ref, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import RevealCard from '../components/RevealCard.vue'
  import RevealForm from '../components/RevealForm.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useRevealStore } from '../stores/reveals'
  import { useGameDataStore } from '../stores/gameData'
  import { useCharacterStore } from '../stores/characters'
  import { applyCharacterFilters, applyCharacterAttributeFilters } from '../utils/filterUtils'
  import { useCrudSplitViewPage } from '../composables/ui/useCrudSplitViewPage'
  import { REVEAL_FILTER_TABS, createRevealFilterState } from '../constants/uiFilters'

  const route = useRoute()

  const revealStore = useRevealStore()
  const gameDataStore = useGameDataStore()
  const characterStore = useCharacterStore()

  const { entities: characters } = storeToRefs(characterStore)

  const activeFilters = ref(createRevealFilterState())

  const parseRouteSelection = (entityList) => {
    const revealId = route.query.id
    if (!revealId) {
      return null
    }

    const id = parseInt(revealId, 10)
    if (!Number.isNaN(id) && entityList.some((reveal) => reveal.id === id)) {
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
    store: revealStore,
    createErrorLabel: 'Reveal',
    loadDeps: async () => {
      await gameDataStore.load()
      await characterStore.loadEntities()
    },
    parseRouteSelection,
    applyEntityFilters: (entityList) => {
      const byCharacter = applyCharacterFilters(entityList, activeFilters.value)
      return applyCharacterAttributeFilters(byCharacter, activeFilters.value, characters.value)
    },
  })

  watch(entities, () => {
    if (!selectedEntityId.value) {
      trySelectFromRoute()
    }
  })
</script>

<style scoped>
  /* Page-specific styles only - form styles are handled by RevealForm.vue */
</style>
