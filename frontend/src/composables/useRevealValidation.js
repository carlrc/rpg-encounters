import { computed } from 'vue'
import { useGameData } from './useGameData.js'

export function useRevealValidation(form) {
  const { gameData } = useGameData()

  const isFormValid = computed(() => {
    const baseValid =
      form.title.trim() &&
      form.character_ids.length > 0 &&
      form.level_1_content.trim() &&
      form.level_1_content.length <= 500

    const level2Valid =
      !form.enable_level_2 || (form.level_2_content.trim() && form.level_2_content.length <= 500)

    const level3Valid =
      !form.enable_level_3 || (form.level_3_content.trim() && form.level_3_content.length <= 500)

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
