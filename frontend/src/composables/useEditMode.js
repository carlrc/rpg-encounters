import { ref, reactive, watch } from 'vue'

/**
 * Edit mode management composable
 * Handles view/edit mode switching and form state management
 */
export function useEditMode(initialData = {}, options = {}) {
  const {
    onSave = () => {},
    onCancel = () => {},
    onDelete = () => {},
    resetOnCancel = true,
    validateOnSave = true,
  } = options

  const isEditing = ref(false)
  const isSaving = ref(false)
  const isDeleting = ref(false)

  // Form data - reactive copy of the initial data
  const formData = reactive({ ...initialData })

  // Keep a backup of original data for reset functionality
  const originalData = ref({ ...initialData })

  // Start editing mode
  const startEdit = (data = null) => {
    if (data) {
      Object.assign(formData, data)
      originalData.value = { ...data }
    }
    isEditing.value = true
  }

  // Cancel editing and optionally reset form
  const cancelEdit = async () => {
    if (resetOnCancel) {
      Object.assign(formData, originalData.value)
    }

    isEditing.value = false

    if (typeof onCancel === 'function') {
      await onCancel()
    }
  }

  // Save changes
  const saveEdit = async (validationFn = null) => {
    if (isSaving.value) return false

    // Validate if validation function provided
    if (validateOnSave && validationFn && typeof validationFn === 'function') {
      const isValid = validationFn()
      if (!isValid) {
        return false
      }
    }

    isSaving.value = true

    try {
      const result = await onSave({ ...formData })

      // Update original data with saved data
      originalData.value = { ...formData }
      isEditing.value = false

      return result
    } catch (error) {
      console.error('Error saving:', error)
      throw error
    } finally {
      isSaving.value = false
    }
  }

  // Delete entity
  const deleteEntity = async (confirmMessage = 'Are you sure you want to delete this item?') => {
    if (isDeleting.value) return false

    if (!confirm(confirmMessage)) {
      return false
    }

    isDeleting.value = true

    try {
      const result = await onDelete()
      return result
    } catch (error) {
      console.error('Error deleting:', error)
      throw error
    } finally {
      isDeleting.value = false
    }
  }

  // Reset form to original data
  const resetForm = () => {
    Object.assign(formData, originalData.value)
  }

  // Update form field
  const updateField = (fieldName, value) => {
    formData[fieldName] = value
  }

  // Update multiple fields
  const updateFields = (updates) => {
    Object.assign(formData, updates)
  }

  // Check if form has changes
  const hasChanges = () => {
    return JSON.stringify(formData) !== JSON.stringify(originalData.value)
  }

  // Update original data (useful when parent data changes)
  const updateOriginalData = (newData) => {
    originalData.value = { ...newData }
    if (!isEditing.value) {
      Object.assign(formData, newData)
    }
  }

  // Watch for external data changes and update if not editing
  const watchExternalData = (dataRef) => {
    watch(
      dataRef,
      (newData) => {
        if (newData && !isEditing.value) {
          updateOriginalData(newData)
        }
      },
      { deep: true, immediate: true }
    )
  }

  return {
    // State
    isEditing,
    isSaving,
    isDeleting,
    formData,

    // Actions
    startEdit,
    cancelEdit,
    saveEdit,
    deleteEntity,
    resetForm,
    updateField,
    updateFields,
    updateOriginalData,
    watchExternalData,

    // Computed
    hasChanges,
  }
}
