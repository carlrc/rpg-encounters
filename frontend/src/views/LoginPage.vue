<template>
  <div class="login-page">
    <SharedEncounterPopup
      :is-open="showSignupClosedPopup"
      title="Registration Closed"
      close-aria-label="Close signups closed popup"
      popup-width="90%"
      popup-max-width="460px"
      popup-max-height="80vh"
      @close="closeSignupClosedPopup"
    >
      <div class="shared-popup-body">
        <p class="shared-popup-message">
          Registration is not open right now. If you already have an account, request a login link
          below.
        </p>
        <button
          type="button"
          class="shared-btn shared-btn-primary shared-popup-action"
          @click="closeSignupClosedPopup"
        >
          Close
        </button>
      </div>
    </SharedEncounterPopup>
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
          <p>If an account exists for that email, we'll send a login link shortly.</p>
          <p>Please check your email.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { serializeError } from 'serialize-error'
  import { requestMagicLink } from '../services/api'
  import SharedEncounterPopup from '../components/base/SharedEncounterPopup.vue'
  import '@/components/shared.css'

  const email = ref('')
  const loading = ref(false)
  const emailSent = ref(false)
  const showSignupClosedPopup = ref(true)

  const closeSignupClosedPopup = () => {
    showSignupClosedPopup.value = false
  }

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
