<template>
  <div class="login-page">
    <div class="login-container">
      <div class="shared-card">
        <form v-if="!emailSent" @submit.prevent="handleSubmit" class="shared-form">
          <div class="form-group">
            <label for="email" class="shared-field-label">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="shared-input"
              placeholder="Enter your email"
              :disabled="loading"
            />
          </div>

          <button type="submit" class="shared-btn shared-btn-primary" :disabled="loading || !email">
            {{ loading ? 'Sending...' : 'Request Login Link' }}
          </button>
        </form>

        <div v-else class="success-message">
          <p>✓ Login link sent!</p>
          <p>Please check your email and click the link to log in.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { serializeError } from 'serialize-error'
  import { requestMagicLink } from '@/services/api'
  import '@/components/shared.css'

  const email = ref('')
  const loading = ref(false)
  const emailSent = ref(false)

  const handleSubmit = async () => {
    if (!email.value || loading.value) return

    loading.value = true
    try {
      await requestMagicLink(email.value)
      emailSent.value = true
    } catch (error) {
      console.error('Failed to send login link:', JSON.stringify(serializeError(error)))
      alert('Failed to send login link. Please try again.')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .login-page {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

  .login-container {
    width: 100%;
    max-width: 400px;
    padding: var(--spacing-xl);
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .success-message {
    text-align: center;
    color: var(--text-secondary);
  }

  .success-message p:first-child {
    color: var(--success-color);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--spacing-md);
  }
</style>
