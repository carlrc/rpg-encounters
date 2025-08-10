import { computed } from 'vue'
import { THRESHOLD_LIMITS } from '../constants/gameData.js'

export function useRevealValidation(form) {
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

    // Threshold validation: only validate gap when both levels use custom thresholds
    const thresholdValid = (() => {
      const privilegedMode = form.privileged_threshold_mode || 'default'
      const exclusiveMode = form.exclusive_threshold_mode || 'default'

      // If both levels are enabled and both use custom thresholds, validate the gap
      if (
        form.enable_level_2 &&
        form.enable_level_3 &&
        privilegedMode === 'custom' &&
        exclusiveMode === 'custom'
      ) {
        return (
          form.privileged_threshold < form.exclusive_threshold &&
          form.exclusive_threshold - form.privileged_threshold >= THRESHOLD_LIMITS.minGap
        )
      }

      // Otherwise, thresholds are valid (using defaults or only one level enabled)
      return true
    })()

    return baseValid && level2Valid && level3Valid && thresholdValid
  })

  return {
    isFormValid,
  }
}
