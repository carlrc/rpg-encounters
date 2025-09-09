import { defineStore } from 'pinia'
import { ref } from 'vue'
import { checkAuth } from '@/services/api'

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
