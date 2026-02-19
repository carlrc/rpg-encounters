<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    list-title="Players"
    create-button-text="Add Player"
    empty-message="No players yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading players...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedEntity && !showCreateForm"
        icon="👤"
        title="No Player Selected"
        message="Select a player from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <PlayerForm :is-editing="false" @save="handleCreateSave" @cancel="handleCancelCreate" />
      </div>

      <PlayerCard
        v-else-if="selectedEntity"
        :player="selectedEntity"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import PlayerCard from '../components/PlayerCard.vue'
  import PlayerForm from '../components/PlayerForm.vue'
  import { usePlayerStore } from '../stores/players.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useCrudSplitViewPage } from '../composables/ui/useCrudSplitViewPage.js'

  const playerStore = usePlayerStore()
  const gameDataStore = useGameDataStore()

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
    store: playerStore,
    createErrorLabel: 'Player',
    loadDeps: async () => {
      await gameDataStore.load()
    },
  })
</script>

<style scoped>
  /* Page-specific styles only - shared styles handled globally */
  /* No additional styles needed - all components use shared styles */
</style>
