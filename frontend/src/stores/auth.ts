import { defineStore } from 'pinia'
import { ref } from 'vue'
import { serializeError } from 'serialize-error'
import { checkAuth, getWorlds } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const isInitialized = ref(false)
  let initPromise = null

  const setAuthenticated = (value) => {
    isAuthenticated.value = value
  }

  const initializeAuth = async () => {
    if (isInitialized.value) return
    if (initPromise) return initPromise

    initPromise = (async () => {
      try {
        const authenticated = await checkAuth()
        setAuthenticated(authenticated)

        // If authenticated, load worlds and set current world ID
        if (authenticated) {
          const { useWorldStore } = await import('../stores/world')
          const worldStore = useWorldStore()

          const worlds = await getWorlds()
          if (worlds && worlds.length > 0) {
            worldStore.setCurrentWorldId(worlds[0].id)
          } else {
            // No worlds configured - treat as auth failure
            setAuthenticated(false)
            return
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', JSON.stringify(serializeError(error)))
        setAuthenticated(false)
      } finally {
        isInitialized.value = true
      }
    })()

    return initPromise
  }

  const logout = async () => {
    const { useWorldStore } = await import('../stores/world')
    const { useCharacterStore } = await import('../stores/characters')
    const { usePlayerStore } = await import('../stores/players')
    const { useMemoryStore } = await import('../stores/memories')
    const { useRevealStore } = await import('../stores/reveals')
    const { useEncounterStore } = await import('../stores/encounters')

    const worldStore = useWorldStore()
    const characterStore = useCharacterStore()
    const playerStore = usePlayerStore()
    const memoryStore = useMemoryStore()
    const revealStore = useRevealStore()
    const encounterStore = useEncounterStore()

    // Clear stores
    characterStore.clearEntities()
    playerStore.clearEntities()
    memoryStore.clearEntities()
    revealStore.clearEntities()
    encounterStore.clearEntities()

    // Clear authentication state
    setAuthenticated(false)
    worldStore.setCurrentWorldId(null)
    isInitialized.value = false
    initPromise = null
  }

  return {
    isAuthenticated,
    isInitialized,
    setAuthenticated,
    initializeAuth,
    logout,
  }
})
