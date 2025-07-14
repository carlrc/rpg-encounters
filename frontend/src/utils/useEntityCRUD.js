import { ref, reactive } from 'vue'
import apiService from '../services/api.js'

export function useEntityCRUD(entityType) {
    const entities = ref([])
    const loading = ref(false)
    const error = ref('')
    const selectedEntityId = ref(null)
    const showCreateForm = ref(false)

    // API method names based on entity type
    const getPlural = (type) => {
        if (type === 'Memory') return 'Memories'
        return `${type}s`
    }

    const apiMethods = {
        get: `get${getPlural(entityType)}`,
        getOne: `get${entityType}`,
        create: `create${entityType}`,
        update: `update${entityType}`,
        delete: `delete${entityType}`
    }

    const loadEntities = async () => {
        loading.value = true
        error.value = ''
        try {
            entities.value = await apiService[apiMethods.get]()
        } catch (err) {
            error.value = `Failed to load ${entityType.toLowerCase()}s. Make sure the backend is running.`
            console.error(`Error loading ${entityType.toLowerCase()}s:`, err)
        } finally {
            loading.value = false
        }
    }

    const createEntity = async (entityData) => {
        try {
            const newEntity = await apiService[apiMethods.create](entityData)
            entities.value.push(newEntity)
            selectedEntityId.value = newEntity.id
            showCreateForm.value = false
            return newEntity
        } catch (err) {
            error.value = `Failed to create ${entityType.toLowerCase()}`
            console.error(`Error creating ${entityType.toLowerCase()}:`, err)
            throw err
        }
    }

    const updateEntity = async (entityId, entityData) => {
        try {
            const updatedEntity = await apiService[apiMethods.update](entityId, entityData)
            const index = entities.value.findIndex(e => e.id === entityId)
            if (index !== -1) {
                entities.value[index] = updatedEntity
            }
            return updatedEntity
        } catch (err) {
            error.value = `Failed to update ${entityType.toLowerCase()}`
            console.error(`Error updating ${entityType.toLowerCase()}:`, err)
            throw err
        }
    }

    const deleteEntity = async (entityId) => {
        try {
            await apiService[apiMethods.delete](entityId)
            entities.value = entities.value.filter(e => e.id !== entityId)

            // If we deleted the selected entity, select another one or clear selection
            if (selectedEntityId.value === entityId) {
                if (entities.value.length > 0) {
                    selectedEntityId.value = entities.value[0].id
                } else {
                    selectedEntityId.value = null
                }
            }
        } catch (err) {
            error.value = `Failed to delete ${entityType.toLowerCase()}`
            console.error(`Error deleting ${entityType.toLowerCase()}:`, err)
            throw err
        }
    }

    const selectEntity = (entityId) => {
        selectedEntityId.value = entityId
        showCreateForm.value = false
    }

    const startCreate = () => {
        showCreateForm.value = true
        selectedEntityId.value = null
    }

    const cancelCreate = () => {
        showCreateForm.value = false
    }

    return {
        entities,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        loadEntities,
        createEntity,
        updateEntity,
        deleteEntity,
        selectEntity,
        startCreate,
        cancelCreate
    }
}
