/**
 * Utility function to get DC label with difficulty class name
 * @param {number} value - The DC value
 * @param {Object} difficultyClasses - The difficulty classes object from game data
 * @returns {string} - Formatted DC label
 */
export const getDCLabel = (value, difficultyClasses) => {
  if (!difficultyClasses) return `DC ${value}`

  const dcEntries = Object.entries(difficultyClasses)
  const entry = dcEntries.find(([key, dcValue]) => dcValue === value)
  return entry ? `${entry[0].replace(/_/g, ' ')} (${value})` : `DC ${value}`
}
