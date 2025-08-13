import apiService from './api.js'

let gameDataCache = null

export async function getGameData() {
  // Return cached data if available
  if (gameDataCache) {
    return gameDataCache
  }

  try {
    // Fetch from API and cache
    gameDataCache = await apiService.request('/game')
    return gameDataCache
  } catch (error) {
    console.error('Failed to load game data:', error)
    throw error
  }
}

export function clearGameDataCache() {
  gameDataCache = null
}
