<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">⚠️</div>
      <h3 class="error-title">Something went wrong</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button @click="retry" class="shared-btn shared-btn-primary">Try Again</button>
        <button @click="reportError" class="shared-btn shared-btn-secondary">Report Issue</button>
      </div>
      <details v-if="errorDetails" class="error-details">
        <summary>Technical Details</summary>
        <pre class="error-stack">{{ errorDetails }}</pre>
      </details>
    </div>
  </div>
  <slot v-else />
</template>

<script>
  import { ref, onErrorCaptured } from 'vue'
  import { useNotification } from '../../composables/useNotification'

  export default {
    name: 'ErrorBoundary',
    props: {
      fallbackMessage: {
        type: String,
        default: 'An unexpected error occurred. Please try refreshing the page.',
      },
      showDetails: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['error', 'retry'],
    setup(props, { emit }) {
      const hasError = ref(false)
      const errorMessage = ref('')
      const errorDetails = ref('')
      const { showError } = useNotification()

      onErrorCaptured((error, instance, info) => {
        hasError.value = true
        errorMessage.value = error.message || props.fallbackMessage

        if (props.showDetails) {
          errorDetails.value = `${error.stack}\n\nComponent: ${info}`
        }

        // Log error for debugging
        console.error('Error caught by boundary:', error, info)

        // Emit error event for parent components to handle
        emit('error', { error, instance, info })

        // Show notification
        showError('An error occurred. Please try again.')

        // Prevent error propagation
        return false
      })

      const retry = () => {
        hasError.value = false
        errorMessage.value = ''
        errorDetails.value = ''
        emit('retry')
      }

      const reportError = () => {
        // In a real app, this would send error details to a logging service
        const errorReport = {
          message: errorMessage.value,
          details: errorDetails.value,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        }

        console.log('Error report:', errorReport)
        showError('Error report logged. Please contact support if the issue persists.')
      }

      // Expose methods for programmatic error handling
      const triggerError = (error) => {
        hasError.value = true
        errorMessage.value = error.message || props.fallbackMessage
        if (props.showDetails && error.stack) {
          errorDetails.value = error.stack
        }
      }

      const clearError = () => {
        hasError.value = false
        errorMessage.value = ''
        errorDetails.value = ''
      }

      return {
        hasError,
        errorMessage,
        errorDetails,
        retry,
        reportError,
        triggerError,
        clearError,
      }
    },
  }
</script>

<style scoped>
  .error-boundary {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    padding: var(--spacing-xxl);
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-card);
  }

  .error-content {
    text-align: center;
    max-width: 500px;
    width: 100%;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-lg);
  }

  .error-title {
    color: var(--danger-color);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    margin: 0 0 var(--spacing-lg) 0;
  }

  .error-message {
    color: var(--text-secondary);
    font-size: var(--font-size-base);
    line-height: 1.5;
    margin: 0 0 var(--spacing-xl) 0;
  }

  .error-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    margin-bottom: var(--spacing-xl);
  }

  .error-details {
    text-align: left;
    margin-top: var(--spacing-lg);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
  }

  .error-details summary {
    padding: var(--spacing-md);
    cursor: pointer;
    font-weight: var(--font-weight-semibold);
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-default);
  }

  .error-details summary:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .error-stack {
    padding: var(--spacing-lg);
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: var(--font-size-sm);
    line-height: 1.4;
    color: var(--text-primary);
    background: var(--bg-white);
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .error-boundary {
      padding: var(--spacing-lg);
      min-height: 150px;
    }

    .error-actions {
      flex-direction: column;
      align-items: stretch;
    }

    .shared-btn {
      width: 100%;
    }

    .error-icon {
      font-size: 2rem;
    }

    .error-title {
      font-size: var(--font-size-lg);
    }
  }

  /* Animation for error appearance */
  .error-boundary {
    animation: errorSlideIn 0.3s ease-out;
  }

  @keyframes errorSlideIn {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .error-boundary {
      border: 2px solid var(--danger-color);
    }

    .error-title {
      color: var(--danger-darker);
    }

    .error-details {
      border: 2px solid var(--text-secondary);
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .error-boundary {
      animation: none;
    }
  }
</style>
