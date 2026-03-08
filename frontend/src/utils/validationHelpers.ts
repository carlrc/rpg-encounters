/**
 * Shared validation utilities
 * Centralizes field mapping and validation logic
 */

/**
 * Get validation limit key for a field based on entity type
 * @param {string} fieldName - The field name to validate
 * @param {string} entityType - The entity type (PLAYER, CHARACTER, MEMORY, REVEAL)
 * @returns {string|null} - The validation limit key or null if not found
 */
export function getValidationLimitKey(fieldName, entityType) {
  const fieldMap = {
    // Common fields
    name: 'name',

    // Player fields
    appearance: 'player_appearance',

    // Character fields
    profession: 'character_profession',
    background: 'character_background',
    communication_style: 'character_communication',
    motivation: 'character_motivation',

    // Memory fields
    title: entityType === 'MEMORY' ? 'memory_title' : 'reveal_title',
    content: 'memory_content',

    // Reveal fields
    level_1_content: 'reveal_content',
    level_2_content: 'reveal_content',
    level_3_content: 'reveal_content',
  }

  return fieldMap[fieldName] || null
}

/**
 * Get validation limit for a field
 * @param {string} fieldName - The field name to validate
 * @param {string} entityType - The entity type
 * @param {Object} gameData - The game data object containing validation_limits
 * @returns {number|null} - The character limit or null if not found
 */
export function getValidationLimit(fieldName, entityType, gameData) {
  if (!gameData?.validation_limits) return null

  const limitKey = getValidationLimitKey(fieldName, entityType)
  return limitKey ? gameData.validation_limits[limitKey] : null
}

/**
 * Validate character limit for a field
 * @param {string} value - The value to validate
 * @param {string} fieldName - The field name
 * @param {string} entityType - The entity type
 * @param {Object} gameData - The game data object
 * @returns {string|null} - Error message or null if valid
 */
export function validateCharacterLimit(value, fieldName, entityType, gameData) {
  if (!value || typeof value !== 'string') return null

  const limit = getValidationLimit(fieldName, entityType, gameData)
  if (!limit) return null

  if (value.length > limit) {
    const fieldLabel = fieldName.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
    return `${fieldLabel} must be ${limit} characters or less (currently ${value.length} characters)`
  }

  return null
}
