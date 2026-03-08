import { v4 as uuidv4, validate as uuidValidate } from 'uuid'

/**
 * Generate a new temporary ID using UUID v4
 * @returns {string} UUID v4 string
 */
export const generateTempId = () => uuidv4()

/**
 * Check if an ID is a temporary UUID using uuid.validate()
 * @param {string} id - The ID to validate
 * @returns {boolean} True if the ID is a valid UUID
 */
export const isTemporaryId = (id) => uuidValidate(id)
