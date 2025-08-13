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
      return value && value.toString().trim() !== ''
    })

    if (!hasRequiredFields) return false

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

    if (requiredFields.includes(fieldName) && (!value || value.toString().trim() === '')) {
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
