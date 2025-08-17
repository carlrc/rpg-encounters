// src/composables/useNotification.js
import { ref } from 'vue'

const notifications = ref([])
let notificationId = 0

export function useNotification() {
  const addNotification = (message, type = 'info', duration = 3000) => {
    const id = ++notificationId
    const notification = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      timestamp: Date.now(),
    }

    notifications.value.push(notification)

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  const removeNotification = (id) => {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const showError = (message) => addNotification(message, 'error', 5000)
  const showSuccess = (message) => addNotification(message, 'success', 3000)
  const showWarning = (message) => addNotification(message, 'warning', 4000)
  const showInfo = (message) => addNotification(message, 'info', 3000)

  return {
    notifications,
    addNotification,
    removeNotification,
    showError,
    showSuccess,
    showWarning,
    showInfo,
  }
}
