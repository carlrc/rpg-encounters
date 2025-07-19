import { ref, reactive } from 'vue'

/**
 * Composable for managing form state and operations
 * @param {Object} initialFormData - Initial form data structure
 * @param {Function} validationFn - Function to validate the form
 * @returns {Object} - Form management utilities
 */
export function useFormManagement(initialFormData, validationFn) {
    const isEditing = ref(false)
    const form = reactive({ ...initialFormData })

    /**
     * Reset form to initial state
     */
    const resetForm = () => {
        Object.keys(initialFormData).forEach(key => {
            if (Array.isArray(initialFormData[key])) {
                form[key] = []
            } else if (typeof initialFormData[key] === 'object' && initialFormData[key] !== null) {
                form[key] = { ...initialFormData[key] }
            } else {
                form[key] = initialFormData[key]
            }
        })
    }

    /**
     * Populate form with entity data
     * @param {Object} entityData - Data to populate form with
     */
    const populateForm = (entityData) => {
        Object.keys(form).forEach(key => {
            if (entityData.hasOwnProperty(key)) {
                if (Array.isArray(form[key])) {
                    form[key] = [...(entityData[key] || [])]
                } else if (typeof form[key] === 'object' && form[key] !== null) {
                    form[key] = { ...(entityData[key] || {}) }
                } else {
                    form[key] = entityData[key] || initialFormData[key]
                }
            }
        })
    }

    /**
     * Start editing mode
     * @param {Object} entityData - Optional data to populate form with
     */
    const startEdit = (entityData = null) => {
        if (entityData) {
            populateForm(entityData)
        }
        isEditing.value = true
    }

    /**
     * Cancel editing mode
     */
    const cancelEdit = () => {
        isEditing.value = false
        resetForm()
    }

    /**
     * Get form validation status
     */
    const isFormValid = validationFn ? () => validationFn(form) : () => true

    return {
        isEditing,
        form,
        resetForm,
        populateForm,
        startEdit,
        cancelEdit,
        isFormValid
    }
}
