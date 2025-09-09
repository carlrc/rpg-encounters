<template>
  <div class="auth-callback-page">
    <div class="auth-container">
      <div class="shared-card">
        <div class="auth-status">
          <p>Authenticating...</p>
          <div class="spinner"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { onMounted, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { consumeMagicLink } from '@/services/api'
  import '@/components/shared.css'

  const route = useRoute()
  const router = useRouter()
  const authStore = useAuthStore()

  onMounted(async () => {
    const token = route.query.token

    if (!token) {
      router.push('/login')
      return
    }

    // Immediately clear the token from URL to prevent any duplicate requests
    router.replace({ path: '/auth', query: {} })

    try {
      // Run both the UI delay and API call concurrently
      const [_, response] = await Promise.all([
        // UI delay for spinner
        new Promise((resolve) => setTimeout(resolve, 2000)),
        // API call to consume the token
        consumeMagicLink(token),
      ])

      // Check if token was successfully consumed
      if (response.ok) {
        // Session is now set, update auth state
        authStore.setAuthenticated(true)
        // Ensure reactive updates are flushed before navigation
        await nextTick()
        // Navigate to players page within the SPA
        router.push('/players')
      } else {
        // Token was invalid or expired
        alert('Failed to authenticate.')
        router.push('/login')
      }
    } catch (error) {
      alert('Failed to authenticate.')
      router.push('/login')
    }
  })
</script>

<style scoped>
  .auth-callback-page {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

  .auth-container {
    width: 100%;
    max-width: 400px;
    padding: var(--spacing-xl);
  }

  .auth-status {
    text-align: center;
    color: var(--text-secondary);
  }

  .spinner {
    margin: var(--spacing-xl) auto 0;
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-light);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
