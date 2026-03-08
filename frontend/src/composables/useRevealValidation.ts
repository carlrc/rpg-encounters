import { computed } from 'vue'
import { useGameData } from './useGameData'
import { getValidationLimit } from '../utils/validationHelpers'

export function useRevealValidation(form) {
  const { gameData } = useGameData()

  const isFormValid = computed(() => {
    const titleLimit = getValidationLimit('title', 'REVEAL', gameData.value)
    const contentLimit = getValidationLimit('level_1_content', 'REVEAL', gameData.value)

    const baseValid =
      form.title.trim() &&
      (!titleLimit || form.title.length <= titleLimit) &&
      form.character_ids.length > 0 &&
      form.level_1_content.trim() &&
      (!contentLimit || form.level_1_content.length <= contentLimit)

    const level2Valid =
      !form.enable_level_2 ||
      (form.level_2_content.trim() &&
        (!contentLimit || form.level_2_content.length <= contentLimit))

    const level3Valid =
      !form.enable_level_3 ||
      (form.level_3_content.trim() &&
        (!contentLimit || form.level_3_content.length <= contentLimit))

    // Threshold validation: ensure thresholds are in ascending order
    const thresholdValid = (() => {
      // Validate ascending order: standard ≤ privileged ≤ exclusive
      let valid = true

      if (form.enable_level_2) {
        valid = valid && form.standard_threshold <= form.privileged_threshold
      }

      if (form.enable_level_3) {
        valid = valid && form.standard_threshold <= form.exclusive_threshold
        if (form.enable_level_2) {
          valid = valid && form.privileged_threshold <= form.exclusive_threshold
        }
      }

      return valid
    })()

    return baseValid && level2Valid && level3Valid && thresholdValid
  })

  return {
    isFormValid,
  }
}
