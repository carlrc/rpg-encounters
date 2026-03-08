import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { useWorldStore } from '@/stores/world'

type EntityApi<TEntity extends { id: number }, TCreate, TUpdate> = {
  getAll: () => Promise<TEntity[]>
  getOne: (id: number) => Promise<TEntity>
  create: (data: TCreate) => Promise<TEntity>
  update: (id: number, data: TUpdate) => Promise<TEntity>
  delete: (id: number) => Promise<unknown>
}

export const createEntityStore = <TEntity extends { id: number }, TCreate, TUpdate>(
  entityName: string,
  apiMethods: EntityApi<TEntity, TCreate, TUpdate>
) => {
  return defineStore(`${entityName.toLowerCase()}s`, () => {
    const entities = ref<TEntity[]>([])
    const loading = ref(false)
    const error = ref('')
    const selectedEntityId = ref<number | null>(null)
    const showCreateForm = ref(false)

    const notificationStore = useNotificationStore()
    const worldStore = useWorldStore()

    const { showError, showSuccess } = notificationStore

    // Getters
    const selectedEntity = computed(
      () => entities.value.find((e) => e.id === selectedEntityId.value) || null
    )

    // Actions
    const loadEntities = async () => {
      // Triggered by state changes (even logout) where there is no world set
      if (!worldStore.currentWorldId) {
        return
      }

      loading.value = true
      error.value = ''
      try {
        entities.value = await apiMethods.getAll()
      } catch (err) {
        const errorMessage = `Failed to load ${entityName.toLowerCase()}s. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
      } finally {
        loading.value = false
      }
    }

    const createEntity = async (entityData: TCreate) => {
      try {
        const newEntity = await apiMethods.create(entityData)
        entities.value.push(newEntity)
        selectedEntityId.value = newEntity.id
        showCreateForm.value = false
        showSuccess(`${entityName} created successfully!`)
        return newEntity
      } catch (err) {
        const errorMessage = `Failed to create ${entityName.toLowerCase()}. Please check your input.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error creating ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const updateEntity = async (entityId: number, entityData: TUpdate) => {
      try {
        const updatedEntity = await apiMethods.update(entityId, entityData)
        const index = entities.value.findIndex((e) => e.id === entityId)
        if (index !== -1) {
          entities.value[index] = updatedEntity
        }
        showSuccess(`${entityName} updated successfully!`)
        return updatedEntity
      } catch (err) {
        const errorMessage = `Failed to update ${entityName.toLowerCase()}. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error updating ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const deleteEntity = async (entityId: number) => {
      try {
        await apiMethods.delete(entityId)
        entities.value = entities.value.filter((e) => e.id !== entityId)

        if (selectedEntityId.value === entityId) {
          if (entities.value.length > 0) {
            selectedEntityId.value = entities.value[0].id
          } else {
            selectedEntityId.value = null
          }
        }
        showSuccess(`${entityName} deleted successfully!`)
      } catch (err) {
        const errorMessage = `Failed to delete ${entityName.toLowerCase()}. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error deleting ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const selectEntity = (entityId: number) => {
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

    const clearEntities = () => {
      entities.value = []
      selectedEntityId.value = null
      showCreateForm.value = false
      error.value = ''
    }

    // Watch for world changes and automatically reload data
    watch(
      () => worldStore.currentWorldId,
      (newWorldId) => {
        clearEntities()
        // Don't trigger load entities without valid world id
        if (newWorldId) {
          loadEntities()
        }
      }
    )

    return {
      entities,
      loading,
      error,
      selectedEntityId,
      selectedEntity,
      showCreateForm,
      loadEntities,
      createEntity,
      updateEntity,
      deleteEntity,
      selectEntity,
      startCreate,
      cancelCreate,
      clearEntities,
    }
  })
}
