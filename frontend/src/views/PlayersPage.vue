<template>
  <SplitViewLayout
    :items="entities"
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
        v-else-if="!selectedPlayer && !showCreateForm"
        icon="👤"
        title="No Player Selected"
        message="Select a player from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <PlayerForm :is-editing="false" @save="handleCreateSave" @cancel="handleCancelCreate" />
      </div>

      <PlayerCard
        v-else-if="selectedPlayer"
        :player="selectedPlayer"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script setup>
  import { onMounted } from 'vue'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import PlayerCard from '../components/PlayerCard.vue'
  import PlayerForm from '../components/PlayerForm.vue'
  import { usePlayerStore } from '../stores/players.js'
  import { useGameDataStore } from '../stores/gameData.js'

  // Initialize stores
  const playerStore = usePlayerStore()
  const gameDataStore = useGameDataStore()

  // Reactive refs from stores
  const {
    entities,
    loading,
    error,
    selectedEntityId,
    selectedEntity: selectedPlayer,
    showCreateForm,
  } = storeToRefs(playerStore)

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
  } = playerStore

  const handleCreateSave = async (formData) => {
    try {
      await createEntity(formData)
    } catch (err) {
      // Error handling is done in player store
    }
  }

  const handleCancelCreate = () => {
    cancelCreate()
  }

  onMounted(async () => {
    await gameDataStore.load()
    await loadEntities()
  })
</script>

<style scoped>
  /* Page-specific styles only - shared styles handled globally */
  /* No additional styles needed - all components use shared styles */
</style>
