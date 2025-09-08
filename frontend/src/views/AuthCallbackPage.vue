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
  import { onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import '@/components/shared.css'

  const route = useRoute()
  const router = useRouter()

  onMounted(() => {
    const token = route.query.token

    if (!token) {
      router.push('/login')
      return
    }

    // Add 2 second delay to show the spinner
    setTimeout(() => {
      // Direct browser navigation - let the browser handle the 302 redirect
      window.location.href = `${import.meta.env.VITE_BACKEND_URL}/auth?token=${encodeURIComponent(token)}`
    }, 2000)
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
