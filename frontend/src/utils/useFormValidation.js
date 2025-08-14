import { computed } from 'vue'
import { FORM_FIELDS } from '../constants/validation.js'
import { useGameData } from '../composables/useGameData.js'

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

      return value && value.toString().trim() !== ''
    })

    if (!hasRequiredFields) return false

    // Validate abilities and skills ranges for PLAYER
    if (entityType === 'PLAYER') {
      // Validate abilities (0-30 range)
      if (formData.abilities) {
        for (const [ability, abilityValue] of Object.entries(formData.abilities)) {
          if (typeof abilityValue !== 'number' || abilityValue < 0 || abilityValue > 30) {
            return false
          }
        }
      }

      // Validate skills (-5 to 25 range)
      if (formData.skills) {
        for (const [skill, skillValue] of Object.entries(formData.skills)) {
          if (typeof skillValue !== 'number' || skillValue < -5 || skillValue > 25) {
            return false
          }
        }
      }
    }

    // Check word limits based on entity type
    if (entityType === 'PLAYER' && gameData.value) {
      const appearanceWords = formData.appearance?.trim()
        ? formData.appearance.trim().split(/\s+/).length
        : 0
      if (appearanceWords > gameData.value.validation_limits.player_appearance) return false
    }

    if (entityType === 'CHARACTER' && gameData.value) {
      const backgroundWords = formData.background?.trim()
        ? formData.background.trim().split(/\s+/).length
        : 0
      const communicationWords = formData.communication_style?.trim()
        ? formData.communication_style.trim().split(/\s+/).length
        : 0

      if (backgroundWords > gameData.value.validation_limits.character_background) return false
      if (communicationWords > gameData.value.validation_limits.character_communication)
        return false
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
        for (const [ability, abilityValue] of Object.entries(value)) {
          if (typeof abilityValue !== 'number' || abilityValue < 0 || abilityValue > 30) {
            errors.push(`${ability} must be between 0 and 30`)
          }
        }
      }

      if (fieldName === 'skills' && value && typeof value === 'object') {
        for (const [skill, skillValue] of Object.entries(value)) {
          if (typeof skillValue !== 'number' || skillValue < -5 || skillValue > 25) {
            errors.push(`${skill} must be between -5 and 25`)
          }
        }
      }
    } else if (requiredFields.includes(fieldName) && (!value || value.toString().trim() === '')) {
      errors.push('This field is required')
    }

    // Word limit checks
    if (fieldName === 'appearance' && entityType === 'PLAYER' && gameData.value) {
      const words = value?.trim() ? value.trim().split(/\s+/).length : 0
      if (words > gameData.value.validation_limits.player_appearance) {
        errors.push(`Maximum ${gameData.value.validation_limits.player_appearance} words allowed`)
      }
    }

    if (fieldName === 'background' && entityType === 'CHARACTER' && gameData.value) {
      const words = value?.trim() ? value.trim().split(/\s+/).length : 0
      if (words > gameData.value.validation_limits.character_background) {
        errors.push(
          `Maximum ${gameData.value.validation_limits.character_background} words allowed`
        )
      }
    }

    if (fieldName === 'communication_style' && entityType === 'CHARACTER' && gameData.value) {
      const words = value?.trim() ? value.trim().split(/\s+/).length : 0
      if (words > gameData.value.validation_limits.character_communication) {
        errors.push(
          `Maximum ${gameData.value.validation_limits.character_communication} words allowed`
        )
      }
    }

    return errors
  }

  return {
    isFormValid,
    getFieldErrors,
  }
}
