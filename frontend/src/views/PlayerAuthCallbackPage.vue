<template>
  <div class="login-consume-page">
    <div class="login-consume-container">
      <div class="login-consume-content">
        <h2>Player Login</h2>
        <div v-if="isProcessing" class="processing-state">
          <div class="loading-spinner"></div>
          <p>Authenticating...</p>
        </div>
        <div v-else-if="error" class="error-state">
          <p class="error-message">{{ error }}</p>
          <button @click="$router.push('/login')" class="shared-btn shared-btn-primary">
            Back to Login
          </button>
        </div>
        <div v-else class="success-state">
          <p>Successfully authenticated. Redirecting...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { serializeError } from 'serialize-error'
  import { consumePlayerLogin } from '../services/api.js'
  import { useWorldStore } from '../stores/world.js'

  export default {
    name: 'PlayerAuthCallbackPage',
    setup() {
      const route = useRoute()
      const router = useRouter()
      const worldStore = useWorldStore()
      const isProcessing = ref(true)
      const error = ref('')

      const handlePlayerLogin = async () => {
        const playerId = route.params.playerId
        const token = route.query.token

        if (!playerId || !token) {
          error.value = 'Invalid login link. Missing player ID or token.'
          isProcessing.value = false
          return
        }

        try {
          // Use the dedicated player login function
          const response = await consumePlayerLogin(playerId, token)

          if (response.ok) {
            // Parse the response to get world_id
            const data = await response.json()
            // Set world_id in the world store immediately so future API calls work
            worldStore.setCurrentWorldId(data.world_id)
            router.replace(`/players/${playerId}/encounter`)
          } else if (response.status === 401) {
            error.value = 'Invalid or expired login link.'
          } else if (response.status === 429) {
            error.value = 'Too many login attempts. Please try again later.'
          } else {
            error.value = 'Authentication failed. Please try again.'
          }
        } catch (err) {
          console.error('Player login error:', JSON.stringify(serializeError(err)))
          error.value = 'Login error. Try clearing your cookies and try again.'
        } finally {
          isProcessing.value = false
        }
      }

      onMounted(() => {
        handlePlayerLogin()
      })

      return {
        isProcessing,
        error,
      }
    },
  }
</script>

<style scoped>
  .login-consume-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
  }

  .login-consume-container {
    max-width: 400px;
    width: 100%;
    padding: var(--spacing-lg);
  }

  .login-consume-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xxl);
    text-align: center;
  }

  h2 {
    margin: 0 0 var(--spacing-xl) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xxl);
    font-weight: var(--font-weight-bold);
  }

  .processing-state,
  .error-state,
  .success-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-lg);
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-default);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .error-message {
    color: var(--danger-color);
    margin: 0;
    font-weight: var(--font-weight-medium);
  }

  p {
    margin: 0;
    color: var(--text-primary);
  }
</style>
