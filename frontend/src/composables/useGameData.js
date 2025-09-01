import { useGameDataStore } from '@/stores/gameData'

export function useGameData() {
  const gameDataStore = useGameDataStore()

  const loadGameData = async () => {
    try {
      const result = await gameDataStore.load()
      if (!result) {
        throw new Error('Failed to load game data')
      }
      return result
    } catch (err) {
      alert('Failed to load game data')
      throw err
    }
  }

  return {
    gameData: gameDataStore.data,
    loading: gameDataStore.isLoading,
    error: gameDataStore.error,
    loadGameData,
  }
}
