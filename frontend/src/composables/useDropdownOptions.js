import { computed } from 'vue'
import { RACES, CLASSES, SIZES, ALIGNMENTS } from '../constants/gameData.js'

/**
 * Centralized dropdown options composable
 * Eliminates duplication of gender arrays and provides consistent dropdown data
 */
export function useDropdownOptions() {
  // Gender options (previously duplicated across multiple components)
  const genders = ['male', 'female', 'nonbinary']

  // Game data from constants
  const races = RACES
  const classes = CLASSES
  const alignments = ALIGNMENTS

  // Size options for different entity types
  const characterSizes = SIZES.CHARACTER
  const playerSizes = SIZES.PLAYER

  // Gender emoji mapping for display
  const genderEmojis = {
    male: '♂️',
    female: '♀️',
    nonbinary: '⚧️',
  }

  // Helper function to get gender emoji
  const getGenderEmoji = (gender) => {
    return genderEmojis[gender] || ''
  }

  // Computed options for different entity types
  const characterOptions = computed(() => ({
    races,
    sizes: characterSizes,
    alignments,
    genders,
  }))

  const playerOptions = computed(() => ({
    races,
    classes,
    sizes: playerSizes,
    alignments,
    genders,
  }))

  // Helper function to get options by entity type
  const getOptionsForEntity = (entityType) => {
    switch (entityType.toLowerCase()) {
      case 'character':
        return characterOptions.value
      case 'player':
        return playerOptions.value
      default:
        return {
          races,
          classes,
          sizes: characterSizes,
          alignments,
          genders,
        }
    }
  }

  return {
    // Individual option arrays
    genders,
    races,
    classes,
    alignments,
    characterSizes,
    playerSizes,

    // Helper functions
    getGenderEmoji,
    getOptionsForEntity,

    // Computed option sets
    characterOptions,
    playerOptions,
  }
}
