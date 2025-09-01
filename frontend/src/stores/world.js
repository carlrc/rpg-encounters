import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getCurrentWorldId, setCurrentWorldId as setWorldStateId } from '../services/worldState.js'

export const useWorldStore = defineStore('world', () => {
  const currentWorldId = ref(getCurrentWorldId())

  const setCurrentWorldId = (id) => {
    currentWorldId.value = id
    // Sync with worldState.js for HTTP client access
    setWorldStateId(id)
  }

  // Watch for external changes to worldState and sync
  watch(currentWorldId, (newId) => {
    setWorldStateId(newId)
  })

  return {
    currentWorldId,
    setCurrentWorldId,
  }
})
