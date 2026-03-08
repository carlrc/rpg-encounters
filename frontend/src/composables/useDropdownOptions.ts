import { computed } from 'vue'
import { useGameData } from './useGameData'

/**
 * Centralized dropdown options composable
 * Eliminates duplication of gender arrays and provides consistent dropdown data
 */
export function useDropdownOptions() {
  const { gameData } = useGameData()

  // Gender options (previously duplicated across multiple components)
  const genders = ['male', 'female', 'nonbinary']

  // Game data from backend
  const races = computed(() => gameData.value?.races || [])
  const classes = computed(() => gameData.value?.classes || [])
  const alignments = computed(() => gameData.value?.alignments || [])

  // Size options for different entity types
  const characterSizes = computed(() => gameData.value?.sizes?.character || [])
  const playerSizes = computed(() => gameData.value?.sizes?.player || [])

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
    races: races.value,
    sizes: characterSizes.value,
    alignments: alignments.value,
    genders,
  }))

  const playerOptions = computed(() => ({
    races: races.value,
    classes: classes.value,
    sizes: playerSizes.value,
    alignments: alignments.value,
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
          races: races.value,
          classes: classes.value,
          sizes: characterSizes.value,
          alignments: alignments.value,
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
