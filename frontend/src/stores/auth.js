import { defineStore } from 'pinia'
import { ref } from 'vue'
import { checkAuth } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const isInitialized = ref(false)

  const setAuthenticated = (value) => {
    isAuthenticated.value = value
  }

  const initializeAuth = async () => {
    if (isInitialized.value) return

    try {
      const authenticated = await checkAuth()
      setAuthenticated(authenticated)
    } catch (error) {
      setAuthenticated(false)
    }
  }

  return {
    isAuthenticated,
    isInitialized,
    setAuthenticated,
    initializeAuth,
  }
})
