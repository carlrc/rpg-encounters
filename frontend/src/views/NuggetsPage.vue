<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Trust Nuggets"
    create-button-text="Add Nugget"
    empty-message="No trust nuggets yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #detail-content>
      <div v-if="loading" class="loading">Loading nuggets...</div>
      <div v-else-if="error" class="error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedNugget && !showCreateForm"
        icon="🧠"
        title="No Nugget Selected"
        message="Select a trust nugget from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Title -->
          <input
            v-model="createForm.title"
            placeholder="Nugget title"
            class="shared-input shared-input-name"
          />

          <!-- Character Selection -->
          <div class="character-field">
            <label class="shared-field-label">Characters</label>
            <div class="character-selection">
              <div v-for="character in characters" :key="character.id" class="character-checkbox">
                <label class="character-option">
                  <input type="checkbox" :value="character.id" v-model="createForm.character_ids" />
                  <span>{{ character.name }}</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Level 1 Content (Always Required) -->
          <div class="shared-field shared-field-full-width">
            <label class="shared-field-label"
              >Level 1: Public Content <span class="required">*</span></label
            >
            <BaseTextareaWithCharacterCounter
              v-model="createForm.level_1_content"
              placeholder="Enter public content (always accessible)..."
              :max-characters="500"
            />
          </div>

          <!-- Level 2 Toggle -->
          <div class="level-toggle">
            <label class="level-toggle-option">
              <input
                type="checkbox"
                v-model="createForm.enable_level_2"
                @change="handleLevel2Toggle"
              />
              <span>Add Level 2: Privileged Content</span>
            </label>
          </div>

          <!-- Level 2 Content -->
          <div v-if="createForm.enable_level_2" class="shared-field shared-field-full-width">
            <label class="shared-field-label">Level 2: Privileged Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="createForm.level_2_content"
              placeholder="Enter privileged content (high trust required)..."
              :max-characters="500"
            />
          </div>

          <!-- Level 3 Toggle -->
          <div class="level-toggle">
            <label class="level-toggle-option">
              <input
                type="checkbox"
                v-model="createForm.enable_level_3"
                @change="handleLevel3Toggle"
              />
              <span>Add Level 3: Exclusive Content</span>
            </label>
          </div>

          <!-- Level 3 Content -->
          <div v-if="createForm.enable_level_3" class="shared-field shared-field-full-width">
            <label class="shared-field-label">Level 3: Exclusive Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="createForm.level_3_content"
              placeholder="Enter exclusive content (maximum trust required)..."
              :max-characters="500"
            />
          </div>

          <!-- Actions -->
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

      <NuggetCard
        v-else-if="selectedNugget"
        :nugget="selectedNugget"
        :characters="characters"
        :current-trust-level="0.6"
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
  import NuggetCard from '../components/NuggetCard.vue'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import apiService from '../services/api.js'

  export default {
    name: 'NuggetsPage',
    components: {
      SplitViewLayout,
      EmptyState,
      NuggetCard,
      BaseTextareaWithCharacterCounter,
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
      } = useEntityCRUD('Nugget')

      const characters = ref([])

      const createForm = reactive({
        title: '',
        character_ids: [],
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
      })

      const isCreateFormValid = computed(() => {
        const baseValid =
          createForm.title.trim() &&
          createForm.character_ids.length > 0 &&
          createForm.level_1_content.trim() &&
          createForm.level_1_content.length <= 500

        const level2Valid =
          !createForm.enable_level_2 ||
          (createForm.level_2_content.trim() && createForm.level_2_content.length <= 500)

        const level3Valid =
          !createForm.enable_level_3 ||
          (createForm.level_3_content.trim() && createForm.level_3_content.length <= 500)

        return baseValid && level2Valid && level3Valid
      })

      const selectedNugget = computed(() => {
        return entities.value.find((n) => n.id === selectedEntityId.value) || null
      })

      const getLevelName = (level) => {
        const names = {
          1: 'Public',
          2: 'Privileged',
          3: 'Exclusive',
        }
        return names[level] || 'Unknown'
      }

      const getLevelDescription = (level) => {
        const descriptions = {
          1: 'Always accessible',
          2: 'High trust required',
          3: 'Maximum trust required',
        }
        return descriptions[level] || 'Unknown level'
      }

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
          character_ids: [],
          level_1_content: '',
          level_2_content: '',
          level_3_content: '',
          enable_level_2: false,
          enable_level_3: false,
        })
      }

      const saveCreate = async () => {
        if (isCreateFormValid.value) {
          try {
            const nuggetData = {
              title: createForm.title.trim(),
              character_ids: createForm.character_ids.map((id) => parseInt(id)),
              level_1_content: createForm.level_1_content.trim(),
              level_2_content: createForm.enable_level_2 ? createForm.level_2_content.trim() : null,
              level_3_content: createForm.enable_level_3 ? createForm.level_3_content.trim() : null,
            }

            await createEntity(nuggetData)
            resetCreateForm()
          } catch (err) {
            // Error handling is done in useEntityCRUD
          }
        }
      }

      const handleLevel2Toggle = () => {
        if (!createForm.enable_level_2) {
          createForm.level_2_content = ''
        }
      }

      const handleLevel3Toggle = () => {
        if (!createForm.enable_level_3) {
          createForm.level_3_content = ''
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

      return {
        entities,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedNugget,
        characters,
        createForm,
        isCreateFormValid,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        getLevelName,
        getLevelDescription,
        saveCreate,
        cancelCreate: handleCancelCreate,
        handleLevel2Toggle,
        handleLevel3Toggle,
      }
    },
  }
</script>

<style scoped>
  .loading {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 1.1em;
  }

  .error {
    text-align: left;
    padding: 20px;
    color: #dc3545;
    font-size: 0.95em;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    margin: 20px;
    white-space: pre-line;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.5;
  }

  .character-field,
  .trust-level-field,
  .content-field {
    margin-bottom: 1.5rem;
  }

  .trust-level-options {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .trust-level-option {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .trust-level-option:hover {
    border-color: #007bff;
    background: #f8f9fa;
  }

  .trust-level-option.active {
    border-color: #007bff;
    background: #e3f2fd;
  }

  .trust-level-option input[type='radio'] {
    margin: 0;
  }

  .trust-level-info {
    flex: 1;
  }

  .trust-level-name {
    font-weight: 600;
    color: #495057;
    margin-bottom: 0.25rem;
  }

  .trust-level-desc {
    font-size: 0.875rem;
    color: #6c757d;
  }

  .trust-level-option.active .trust-level-name {
    color: #007bff;
  }

  .character-selection {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    max-height: 150px;
    overflow-y: auto;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
  }

  .character-checkbox {
    display: flex;
    align-items: center;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    width: 100%;
    font-size: 0.9rem;
  }

  .character-option:hover {
    background-color: #e9ecef;
  }

  .character-option input[type='checkbox'] {
    margin: 0;
    transform: scale(0.9);
  }

  .character-option span {
    font-weight: 500;
    color: #495057;
  }

  /* Level toggle styles */
  .level-toggle {
    margin-bottom: 1rem;
  }

  .level-toggle-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    font-weight: 500;
    color: #495057;
  }

  .level-toggle-option:hover {
    border-color: #007bff;
    background: #e3f2fd;
  }

  .level-toggle-option input[type='checkbox'] {
    margin: 0;
    transform: scale(1.1);
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
