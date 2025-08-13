import { computed, ref, watch } from 'vue'
import { FORM_FIELDS } from '../constants/validation.js'
import { useGameData } from './useGameData.js'

/**
 * Enhanced entity validation composable
 * Provides comprehensive validation with detailed error messages
 */
export function useEntityValidation(formData, entityType = 'PLAYER') {
  const { gameData } = useGameData()
  const errors = ref({})
  const touched = ref({})

  // Get required fields for the entity type
  const requiredFields = FORM_FIELDS[entityType]?.REQUIRED || []

  // Mark field as touched
  const touchField = (fieldName) => {
    touched.value[fieldName] = true
  }

  // Mark all fields as touched
  const touchAllFields = () => {
    Object.keys(formData).forEach((field) => {
      touched.value[field] = true
    })
  }

  // Reset validation state
  const resetValidation = () => {
    errors.value = {}
    touched.value = {}
  }

  // Validate individual field
  const validateField = (fieldName, value) => {
    const fieldErrors = []

    // Required field validation
    if (requiredFields.includes(fieldName)) {
      if (!value || value.toString().trim() === '') {
        fieldErrors.push(`${getFieldLabel(fieldName)} is required`)
      }
    }

    // Entity-specific validations
    switch (entityType) {
      case 'PLAYER':
        if (fieldName === 'appearance' && gameData.value) {
          const words = value?.trim() ? value.trim().split(/\s+/).length : 0
          if (words > gameData.value.validation_limits.player_appearance) {
            fieldErrors.push(
              `Appearance must be ${gameData.value.validation_limits.player_appearance} words or less (currently ${words} words)`
            )
          }
        }
        break

      case 'CHARACTER':
        if (fieldName === 'background' && gameData.value) {
          const chars = value?.length || 0
          if (chars > gameData.value.validation_limits.character_background) {
            fieldErrors.push(
              `Background must be ${gameData.value.validation_limits.character_background} characters or less (currently ${chars} characters)`
            )
          }
        }
        if (fieldName === 'communication_style' && gameData.value) {
          const chars = value?.length || 0
          if (chars > gameData.value.validation_limits.character_communication) {
            fieldErrors.push(
              `Communication style must be ${gameData.value.validation_limits.character_communication} characters or less (currently ${chars} characters)`
            )
          }
        }
        if (fieldName === 'motivation' && gameData.value) {
          const chars = value?.length || 0
          if (chars > gameData.value.validation_limits.character_motivation) {
            fieldErrors.push(
              `Motivation must be ${gameData.value.validation_limits.character_motivation} characters or less (currently ${chars} characters)`
            )
          }
        }
        break

      case 'REVEAL':
        if (fieldName === 'title' && (!value || value.trim() === '')) {
          fieldErrors.push('Title is required')
        }
        if (fieldName === 'character_ids' && (!value || value.length === 0)) {
          fieldErrors.push('At least one character must be selected')
        }
        if (fieldName === 'level_1_content') {
          if (!value || value.trim() === '') {
            fieldErrors.push('Level 1 content is required')
          } else if (value.length > 500) {
            fieldErrors.push(
              `Level 1 content must be 500 characters or less (currently ${value.length} characters)`
            )
          }
        }
        if (fieldName === 'level_2_content' && value && value.length > 500) {
          fieldErrors.push(
            `Level 2 content must be 500 characters or less (currently ${value.length} characters)`
          )
        }
        if (fieldName === 'level_3_content' && value && value.length > 500) {
          fieldErrors.push(
            `Level 3 content must be 500 characters or less (currently ${value.length} characters)`
          )
        }
        break
    }

    // Email validation
    if (fieldName === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        fieldErrors.push('Please enter a valid email address')
      }
    }

    return fieldErrors
  }

  // Get human-readable field label
  const getFieldLabel = (fieldName) => {
    const labels = {
      name: 'Name',
      race: 'Race',
      class_name: 'Class',
      size: 'Size',
      alignment: 'Alignment',
      gender: 'Gender',
      profession: 'Profession',
      background: 'Background',
      communication_style: 'Communication Style',
      motivation: 'Motivation',
      appearance: 'Appearance',
      title: 'Title',
      character_ids: 'Characters',
      level_1_content: 'Level 1 Content',
      level_2_content: 'Level 2 Content',
      level_3_content: 'Level 3 Content',
    }
    return (
      labels[fieldName] || fieldName.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
    )
  }

  // Validate all fields
  const validateAllFields = () => {
    const newErrors = {}

    Object.keys(formData).forEach((fieldName) => {
      const fieldErrors = validateField(fieldName, formData[fieldName])
      if (fieldErrors.length > 0) {
        newErrors[fieldName] = fieldErrors
      }
    })

    errors.value = newErrors
    return Object.keys(newErrors).length === 0
  }

  // Get errors for a specific field
  const getFieldErrors = (fieldName) => {
    return errors.value[fieldName] || []
  }

  // Check if field has errors
  const hasFieldError = (fieldName) => {
    return getFieldErrors(fieldName).length > 0
  }

  // Check if field should show errors (touched and has errors)
  const shouldShowFieldError = (fieldName) => {
    return touched.value[fieldName] && hasFieldError(fieldName)
  }

  // Overall form validity
  const isFormValid = computed(() => {
    // Check all required fields are filled
    const hasRequiredFields = requiredFields.every((field) => {
      const value = formData[field]
      return value && value.toString().trim() !== ''
    })

    if (!hasRequiredFields) return false

    // Check for any validation errors
    const hasErrors = Object.keys(errors.value).some((field) => errors.value[field].length > 0)

    return !hasErrors
  })

  // Watch form data and validate touched fields
  watch(
    () => formData,
    () => {
      Object.keys(touched.value).forEach((fieldName) => {
        if (touched.value[fieldName]) {
          const fieldErrors = validateField(fieldName, formData[fieldName])
          if (fieldErrors.length > 0) {
            errors.value[fieldName] = fieldErrors
          } else {
            delete errors.value[fieldName]
          }
        }
      })
    },
    { deep: true }
  )

  return {
    errors: computed(() => errors.value),
    touched: computed(() => touched.value),
    isFormValid,
    touchField,
    touchAllFields,
    resetValidation,
    validateField,
    validateAllFields,
    getFieldErrors,
    hasFieldError,
    shouldShowFieldError,
    getFieldLabel,
  }
}
