import { defineStore } from 'pinia'
import { ref } from 'vue'
import { serializeError } from 'serialize-error'
import { getConversationData } from '@/services/api'

export const useConversationDataStore = defineStore('conversationData', () => {
  // Cache conversation data by key: "encounterId-playerId-characterId"
  const cache = ref({})
  const isLoading = ref(false)
  const error = ref(null)

  // Generate cache key from encounter, player, and character IDs
  const getCacheKey = (encounterId, playerId, characterId) => {
    return `${encounterId}-${playerId}-${characterId}`
  }

  // Get conversation data from cache or fetch if not available
  const getData = async (encounterId, playerId, characterId) => {
    const cacheKey = getCacheKey(encounterId, playerId, characterId)

    // Return cached data if available
    if (cache.value[cacheKey]) {
      return cache.value[cacheKey]
    }

    // Fetch and cache if not available
    isLoading.value = true
    error.value = null

    try {
      const data = await getConversationData(encounterId, playerId, characterId)

      // Cache the data
      cache.value[cacheKey] = {
        influence: data.influence,
        reveals: data.reveals,
        rawReveals: data.raw_reveals || data.reveals,
      }

      return cache.value[cacheKey]
    } catch (err) {
      console.error('Conversation data error:', JSON.stringify(serializeError(err)))
      error.value = err
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Get cached data without fetching (returns null if not cached)
  const getCached = (encounterId, playerId, characterId) => {
    const cacheKey = getCacheKey(encounterId, playerId, characterId)
    return cache.value[cacheKey] || null
  }

  // Clear cache for a specific combination
  const clearData = (encounterId, playerId, characterId) => {
    const cacheKey = getCacheKey(encounterId, playerId, characterId)
    delete cache.value[cacheKey]
  }

  // Clear all cached data for a character (useful when character changes)
  const clearCharacterCache = (characterId) => {
    const keysToDelete = Object.keys(cache.value).filter((key) => key.endsWith(`-${characterId}`))
    keysToDelete.forEach((key) => delete cache.value[key])
  }

  // Clear all cache
  const clearCache = () => {
    cache.value = {}
    error.value = null
  }

  return {
    cache,
    isLoading,
    error,
    getData,
    getCached,
    clearData,
    clearCharacterCache,
    clearCache,
  }
})
