/**
 * Utility functions for world management
 */

/**
 * Get the display number for a world (1-based index)
 * @param {Array} worlds - Array of world objects
 * @param {number} worldId - The world ID to find
 * @returns {number} The display number (1-based index)
 */
export function getWorldNumber(worlds, worldId) {
  const index = worlds.findIndex((w) => w.id === worldId)
  return index + 1
}

/**
 * Get world display name for user-friendly messages
 * @param {Array} worlds - Array of world objects
 * @param {number} worldId - The world ID to find
 * @returns {string} Display name like "World 1"
 */
export function getWorldDisplayName(worlds, worldId) {
  const number = getWorldNumber(worlds, worldId)
  return `World ${number}`
}
