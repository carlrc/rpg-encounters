import { computed, ref, watch } from 'vue'
import { FORM_FIELDS } from '../constants/validation.js'
import { useGameData } from './useGameData.js'
import { validateCharacterLimit } from '../utils/validationHelpers.js'

/**
 * Enhanced entity validation composable
 * All validation limits now come from backend gameData
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

    // Character limit validation using shared helper
    const limitError = validateCharacterLimit(value, fieldName, entityType, gameData.value)
    if (limitError) {
      fieldErrors.push(limitError)
    }

    // Special validations
    if (fieldName === 'character_ids' && (!value || value.length === 0)) {
      fieldErrors.push('At least one character must be selected')
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
