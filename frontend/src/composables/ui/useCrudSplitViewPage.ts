import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { serializeError } from 'serialize-error'

export function useCrudSplitViewPage(options) {
  const {
    store,
    loadDeps,
    parseRouteSelection,
    applyEntityFilters,
    createErrorLabel = 'Entity',
  } = options

  const { entities, loading, error, selectedEntityId, selectedEntity, showCreateForm } =
    storeToRefs(store)

  const {
    loadEntities,
    createEntity,
    updateEntity,
    deleteEntity,
    selectEntity,
    startCreate,
    cancelCreate,
  } = store

  const filteredEntities = computed(() => {
    if (typeof applyEntityFilters !== 'function') {
      return entities.value
    }
    return applyEntityFilters(entities.value)
  })

  const handleCreateSave = async (formData) => {
    try {
      await createEntity(formData)
    } catch (err) {
      console.error(
        `${createErrorLabel} entity creation error:`,
        JSON.stringify(serializeError(err))
      )
    }
  }

  const handleCancelCreate = () => {
    cancelCreate()
  }

  const trySelectFromRoute = () => {
    if (typeof parseRouteSelection !== 'function') {
      return
    }

    const selectedId = parseRouteSelection(entities.value)
    if (selectedId != null) {
      selectEntity(selectedId)
    }
  }

  const initializePage = async () => {
    if (typeof loadDeps === 'function') {
      await loadDeps()
    }

    await loadEntities()
    trySelectFromRoute()
  }

  onMounted(async () => {
    await initializePage()
  })

  return {
    entities,
    filteredEntities,
    loading,
    error,
    selectedEntityId,
    selectedEntity,
    showCreateForm,
    updateEntity,
    deleteEntity,
    selectEntity,
    startCreate,
    handleCreateSave,
    handleCancelCreate,
    trySelectFromRoute,
    initializePage,
  }
}
