<template>
  <DeviceWarningPopup :is-open="showDeviceWarning" @close="dismissDeviceWarning" />
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
  import { onMounted, ref } from 'vue'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import DeviceWarningPopup from '../components/ui/DeviceWarningPopup.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import PlayerCard from '../components/PlayerCard.vue'
  import PlayerForm from '../components/PlayerForm.vue'
  import { usePlayerStore } from '../stores/players'
  import { useGameDataStore } from '../stores/gameData'
  import { useCrudSplitViewPage } from '../composables/ui/useCrudSplitViewPage'
  import { shouldShowDeviceWarning } from '../utils/deviceWarning'

  const playerStore = usePlayerStore()
  const gameDataStore = useGameDataStore()
  const showDeviceWarning = ref(false)
  const DEVICE_WARNING_KEY = 'device-warning-shown'

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

  onMounted(() => {
    if (typeof window === 'undefined') return
    try {
      const alreadyShown = sessionStorage.getItem(DEVICE_WARNING_KEY) === 'true'
      if (!shouldShowDeviceWarning(window.innerWidth, alreadyShown)) return
      sessionStorage.setItem(DEVICE_WARNING_KEY, 'true')
    } catch (error) {
      console.warn('Unable to persist device warning state.', error)
    }
    showDeviceWarning.value = true
  })

  const dismissDeviceWarning = () => {
    showDeviceWarning.value = false
  }
</script>

<style scoped>
  /* Page-specific styles only - shared styles handled globally */
  /* No additional styles needed - all components use shared styles */
</style>
