import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getGameData } from '../services/gameDataService'

export const useGameDataStore = defineStore('gameData', () => {
  const data = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const load = async () => {
    if (data.value) return data.value

    isLoading.value = true
    error.value = null

    try {
      data.value = await getGameData()
      return data.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { data, isLoading, error, load }
})
