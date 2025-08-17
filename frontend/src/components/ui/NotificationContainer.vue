<template>
  <div class="notification-container">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification', `notification-${notification.type}`]"
        @click="removeNotification(notification.id)"
      >
        <div class="notification-content">
          <span class="notification-icon">{{ getIcon(notification.type) }}</span>
          <span class="notification-message">{{ notification.message }}</span>
        </div>
        <button
          class="notification-close"
          @click.stop="removeNotification(notification.id)"
          aria-label="Close notification"
        >
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
  import { useNotification } from '../../composables/useNotification'

  export default {
    name: 'NotificationContainer',
    setup() {
      const { notifications, removeNotification } = useNotification()

      const getIcon = (type) => {
        const icons = {
          success: '✓',
          error: '⚠',
          warning: '⚠',
          info: 'ℹ',
        }
        return icons[type] || 'ℹ'
      }

      return {
        notifications,
        removeNotification,
        getIcon,
      }
    },
  }
</script>

<style scoped>
  .notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    pointer-events: none;
  }

  .notification {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    box-shadow: var(--shadow-card);
    border-left: 4px solid;
    min-width: 300px;
    max-width: 400px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--spacing-md);
    cursor: pointer;
    pointer-events: auto;
    transition: all var(--transition-normal);
  }

  .notification:hover {
    transform: translateX(-4px);
    box-shadow: var(--shadow-card-hover);
  }

  .notification-success {
    border-left-color: var(--success-color);
    background: linear-gradient(135deg, #ffffff, #f8fff9);
  }

  .notification-error {
    border-left-color: var(--danger-color);
    background: linear-gradient(135deg, #ffffff, #fff8f8);
  }

  .notification-warning {
    border-left-color: #ffc107;
    background: linear-gradient(135deg, #ffffff, #fffdf5);
  }

  .notification-info {
    border-left-color: var(--primary-color);
    background: linear-gradient(135deg, #ffffff, #f8fbff);
  }

  .notification-content {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm);
    flex: 1;
  }

  .notification-icon {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    line-height: 1;
    margin-top: 2px;
  }

  .notification-success .notification-icon {
    color: var(--success-color);
  }

  .notification-error .notification-icon {
    color: var(--danger-color);
  }

  .notification-warning .notification-icon {
    color: #ffc107;
  }

  .notification-info .notification-icon {
    color: var(--primary-color);
  }

  .notification-message {
    color: var(--text-primary);
    font-size: var(--font-size-base);
    line-height: 1.4;
    word-wrap: break-word;
  }

  .notification-close {
    background: none;
    border: none;
    font-size: 1.5em;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .notification-close:hover {
    background: rgba(0, 0, 0, 0.1);
    color: var(--text-primary);
  }

  /* Transition animations */
  .notification-enter-active {
    transition: all 0.3s ease-out;
  }

  .notification-leave-active {
    transition: all 0.3s ease-in;
  }

  .notification-enter-from {
    opacity: 0;
    transform: translateX(100%);
  }

  .notification-leave-to {
    opacity: 0;
    transform: translateX(100%);
  }

  .notification-move {
    transition: transform 0.3s ease;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .notification-container {
      top: 10px;
      right: 10px;
      left: 10px;
    }

    .notification {
      min-width: auto;
      max-width: none;
    }
  }
</style>
