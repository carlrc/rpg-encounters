import { ref, readonly } from 'vue'
import { getGameData } from '../services/gameDataService.js'

const gameData = ref(null)
const loading = ref(false)
const error = ref(null)

export function useGameData() {
  const loadGameData = async () => {
    if (gameData.value) {
      return gameData.value
    }

    loading.value = true
    error.value = null

    try {
      gameData.value = await getGameData()
      if (!gameData.value) {
        throw new Error('Failed to load game data')
      }
      return gameData.value
    } catch (err) {
      error.value = err
      alert('Failed to load game data')
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    gameData: readonly(gameData),
    loading: readonly(loading),
    error: readonly(error),
    loadGameData,
  }
}
