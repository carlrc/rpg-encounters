import { computed } from 'vue'
import { FORM_FIELDS } from '../constants/validation.js'
import { useGameData } from '../composables/useGameData.js'
import { getValidationLimit, validateCharacterLimit } from './validationHelpers.js'

export function useFormValidation(formData, entityType = 'PLAYER') {
  const { gameData } = useGameData()
  const requiredFields = FORM_FIELDS[entityType].REQUIRED

  const isFormValid = computed(() => {
    // Check all required fields are filled
    const hasRequiredFields = requiredFields.every((field) => {
      const value = formData[field]

      // Special handling for abilities and skills objects
      if (field === 'abilities' || field === 'skills') {
        return value && typeof value === 'object' && Object.keys(value).length > 0
      }

      // Special handling for communication_style - only required if communication_style_type is 'Custom'
      if (field === 'communication_style' && entityType === 'CHARACTER') {
        if (formData.communication_style_type && formData.communication_style_type !== 'Custom') {
          return true // Not required for presets
        }
      }

      return value && value.toString().trim() !== ''
    })

    if (!hasRequiredFields) return false

    // Validate abilities and skills ranges for PLAYER
    if (entityType === 'PLAYER') {
      // Get modifier limits from game data, with fallback values
      const abilityMin = gameData.value?.modifier_limits?.ability_min
      const abilityMax = gameData.value?.modifier_limits?.ability_max
      const skillMin = gameData.value?.modifier_limits?.skill_min
      const skillMax = gameData.value?.modifier_limits?.skill_max

      // Validate abilities
      if (formData.abilities) {
        for (const [ability, abilityValue] of Object.entries(formData.abilities)) {
          if (
            typeof abilityValue !== 'number' ||
            abilityValue < abilityMin ||
            abilityValue > abilityMax
          ) {
            return false
          }
        }
      }

      // Validate skills
      if (formData.skills) {
        for (const [skill, skillValue] of Object.entries(formData.skills)) {
          if (typeof skillValue !== 'number' || skillValue < skillMin || skillValue > skillMax) {
            return false
          }
        }
      }
    }

    // Check character limits for text fields using shared helper
    for (const [fieldName, value] of Object.entries(formData)) {
      if (typeof value === 'string') {
        const limit = getValidationLimit(fieldName, entityType, gameData.value)
        if (limit && value.length > limit) {
          return false
        }
      }
    }

    return true
  })

  const getFieldErrors = (fieldName) => {
    const errors = []
    const value = formData[fieldName]

    // Special handling for abilities and skills validation
    if (fieldName === 'abilities' || fieldName === 'skills') {
      if (
        requiredFields.includes(fieldName) &&
        (!value || typeof value !== 'object' || Object.keys(value).length === 0)
      ) {
        errors.push('This field is required')
      }

      if (fieldName === 'abilities' && value && typeof value === 'object') {
        // Get modifier limits from game data, with fallback values
        const abilityMin = gameData.value?.modifier_limits?.ability_min
        const abilityMax = gameData.value?.modifier_limits?.ability_max

        for (const [ability, abilityValue] of Object.entries(value)) {
          if (
            typeof abilityValue !== 'number' ||
            abilityValue < abilityMin ||
            abilityValue > abilityMax
          ) {
            errors.push(`${ability} must be between ${abilityMin} and ${abilityMax}`)
          }
        }
      }

      if (fieldName === 'skills' && value && typeof value === 'object') {
        // Get modifier limits from game data, with fallback values
        const skillMin = gameData.value?.modifier_limits?.skill_min
        const skillMax = gameData.value?.modifier_limits?.skill_max

        for (const [skill, skillValue] of Object.entries(value)) {
          if (typeof skillValue !== 'number' || skillValue < skillMin || skillValue > skillMax) {
            errors.push(`${skill} must be between ${skillMin} and ${skillMax}`)
          }
        }
      }
    } else if (requiredFields.includes(fieldName) && (!value || value.toString().trim() === '')) {
      errors.push('This field is required')
    }

    // Character limit validation using shared helper
    const limitError = validateCharacterLimit(value, fieldName, entityType, gameData.value)
    if (limitError) {
      errors.push(limitError)
    }

    return errors
  }

  return {
    isFormValid,
    getFieldErrors,
  }
}
