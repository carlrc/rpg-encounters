import { ref } from 'vue'
import { getInitials, handleAvatarUpload as utilHandleAvatarUpload } from '../utils/avatarUtils.js'

/**
 * Centralized avatar upload composable
 * Eliminates duplication of avatar handling logic across components
 */
export function useAvatarUpload(initialAvatar = null) {
  const avatar = ref(initialAvatar)
  const isUploading = ref(false)
  const uploadError = ref('')

  const handleAvatarUpload = (event) => {
    isUploading.value = true
    uploadError.value = ''

    utilHandleAvatarUpload(
      event,
      (result) => {
        avatar.value = result
        isUploading.value = false
      },
      (error) => {
        uploadError.value = error || 'Failed to upload avatar'
        isUploading.value = false
      }
    )
  }

  const removeAvatar = () => {
    avatar.value = null
    uploadError.value = ''
  }

  const resetAvatar = (newAvatar = null) => {
    avatar.value = newAvatar
    uploadError.value = ''
    isUploading.value = false
  }

  return {
    avatar,
    isUploading,
    uploadError,
    handleAvatarUpload,
    removeAvatar,
    resetAvatar,
    getInitials, // Re-export for convenience
  }
}
