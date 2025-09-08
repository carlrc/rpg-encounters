<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <form v-if="!emailSent" @submit.prevent="handleSubmit" class="login-form">
          <div class="form-group">
            <label for="email" class="form-label">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="form-input"
              placeholder="Enter your email"
              :disabled="loading"
            />
          </div>

          <button type="submit" class="submit-button" :disabled="loading || !email">
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
  import { requestMagicLink } from '@/services/api'

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
      console.error('Failed to send login link:', error)
      alert('Failed to send login link. Please try again.')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-light);
  }

  .login-container {
    width: 100%;
    max-width: 400px;
    padding: var(--spacing-xl);
  }

  .login-card {
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-light);
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .form-label {
    font-weight: var(--font-weight-bold);
    color: var(--text-label);
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
  }

  .form-input {
    padding: var(--spacing-md);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    font-size: var(--font-size-md);
    width: 100%;
    transition: border-color var(--transition-fast);
  }

  .form-input:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  .submit-button {
    padding: var(--spacing-md) var(--spacing-xl);
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--font-size-md);
    font-weight: var(--font-weight-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .submit-button:hover:not(:disabled) {
    background: var(--primary-hover);
    transform: translateY(-1px);
  }

  .submit-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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
