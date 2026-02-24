// src/composables/useNotification.js
// Wrapper around the notification store to maintain backward compatibility
import { useNotificationStore } from '@/stores/notifications'

export function useNotification() {
  const notificationStore = useNotificationStore()

  return {
    notifications: notificationStore.notifications,
    addNotification: notificationStore.addNotification,
    removeNotification: notificationStore.removeNotification,
    showError: notificationStore.showError,
    showSuccess: notificationStore.showSuccess,
    showWarning: notificationStore.showWarning,
    showInfo: notificationStore.showInfo,
  }
}
