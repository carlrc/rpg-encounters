<template>
  <div class="world-tabs">
    <div
      v-for="(world, index) in worlds"
      :key="world.id"
      :class="['world-tab', { active: world.id === currentWorldId }]"
      @click="selectWorld(world.id)"
    >
      {{ index + 1 }}
      <span class="delete-btn" @click.stop="deleteWorld(world.id)" title="Delete world"> × </span>
    </div>
    <div class="add-world-tab" @click="createWorld" title="Create new world">+</div>
  </div>
</template>

<script>
  import { ref, onMounted } from 'vue'
  import { serializeError } from 'serialize-error'
  import { getWorlds, createWorld, deleteWorld } from '../services/api'
  import { useWorldStore } from '../stores/world'
  import { storeToRefs } from 'pinia'
  import { useNotification } from '../composables/useNotification'
  import { getWorldNumber, getWorldDisplayName } from '../utils/worldUtils'

  export default {
    name: 'WorldTabs',
    emits: ['world-changed', 'world-created', 'world-deleted'],
    setup(props, { emit }) {
      const worlds = ref([])
      const loading = ref(false)
      const { showError, showSuccess } = useNotification()

      const worldStore = useWorldStore()
      const { currentWorldId } = storeToRefs(worldStore)
      const { setCurrentWorldId } = worldStore

      const loadWorlds = async () => {
        try {
          loading.value = true
          worlds.value = await getWorlds()

          // If we have worlds and current world doesn't exist, switch to first available
          if (worlds.value.length > 0) {
            const currentExists = worlds.value.some((w) => w.id === currentWorldId.value)
            if (!currentExists) {
              setCurrentWorldId(worlds.value[0].id)
              emit('world-changed', worlds.value[0].id)
            }
          }
          // If no worlds exist, currentWorldId will remain as default but no data will load
        } catch (error) {
          console.error('Failed to load worlds:', JSON.stringify(serializeError(error)))
          showError('Failed to load worlds')
        } finally {
          loading.value = false
        }
      }

      const selectWorld = (worldId) => {
        if (worldId !== currentWorldId.value) {
          setCurrentWorldId(worldId)
          emit('world-changed', worldId)
          showSuccess(`Switched to ${getWorldDisplayName(worlds.value, worldId)}`)
        }
      }

      const handleCreateWorld = async () => {
        try {
          const newWorld = await createWorld()
          worlds.value.push(newWorld)
          setCurrentWorldId(newWorld.id)
          emit('world-created', newWorld)
          emit('world-changed', newWorld.id)
          showSuccess(`Created ${getWorldDisplayName(worlds.value, newWorld.id)}`)
        } catch (error) {
          console.error('Failed to create world:', JSON.stringify(serializeError(error)))
          showError('Failed to create world')
        }
      }

      const handleDeleteWorld = async (worldId) => {
        if (worlds.value.length <= 1) {
          showError('Cannot delete the last world')
          return
        }

        const worldDisplayName = getWorldDisplayName(worlds.value, worldId)

        // Show confirmation dialog
        if (
          !confirm(
            `Are you sure you want to delete ${worldDisplayName}? This action cannot be undone.`
          )
        ) {
          return
        }

        try {
          await deleteWorld(worldId)
          worlds.value = worlds.value.filter((w) => w.id !== worldId)

          // If we deleted the active world, switch to the first available
          if (worldId === currentWorldId.value && worlds.value.length > 0) {
            setCurrentWorldId(worlds.value[0].id)
            emit('world-changed', worlds.value[0].id)
          }

          emit('world-deleted', worldId)
          showSuccess(`Deleted ${worldDisplayName}`)
        } catch (error) {
          console.error('Failed to delete world:', JSON.stringify(serializeError(error)))
          showError(`Failed to delete world`)
        }
      }

      onMounted(() => {
        loadWorlds()
      })

      return {
        worlds,
        loading,
        currentWorldId,
        selectWorld,
        createWorld: handleCreateWorld,
        deleteWorld: handleDeleteWorld,
      }
    },
  }
</script>

<style scoped>
  /* All WorldTabs styles now use shared classes from index.css - no component-specific styles needed */
</style>
