/**
 * Shared avatar utility functions
 */
import { sanitizeDisplayName } from './nameUtils'

/**
 * Generate initials from a name
 * @param {string} name - The name to generate initials from
 * @returns {string} - The initials (max 2 characters)
 */
export const getInitials = (name) => {
  const safeName = sanitizeDisplayName(name)
  if (!safeName) return '?'

  const initials = safeName
    .split(' ')
    .map((word) => {
      const match = word.match(/[\p{L}\p{N}]/u)
      return match ? match[0] : ''
    })
    .filter(Boolean)
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return initials || '?'
}
