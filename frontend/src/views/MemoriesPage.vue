<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Memories"
    create-button-text="Add Memory"
    empty-message="No memories yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="memoryFilterTabs"
        :characters="characters"
      />
    </template>
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading memories...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedMemory && !showCreateForm"
        icon="🧠"
        title="No Memory Selected"
        message="Select a memory from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Title -->
          <input
            v-model="createForm.title"
            placeholder="Memory title"
            class="shared-input shared-input-name"
          />

          <!-- Content -->
          <div class="content-field">
            <label class="shared-field-label">Content <span class="required">*</span></label>
            <BaseTextareaWithCharacterCounter
              v-model="createForm.content"
              :placeholder="`Memory content`"
              :max-characters="1000"
            />
          </div>

          <!-- Character Selection -->
          <CharacterSelector
            v-model="createForm.character_ids"
            :characters="characters"
            :enable-filtering="true"
            label="Characters"
          />

          <div class="shared-actions">
            <button
              @click="saveCreate"
              class="shared-btn shared-btn-success"
              :disabled="!isCreateFormValid"
            >
              Save
            </button>
            <button @click="cancelCreate" class="shared-btn shared-btn-secondary">Cancel</button>
          </div>
        </div>
      </div>

      <MemoryCard
        v-else-if="selectedMemory"
        :memory="selectedMemory"
        :characters="characters"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script>
  import { ref, reactive, computed, onMounted } from 'vue'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import MemoryCard from '../components/MemoryCard.vue'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from '../components/entity/CharacterSelector.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import { applyCharacterFilters } from '../utils/filterUtils.js'
  import apiService from '../services/api.js'

  const CONTENT_WORD_LIMIT = 200

  export default {
    name: 'MemoriesPage',
    components: {
      SplitViewLayout,
      EmptyState,
      MemoryCard,
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
      FilterPanel,
    },
    setup() {
      const {
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
        cancelCreate,
      } = useEntityCRUD('Memory')

      const characters = ref([])

      // Memory filter tabs configuration
      const memoryFilterTabs = [{ id: 'characters', label: 'Characters' }]

      // Character filtering state
      const activeFilters = ref({
        characterIds: [],
        showUnassigned: false,
      })

      const createForm = reactive({
        title: '',
        content: '',
        character_ids: [],
      })

      const isCreateFormValid = computed(() => {
        return (
          createForm.title.trim().length > 0 &&
          createForm.content.trim().length > 0 &&
          createForm.character_ids.length > 0 &&
          createForm.content.trim().split(' ').length <= CONTENT_WORD_LIMIT
        )
      })

      const selectedMemory = computed(() => {
        return entities.value.find((m) => m.id === selectedEntityId.value) || null
      })

      const loadCharacters = async () => {
        try {
          characters.value = await apiService.getCharacters()
        } catch (err) {
          console.error('Error loading characters:', err)
        }
      }

      const resetCreateForm = () => {
        Object.assign(createForm, {
          title: '',
          content: '',
          character_ids: [],
        })
      }

      const saveCreate = async () => {
        if (isCreateFormValid.value) {
          try {
            const memoryData = {
              title: createForm.title.trim(),
              content: createForm.content.trim(),
              character_ids: createForm.character_ids,
            }

            await createEntity(memoryData)
            resetCreateForm()
          } catch (err) {
            // Error handling is done in useEntityCRUD
          }
        }
      }

      const handleCancelCreate = () => {
        cancelCreate()
        resetCreateForm()
      }

      onMounted(async () => {
        await loadEntities()
        await loadCharacters()
      })

      // Filtered entities based on character filters
      const filteredEntities = computed(() => {
        return applyCharacterFilters(entities.value, activeFilters.value)
      })

      const hasActiveCharacterFilters = computed(() => {
        return activeFilters.value.characterIds.length > 0 || activeFilters.value.showUnassigned
      })

      const clearCharacterFilters = () => {
        activeFilters.value.characterIds = []
        activeFilters.value.showUnassigned = false
      }

      return {
        entities,
        filteredEntities,
        activeFilters,
        memoryFilterTabs,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedMemory,
        characters,
        createForm,
        isCreateFormValid,
        CONTENT_WORD_LIMIT,
        hasActiveCharacterFilters,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        saveCreate,
        cancelCreate: handleCancelCreate,
        clearCharacterFilters,
      }
    },
  }
</script>

<style scoped>
  .content-field {
    margin-bottom: 1.5rem;
  }

  .required {
    color: #dc3545;
    font-weight: bold;
  }

  /* Ensure text areas take full width */
  .shared-field-full-width :deep(.shared-word-counter-field) {
    width: 100% !important;
  }

  .shared-field-full-width :deep(.shared-textarea) {
    width: 100% !important;
    box-sizing: border-box;
    min-width: 100%;
  }
</style>
