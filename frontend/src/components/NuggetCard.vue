<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="nugget-display">
      <!-- Title -->
      <h2 class="shared-title">{{ nugget.title }}</h2>

      <!-- Trust Level Display -->
      <div class="shared-field-columns">
        <div class="shared-field-column">
          <div class="shared-field">
            <div class="shared-field-label">Level 1: Public</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ nugget.level_1_content }}</div>
            </div>
          </div>

          <div v-if="nugget.level_2_content" class="shared-field">
            <div class="shared-field-label">Level 2: Privileged</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ nugget.level_2_content }}</div>
            </div>
          </div>
        </div>

        <div class="shared-field-column">
          <div v-if="nugget.level_3_content" class="shared-field">
            <div class="shared-field-label">Level 3: Exclusive</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ nugget.level_3_content }}</div>
            </div>
          </div>

          <div class="shared-field">
            <div class="shared-field-label">Assigned Characters</div>
            <div class="shared-field-value">
              <div class="shared-tags-display">
                <span
                  v-for="characterId in nugget.character_ids"
                  :key="characterId"
                  class="shared-tag-bubble"
                >
                  {{ getCharacterName(characterId) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="confirmDelete" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else class="nugget-edit">
      <!-- Edit Form -->
      <div class="shared-form">
        <!-- Title -->
        <input
          v-model="editForm.title"
          placeholder="Nugget title"
          class="shared-input shared-input-name"
        />

        <!-- Character Selection -->
        <div class="character-field">
          <label class="shared-field-label">Characters</label>
          <div class="character-selection">
            <div v-for="character in characters" :key="character.id" class="character-checkbox">
              <label class="shared-checkbox-option">
                <input type="checkbox" :value="character.id" v-model="editForm.character_ids" />
                <span>{{ character.name }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Level 1 Content (Always Required) -->
        <div class="shared-field shared-field-full-width">
          <label class="shared-field-label">Level 1: Public Content</label>
          <BaseTextareaWithCharacterCounter
            v-model="editForm.level_1_content"
            placeholder="Enter public content (always accessible)..."
            :max-characters="500"
          />
        </div>

        <!-- Level 2 Content -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-toggle">
            <label class="shared-toggle-option">
              <input
                type="checkbox"
                v-model="editForm.enable_level_2"
                @change="handleLevel2Toggle"
              />
              <span>Add Level 2: Privileged Content</span>
            </label>
          </div>

          <div v-if="editForm.enable_level_2">
            <label class="shared-field-label">Level 2: Privileged Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="editForm.level_2_content"
              placeholder="Enter privileged content (high trust required)..."
              :max-characters="500"
            />
          </div>
        </div>

        <!-- Level 2 Trust Threshold -->
        <div v-if="editForm.enable_level_2" class="threshold-section">
          <div class="threshold-options">
            <label class="shared-radio-option">
              <input
                type="radio"
                value="default"
                v-model="editForm.threshold_mode"
                @change="handleThresholdModeChange"
              />
              <span>Use Default Threshold</span>
            </label>

            <label class="shared-radio-option">
              <input
                type="radio"
                value="custom"
                v-model="editForm.threshold_mode"
                @change="handleThresholdModeChange"
              />
              <span>Custom Threshold</span>
            </label>
          </div>

          <!-- Level 2 Custom Threshold Slider -->
          <div v-if="editForm.threshold_mode === 'custom'" class="custom-thresholds">
            <div class="threshold-slider">
              <label class="threshold-label">
                Privileged Content: {{ (editForm.privileged_threshold * 100).toFixed(0) }}%
              </label>
              <input
                type="range"
                v-model.number="editForm.privileged_threshold"
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
          <div class="shared-toggle">
            <label class="shared-toggle-option">
              <input
                type="checkbox"
                v-model="editForm.enable_level_3"
                @change="handleLevel3Toggle"
              />
              <span>Add Level 3: Exclusive Content</span>
            </label>
          </div>

          <div v-if="editForm.enable_level_3">
            <label class="shared-field-label">Level 3: Exclusive Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="editForm.level_3_content"
              placeholder="Enter exclusive content (maximum trust required)..."
              :max-characters="500"
            />
          </div>
        </div>

        <!-- Level 3 Trust Threshold -->
        <div v-if="editForm.enable_level_3" class="threshold-section">
          <div class="threshold-options">
            <label class="shared-radio-option">
              <input
                type="radio"
                value="default"
                v-model="editForm.threshold_mode"
                @change="handleThresholdModeChange"
              />
              <span>Use Default Threshold</span>
            </label>

            <label class="shared-radio-option">
              <input
                type="radio"
                value="custom"
                v-model="editForm.threshold_mode"
                @change="handleThresholdModeChange"
              />
              <span>Custom Threshold</span>
            </label>
          </div>

          <!-- Level 3 Custom Threshold Slider -->
          <div v-if="editForm.threshold_mode === 'custom'" class="custom-thresholds">
            <div class="threshold-slider">
              <label class="threshold-label">
                Exclusive Content: {{ (editForm.exclusive_threshold * 100).toFixed(0) }}%
              </label>
              <input
                type="range"
                v-model.number="editForm.exclusive_threshold"
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
          <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">
            Save
          </button>
          <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, computed } from 'vue'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import { DEFAULT_THRESHOLDS, THRESHOLD_LIMITS } from '../constants/gameData.js'

  export default {
    name: 'NuggetCard',
    components: {
      BaseTextareaWithCharacterCounter,
    },
    props: {
      nugget: {
        type: Object,
        required: true,
      },
      characters: {
        type: Array,
        default: () => [],
      },
      currentTrustLevel: {
        type: Number,
        default: 0,
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const isEditing = ref(false)
      const editForm = reactive({
        title: '',
        character_ids: [],
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
        threshold_mode: 'default',
        privileged_threshold: DEFAULT_THRESHOLDS.privileged,
        exclusive_threshold: DEFAULT_THRESHOLDS.exclusive,
      })

      const isFormValid = computed(() => {
        const baseValid =
          editForm.title.trim() &&
          editForm.character_ids.length > 0 &&
          editForm.level_1_content.trim() &&
          editForm.level_1_content.length <= 500

        const level2Valid =
          !editForm.enable_level_2 ||
          (editForm.level_2_content.trim() && editForm.level_2_content.length <= 500)

        const level3Valid =
          !editForm.enable_level_3 ||
          (editForm.level_3_content.trim() && editForm.level_3_content.length <= 500)

        const thresholdValid =
          editForm.threshold_mode === 'default' ||
          (editForm.privileged_threshold < editForm.exclusive_threshold &&
            editForm.exclusive_threshold - editForm.privileged_threshold >= THRESHOLD_LIMITS.minGap)

        return baseValid && level2Valid && level3Valid && thresholdValid
      })

      const getCharacterName = (characterId) => {
        const character = props.characters.find((c) => c.id === characterId)
        return character ? character.name : `Character ${characterId}`
      }

      const getCharacterNames = (characterIds) => {
        if (!characterIds || characterIds.length === 0) return 'No Characters'
        if (characterIds.length === 1) return getCharacterName(characterIds[0])
        if (characterIds.length === 2)
          return `${getCharacterName(characterIds[0])} & ${getCharacterName(characterIds[1])}`
        return `${getCharacterName(characterIds[0])} & ${characterIds.length - 1} others`
      }

      const startEdit = () => {
        // Determine if nugget has custom thresholds
        const hasCustomThresholds =
          props.nugget.privileged_threshold !== null || props.nugget.exclusive_threshold !== null

        Object.assign(editForm, {
          title: props.nugget.title,
          character_ids: [...props.nugget.character_ids],
          level_1_content: props.nugget.level_1_content || '',
          level_2_content: props.nugget.level_2_content || '',
          level_3_content: props.nugget.level_3_content || '',
          enable_level_2: !!props.nugget.level_2_content,
          enable_level_3: !!props.nugget.level_3_content,
          threshold_mode: hasCustomThresholds ? 'custom' : 'default',
          privileged_threshold: props.nugget.privileged_threshold,
          exclusive_threshold: props.nugget.exclusive_threshold,
        })
        isEditing.value = true
      }

      const cancelEdit = () => {
        isEditing.value = false
      }

      const saveEdit = () => {
        if (isFormValid.value) {
          const updateData = {
            title: editForm.title.trim(),
            character_ids: editForm.character_ids.map((id) => parseInt(id)),
            level_1_content: editForm.level_1_content.trim(),
            level_2_content: editForm.enable_level_2 ? editForm.level_2_content.trim() : null,
            level_3_content: editForm.enable_level_3 ? editForm.level_3_content.trim() : null,
          }

          // Add custom thresholds if using custom mode
          if (editForm.threshold_mode === 'custom') {
            if (editForm.enable_level_2) {
              updateData.privileged_threshold = editForm.privileged_threshold
            }
            if (editForm.enable_level_3) {
              updateData.exclusive_threshold = editForm.exclusive_threshold
            }
          }

          emit('update', props.nugget.id, updateData)
          isEditing.value = false
        }
      }

      const handleLevel2Toggle = () => {
        if (!editForm.enable_level_2) {
          editForm.level_2_content = ''
        }
      }

      const handleLevel3Toggle = () => {
        if (!editForm.enable_level_3) {
          editForm.level_3_content = ''
        }
      }

      const handleThresholdModeChange = () => {
        if (editForm.threshold_mode === 'default') {
          editForm.privileged_threshold = DEFAULT_THRESHOLDS.privileged
          editForm.exclusive_threshold = DEFAULT_THRESHOLDS.exclusive
        }
      }

      const confirmDelete = () => {
        const characterNames = getCharacterNames(props.nugget.character_ids)
        if (confirm(`Are you sure you want to delete the nugget for ${characterNames}?`)) {
          emit('delete', props.nugget.id)
        }
      }

      return {
        isEditing,
        editForm,
        isFormValid,
        getCharacterName,
        getCharacterNames,
        startEdit,
        cancelEdit,
        saveEdit,
        confirmDelete,
        handleLevel2Toggle,
        handleLevel3Toggle,
        handleThresholdModeChange,
        DEFAULT_THRESHOLDS,
        THRESHOLD_LIMITS,
      }
    },
  }
</script>

<style scoped>
  .character-field,
  .content-field {
    margin-bottom: 1.5rem;
  }

  .character-selection {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    max-height: 150px;
    overflow-y: auto;
    padding: var(--spacing-lg);
    border: 2px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
  }

  .character-checkbox {
    display: flex;
    align-items: center;
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
