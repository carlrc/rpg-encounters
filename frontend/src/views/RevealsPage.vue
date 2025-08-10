<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Reveals"
    create-button-text="Add Reveal"
    empty-message="No reveals yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading reveals...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedReveal && !showCreateForm"
        icon="🧠"
        title="No Reveal Selected"
        message="Select a trust reveal from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Title -->
          <input
            v-model="createForm.title"
            placeholder="Reveal title"
            class="shared-input shared-input-name"
          />

          <!-- Character Selection -->
          <CharacterSelector
            v-model="createForm.character_ids"
            :characters="characters"
            label="Characters"
          />

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

          <!-- Level 2 Threshold Options -->
          <div v-if="createForm.enable_level_2" class="threshold-section">
            <h4 class="threshold-title">Level 2: Privileged Content Threshold</h4>
            <div class="threshold-options">
              <label class="shared-radio-option">
                <input
                  type="radio"
                  value="default"
                  v-model="createForm.privileged_threshold_mode"
                  @change="handlePrivilegedThresholdModeChange"
                />
                <span>Use Default Threshold</span>
              </label>
              <label class="shared-radio-option">
                <input type="radio" value="custom" v-model="createForm.privileged_threshold_mode" />
                <span>Custom Threshold</span>
              </label>
            </div>

            <div v-if="createForm.privileged_threshold_mode === 'custom'" class="custom-thresholds">
              <div class="threshold-slider">
                <label class="threshold-label">
                  Privileged Content:
                  {{
                    DC_LABELS[createForm.privileged_threshold] ||
                    `DC ${createForm.privileged_threshold}`
                  }}
                </label>
                <input
                  type="range"
                  v-model.number="createForm.privileged_threshold"
                  :min="THRESHOLD_LIMITS.min"
                  :max="THRESHOLD_LIMITS.max"
                  :step="THRESHOLD_LIMITS.step"
                  class="slider"
                />
              </div>
            </div>
          </div>

          <!-- Level 3 Content -->
          <div class="shared-field shared-field-full-width">
            <div class="level-toggle level-toggle-in-divider">
              <label class="level-toggle-option">
                <input
                  type="checkbox"
                  v-model="createForm.enable_level_3"
                  @change="handleLevel3Toggle"
                />
                <span>Add Level 3: Exclusive Content</span>
              </label>
            </div>

            <div v-if="createForm.enable_level_3">
              <label class="shared-field-label">Level 3: Exclusive Content</label>
              <BaseTextareaWithCharacterCounter
                v-model="createForm.level_3_content"
                placeholder="Enter exclusive content (maximum trust required)..."
                :max-characters="500"
              />
            </div>
          </div>

          <!-- Level 3 Threshold Options -->
          <div v-if="createForm.enable_level_3" class="threshold-section">
            <h4 class="threshold-title">Level 3: Exclusive Content Threshold</h4>
            <div class="threshold-options">
              <label class="shared-radio-option">
                <input
                  type="radio"
                  value="default"
                  v-model="createForm.exclusive_threshold_mode"
                  @change="handleExclusiveThresholdModeChange"
                />
                <span>Use Default Threshold</span>
              </label>
              <label class="shared-radio-option">
                <input type="radio" value="custom" v-model="createForm.exclusive_threshold_mode" />
                <span>Custom Threshold</span>
              </label>
            </div>

            <div v-if="createForm.exclusive_threshold_mode === 'custom'" class="custom-thresholds">
              <div class="threshold-slider">
                <label class="threshold-label">
                  Exclusive Content:
                  {{
                    DC_LABELS[createForm.exclusive_threshold] ||
                    `DC ${createForm.exclusive_threshold}`
                  }}
                </label>
                <input
                  type="range"
                  v-model.number="createForm.exclusive_threshold"
                  :min="THRESHOLD_LIMITS.min"
                  :max="THRESHOLD_LIMITS.max"
                  :step="THRESHOLD_LIMITS.step"
                  class="slider"
                />
              </div>
            </div>
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

      <RevealCard
        v-else-if="selectedReveal"
        :reveal="selectedReveal"
        :characters="characters"
        :current-trust-level="18"
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
  import RevealCard from '../components/RevealCard.vue'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from '../components/entity/CharacterSelector.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import { useRevealValidation } from '../composables/useRevealValidation.js'
  import apiService from '../services/api.js'
  import { DEFAULT_THRESHOLDS, THRESHOLD_LIMITS, DC_LABELS } from '../constants/gameData.js'

  export default {
    name: 'RevealsPage',
    components: {
      SplitViewLayout,
      EmptyState,
      RevealCard,
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
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
      } = useEntityCRUD('Reveal')

      const characters = ref([])

      const createForm = reactive({
        title: '',
        character_ids: [],
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
        privileged_threshold_mode: 'default',
        exclusive_threshold_mode: 'default',
        privileged_threshold: DEFAULT_THRESHOLDS.privileged,
        exclusive_threshold: DEFAULT_THRESHOLDS.exclusive,
      })

      const { isFormValid: isCreateFormValid } = useRevealValidation(createForm)

      const selectedReveal = computed(() => {
        return entities.value.find((n) => n.id === selectedEntityId.value) || null
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
          character_ids: [],
          level_1_content: '',
          level_2_content: '',
          level_3_content: '',
          enable_level_2: false,
          enable_level_3: false,
          privileged_threshold_mode: 'default',
          exclusive_threshold_mode: 'default',
          privileged_threshold: DEFAULT_THRESHOLDS.privileged,
          exclusive_threshold: DEFAULT_THRESHOLDS.exclusive,
        })
      }

      const saveCreate = async () => {
        if (isCreateFormValid.value) {
          try {
            const revealData = {
              title: createForm.title.trim(),
              character_ids: createForm.character_ids.map((id) => parseInt(id)),
              level_1_content: createForm.level_1_content.trim(),
              level_2_content: createForm.enable_level_2 ? createForm.level_2_content.trim() : null,
              level_3_content: createForm.enable_level_3 ? createForm.level_3_content.trim() : null,
            }

            // Add custom thresholds based on individual modes
            if (createForm.enable_level_2 && createForm.privileged_threshold_mode === 'custom') {
              revealData.privileged_threshold = createForm.privileged_threshold
            }
            if (createForm.enable_level_3 && createForm.exclusive_threshold_mode === 'custom') {
              revealData.exclusive_threshold = createForm.exclusive_threshold
            }

            await createEntity(revealData)
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

      const handlePrivilegedThresholdModeChange = () => {
        if (createForm.privileged_threshold_mode === 'default') {
          createForm.privileged_threshold = DEFAULT_THRESHOLDS.privileged
        }
      }

      const handleExclusiveThresholdModeChange = () => {
        if (createForm.exclusive_threshold_mode === 'default') {
          createForm.exclusive_threshold = DEFAULT_THRESHOLDS.exclusive
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
        selectedReveal,
        characters,
        createForm,
        isCreateFormValid,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        saveCreate,
        cancelCreate: handleCancelCreate,
        handleLevel2Toggle,
        handleLevel3Toggle,
        handlePrivilegedThresholdModeChange,
        handleExclusiveThresholdModeChange,
        DEFAULT_THRESHOLDS,
        THRESHOLD_LIMITS,
        DC_LABELS,
      }
    },
  }
</script>

<style scoped>
  .character-field {
    margin-bottom: 1.5rem;
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

  /* Threshold section styles using shared design tokens */
  .threshold-section {
    margin-bottom: var(--spacing-xl);
  }

  .threshold-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
  }

  .threshold-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    transition: background-color var(--transition-fast);
    font-size: var(--font-size-base);
    color: var(--text-primary);
  }

  .threshold-option:hover {
    background-color: var(--bg-light);
  }

  .threshold-option input[type='radio'] {
    margin: 0;
  }

  .threshold-option span {
    color: var(--text-primary);
    font-weight: var(--font-weight-medium);
  }

  .custom-thresholds {
    padding: var(--spacing-lg);
    border: 2px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
  }

  .threshold-slider {
    margin-bottom: var(--spacing-lg);
  }

  .threshold-slider:last-child {
    margin-bottom: 0;
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--border-default);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
    border: none;
  }

  .required {
    color: #dc3545;
    font-weight: bold;
  }

  /* Level 3 divider toggle styles */
  .level-toggle-in-divider {
    position: relative;
    margin: var(--spacing-xl) 0 var(--spacing-lg) 0;
  }

  .level-toggle-in-divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--border-default);
    z-index: 1;
  }

  .level-toggle-in-divider .level-toggle-option {
    position: relative;
    z-index: 2;
    background: var(--bg-white);
    margin: 0 auto;
    width: fit-content;
    padding: var(--spacing-sm) var(--spacing-lg);
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
