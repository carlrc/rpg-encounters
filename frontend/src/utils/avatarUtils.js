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
