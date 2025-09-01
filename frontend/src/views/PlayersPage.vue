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
    <template #footer-actions>
      <ImportButton entity-type="Player" :importing="importing" @import="handleImportFile" />
    </template>

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

<script>
  import { computed, onMounted, onUnmounted } from 'vue'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import PlayerCard from '../components/PlayerCard.vue'
  import PlayerForm from '../components/PlayerForm.vue'
  import ImportButton from '../components/ui/ImportButton.vue'
  import { usePlayerStore } from '../stores/players.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useFileImport } from '../utils/useFileImport.js'

  export default {
    name: 'PlayersPage',
    components: {
      SplitViewLayout,
      EmptyState,
      PlayerCard,
      PlayerForm,
      ImportButton,
    },
    setup() {
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

      const { importing, handleImportFile: handleFileImport } = useFileImport('Player')

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
      })

      // Clean up event listener on unmount
      onUnmounted(() => {
        window.removeEventListener('world-changed', handleWorldChange)
      })

      return {
        gameData,
        entities,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedPlayer,
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
  /* Page-specific styles only - shared styles handled globally */
  /* No additional styles needed - all components use shared styles */
</style>
