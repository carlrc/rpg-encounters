/**
 * Shared avatar utility functions
 */

/**
 * Generate initials from a name
 * @param {string} name - The name to generate initials from
 * @returns {string} - The initials (max 2 characters)
 */
export const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Handle avatar file upload
 * @param {Event} event - The file input change event
 * @param {Function} callback - Callback function to handle the result
 */
export const handleAvatarUpload = (event, callback) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      callback(e.target.result)
    }
    reader.readAsDataURL(file)
  }
}
