import { getGameData as fetchGameData } from './api.js'

let gameDataCache = null

export const getGameData = async () => {
  // Return cached data if available
  if (gameDataCache) {
    return gameDataCache
  }

  try {
    // Fetch from API and cache
    gameDataCache = await fetchGameData()
    return gameDataCache
  } catch (error) {
    console.error('Failed to load game data:', error)
    throw error
  }
}

export const clearGameDataCache = () => {
  gameDataCache = null
}
