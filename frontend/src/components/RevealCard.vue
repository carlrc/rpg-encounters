<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="reveal-display">
      <!-- Title -->
      <h2 class="shared-title">{{ reveal.title }}</h2>

      <!-- Trust Level Display -->
      <div class="shared-field-columns">
        <div class="shared-field-column">
          <div class="shared-field">
            <div class="shared-field-label">Level 1: Public</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_1_content }}</div>
            </div>
          </div>

          <div v-if="reveal.level_2_content" class="shared-field">
            <div class="shared-field-label">Level 2: Privileged</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_2_content }}</div>
            </div>
          </div>
        </div>

        <div class="shared-field-column">
          <div v-if="reveal.level_3_content" class="shared-field">
            <div class="shared-field-label">Level 3: Exclusive</div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_3_content }}</div>
            </div>
          </div>

          <div class="shared-field">
            <div class="shared-field-label">Assigned Characters</div>
            <div class="shared-field-value">
              <div class="shared-tags-display">
                <span
                  v-for="characterId in reveal.character_ids"
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

    <div v-else class="reveal-edit">
      <!-- Edit Form -->
      <div class="shared-form">
        <!-- Title -->
        <input
          v-model="editForm.title"
          placeholder="Reveal title"
          class="shared-input shared-input-name"
        />

        <!-- Character Selection -->
        <CharacterSelector
          v-model="editForm.character_ids"
          :characters="characters"
          label="Characters"
        />

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

        <!-- Level 2 Threshold Options -->
        <div v-if="editForm.enable_level_2" class="threshold-section">
          <h4 class="threshold-title">Level 2: Privileged Content Threshold</h4>
          <div class="threshold-options">
            <label class="shared-radio-option">
              <input
                type="radio"
                value="default"
                v-model="editForm.privileged_threshold_mode"
                @change="handlePrivilegedThresholdModeChange"
              />
              <span>Use Default Threshold</span>
            </label>
            <label class="shared-radio-option">
              <input type="radio" value="custom" v-model="editForm.privileged_threshold_mode" />
              <span>Custom Threshold</span>
            </label>
          </div>

          <div v-if="editForm.privileged_threshold_mode === 'custom'" class="custom-thresholds">
            <div class="threshold-slider">
              <label class="threshold-label">
                Privileged Content:
                {{
                  DC_LABELS[editForm.privileged_threshold] || `DC ${editForm.privileged_threshold}`
                }}
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

        <!-- Level 3 Threshold Options -->
        <div v-if="editForm.enable_level_3" class="threshold-section">
          <h4 class="threshold-title">Level 3: Exclusive Content Threshold</h4>
          <div class="threshold-options">
            <label class="shared-radio-option">
              <input
                type="radio"
                value="default"
                v-model="editForm.exclusive_threshold_mode"
                @change="handleExclusiveThresholdModeChange"
              />
              <span>Use Default Threshold</span>
            </label>
            <label class="shared-radio-option">
              <input type="radio" value="custom" v-model="editForm.exclusive_threshold_mode" />
              <span>Custom Threshold</span>
            </label>
          </div>

          <div v-if="editForm.exclusive_threshold_mode === 'custom'" class="custom-thresholds">
            <div class="threshold-slider">
              <label class="threshold-label">
                Exclusive Content:
                {{
                  DC_LABELS[editForm.exclusive_threshold] || `DC ${editForm.exclusive_threshold}`
                }}
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
  import CharacterSelector from './entity/CharacterSelector.vue'
  import { useRevealValidation } from '../composables/useRevealValidation.js'
  import { DEFAULT_THRESHOLDS, THRESHOLD_LIMITS, DC_LABELS } from '../constants/gameData.js'

  export default {
    name: 'RevealCard',
    components: {
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
    },
    props: {
      reveal: {
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
        privileged_threshold_mode: 'default',
        exclusive_threshold_mode: 'default',
        privileged_threshold: DEFAULT_THRESHOLDS.privileged,
        exclusive_threshold: DEFAULT_THRESHOLDS.exclusive,
      })

      // Pass the form directly to validation since it now handles separate threshold modes
      const { isFormValid } = useRevealValidation(editForm)

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
        // Determine if reveal has custom thresholds for each level
        const hasCustomPrivilegedThreshold = props.reveal.privileged_threshold !== null
        const hasCustomExclusiveThreshold = props.reveal.exclusive_threshold !== null

        Object.assign(editForm, {
          title: props.reveal.title,
          character_ids: [...props.reveal.character_ids],
          level_1_content: props.reveal.level_1_content || '',
          level_2_content: props.reveal.level_2_content || '',
          level_3_content: props.reveal.level_3_content || '',
          enable_level_2: !!props.reveal.level_2_content,
          enable_level_3: !!props.reveal.level_3_content,
          privileged_threshold_mode: hasCustomPrivilegedThreshold ? 'custom' : 'default',
          exclusive_threshold_mode: hasCustomExclusiveThreshold ? 'custom' : 'default',
          privileged_threshold: props.reveal.privileged_threshold ?? DEFAULT_THRESHOLDS.privileged,
          exclusive_threshold: props.reveal.exclusive_threshold ?? DEFAULT_THRESHOLDS.exclusive,
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

          // Handle privileged threshold based on its mode
          if (editForm.enable_level_2 && editForm.privileged_threshold_mode === 'custom') {
            updateData.privileged_threshold = editForm.privileged_threshold
          } else {
            updateData.privileged_threshold = null
          }

          // Handle exclusive threshold based on its mode
          if (editForm.enable_level_3 && editForm.exclusive_threshold_mode === 'custom') {
            updateData.exclusive_threshold = editForm.exclusive_threshold
          } else {
            updateData.exclusive_threshold = null
          }

          emit('update', props.reveal.id, updateData)
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

      const handlePrivilegedThresholdModeChange = () => {
        if (editForm.privileged_threshold_mode === 'default') {
          editForm.privileged_threshold = DEFAULT_THRESHOLDS.privileged
        }
      }

      const handleExclusiveThresholdModeChange = () => {
        if (editForm.exclusive_threshold_mode === 'default') {
          editForm.exclusive_threshold = DEFAULT_THRESHOLDS.exclusive
        }
      }

      const confirmDelete = () => {
        const characterNames = getCharacterNames(props.reveal.character_ids)
        if (confirm(`Are you sure you want to delete the reveal for ${characterNames}?`)) {
          emit('delete', props.reveal.id)
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
  .content-field {
    margin-bottom: 1.5rem;
  }

  /* Threshold section styles using shared design tokens */
  .threshold-section {
    margin-bottom: var(--spacing-xl);
  }

  .threshold-title {
    margin: 0 0 var(--spacing-md) 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
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
