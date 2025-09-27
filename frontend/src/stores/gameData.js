import { defineStore } from 'pinia'
import { ref } from 'vue'
import { serializeError } from 'serialize-error'
import { getGameData } from '../services/api'
import { useNotification } from '../composables/useNotification.js'

export const useGameDataStore = defineStore('gameData', () => {
  const data = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const { showError } = useNotification()

  const load = async () => {
    if (data.value) return data.value

    isLoading.value = true
    error.value = null

    try {
      data.value = await getGameData()
      return data.value
    } catch (err) {
      console.error('Game data store error:', JSON.stringify(serializeError(err)))
      error.value = err
      showError('Failed to load game data. Please refresh the page and try again.')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearCache = () => {
    data.value = null
    error.value = null
  }

  const reload = async () => {
    clearCache()
    return await load()
  }

  return {
    data,
    isLoading,
    error,
    load,
    clearCache,
    reload,
  }
})
