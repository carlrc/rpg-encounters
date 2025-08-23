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
  import apiService from '../services/api.js'
  import { getCurrentWorldIdRef, setCurrentWorldId } from '../services/worldState.js'
  import { useNotification } from '../composables/useNotification.js'
  import { getWorldNumber, getWorldDisplayName } from '../utils/worldUtils.js'

  export default {
    name: 'WorldTabs',
    emits: ['world-changed', 'world-created', 'world-deleted'],
    setup(props, { emit }) {
      const worlds = ref([])
      const loading = ref(false)
      const { showError, showSuccess } = useNotification()

      const currentWorldId = getCurrentWorldIdRef()

      const loadWorlds = async () => {
        try {
          loading.value = true
          worlds.value = await apiService.getWorlds()

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
          console.error('Failed to load worlds:', error)
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

      const createWorld = async () => {
        try {
          const newWorld = await apiService.createWorld()
          worlds.value.push(newWorld)
          setCurrentWorldId(newWorld.id)
          emit('world-created', newWorld)
          emit('world-changed', newWorld.id)
          showSuccess(`Created ${getWorldDisplayName(worlds.value, newWorld.id)}`)
        } catch (error) {
          console.error('Failed to create world:', error)
          showError('Failed to create new world. Please try again.')
        }
      }

      const deleteWorld = async (worldId) => {
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
          await apiService.deleteWorld(worldId)
          worlds.value = worlds.value.filter((w) => w.id !== worldId)

          // If we deleted the active world, switch to the first available
          if (worldId === currentWorldId.value && worlds.value.length > 0) {
            setCurrentWorldId(worlds.value[0].id)
            emit('world-changed', worlds.value[0].id)
          }

          emit('world-deleted', worldId)
          showSuccess(`Deleted ${worldDisplayName}`)
        } catch (error) {
          console.error('Failed to delete world:', error)
          showError(`Failed to delete ${worldDisplayName}. Please try again.`)
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
        createWorld,
        deleteWorld,
      }
    },
  }
</script>

<style scoped>
  .world-tabs {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 0;
    background: transparent;
    width: 60px;
  }

  .world-tab {
    padding: 10px 8px;
    background: white;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    cursor: pointer;
    position: relative;
    width: 60px;
    height: 60px;
    text-align: center;
    font-weight: 600;
    color: #495057;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    font-size: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    flex-direction: column;
  }

  .world-tab.active {
    background: linear-gradient(135deg, #007bff, #0056b3) !important;
    color: white !important;
    border-color: #007bff !important;
    font-weight: 700;
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
    transform: translateX(2px);
  }

  .world-tab:hover:not(.active) {
    background: #e3f2fd;
    border-color: #bbdefb;
    color: #1976d2;
    transform: translateX(1px);
  }

  .add-world-tab {
    padding: 10px 8px;
    background: white;
    border: 2px dashed #6c757d;
    border-radius: 8px;
    cursor: pointer;
    color: #6c757d;
    font-weight: bold;
    font-size: 24px;
    transition: all 0.2s ease;
    width: 60px;
    height: 60px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .add-world-tab:hover {
    background: #f8f9fa;
    border-color: #495057;
    color: #495057;
    transform: translateX(1px);
  }

  .delete-btn {
    position: absolute;
    top: -4px;
    right: -4px;
    color: #dc3545;
    background: white;
    font-weight: bold;
    font-size: 12px;
    line-height: 1;
    padding: 2px 4px;
    border-radius: 50%;
    transition: all 0.2s ease;
    border: 1px solid #dc3545;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .delete-btn:hover {
    background: #dc3545;
    color: white;
    transform: scale(1.1);
  }

  .world-tab.active .delete-btn {
    border-color: rgba(255, 255, 255, 0.8);
    color: #dc3545;
    background: rgba(255, 255, 255, 0.9);
  }

  .world-tab.active .delete-btn:hover {
    background: #dc3545;
    color: white;
  }
</style>
