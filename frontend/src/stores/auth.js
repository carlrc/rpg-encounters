import { defineStore } from 'pinia'
import { ref } from 'vue'
import { checkAuth, getWorlds } from '@/services/api'

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
          const { useWorldStore } = await import('@/stores/world')
          const worldStore = useWorldStore()

          const worlds = await getWorlds()
          if (worlds && worlds.length > 0) {
            worldStore.setCurrentWorldId(worlds[0].id)
          } else {
            // No worlds configured - treat as auth failure
            setAuthenticated(false)
            const router = await import('@/router')
            router.default.push('/login')
            return
          }
        }
      } catch (error) {
        setAuthenticated(false)
      } finally {
        isInitialized.value = true
      }
    })()

    return initPromise
  }

  return {
    isAuthenticated,
    isInitialized,
    setAuthenticated,
    initializeAuth,
  }
})
