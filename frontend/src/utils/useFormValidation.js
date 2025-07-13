import { computed } from 'vue'
import { FORM_FIELDS, WORD_LIMITS } from '../constants/validation.js'

export function useFormValidation(formData, entityType = 'PLAYER') {
    const requiredFields = FORM_FIELDS[entityType].REQUIRED

    const isFormValid = computed(() => {
        // Check all required fields are filled
        const hasRequiredFields = requiredFields.every(field => {
            const value = formData[field]
            return value && value.toString().trim() !== ''
        })

        if (!hasRequiredFields) return false

        // Check word limits based on entity type
        if (entityType === 'PLAYER') {
            const appearanceWords = formData.appearance?.trim()
                ? formData.appearance.trim().split(/\s+/).length
                : 0
            if (appearanceWords > WORD_LIMITS.PLAYER_APPEARANCE) return false
        }

        if (entityType === 'CHARACTER') {
            const backgroundWords = formData.background?.trim()
                ? formData.background.trim().split(/\s+/).length
                : 0
            const communicationWords = formData.communication_style?.trim()
                ? formData.communication_style.trim().split(/\s+/).length
                : 0

            if (backgroundWords > WORD_LIMITS.CHARACTER_BACKGROUND) return false
            if (communicationWords > WORD_LIMITS.CHARACTER_COMMUNICATION) return false
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
        if (fieldName === 'appearance' && entityType === 'PLAYER') {
            const words = value?.trim() ? value.trim().split(/\s+/).length : 0
            if (words > WORD_LIMITS.PLAYER_APPEARANCE) {
                errors.push(`Maximum ${WORD_LIMITS.PLAYER_APPEARANCE} words allowed`)
            }
        }

        if (fieldName === 'background' && entityType === 'CHARACTER') {
            const words = value?.trim() ? value.trim().split(/\s+/).length : 0
            if (words > WORD_LIMITS.CHARACTER_BACKGROUND) {
                errors.push(`Maximum ${WORD_LIMITS.CHARACTER_BACKGROUND} words allowed`)
            }
        }

        if (fieldName === 'communication_style' && entityType === 'CHARACTER') {
            const words = value?.trim() ? value.trim().split(/\s+/).length : 0
            if (words > WORD_LIMITS.CHARACTER_COMMUNICATION) {
                errors.push(`Maximum ${WORD_LIMITS.CHARACTER_COMMUNICATION} words allowed`)
            }
        }

        return errors
    }

    return {
        isFormValid,
        getFieldErrors
    }
}
