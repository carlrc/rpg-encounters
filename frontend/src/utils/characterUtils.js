/**
 * Get the name of a character by ID
 * @param {number|string} characterId - The character ID
 * @param {Array} characters - Array of character objects
 * @returns {string} The character name or empty string if not found
 */
export function getCharacterName(characterId, characters) {
  const character = characters.find((c) => c.id === characterId)
  return character ? character.name : ''
}
