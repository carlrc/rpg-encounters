<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="reveal-display">
      <!-- Title -->
      <h2 class="shared-title">{{ reveal.title }}</h2>

      <!-- Influence Level Display -->
      <div class="shared-field-columns">
        <div class="shared-field-column">
          <div class="shared-field">
            <div class="shared-field-label">
              Level 1: Standard (DC {{ getEffectiveThreshold('standard') }})
            </div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_1_content }}</div>
            </div>
          </div>

          <div v-if="reveal.level_2_content" class="shared-field">
            <div class="shared-field-label">
              Level 2: Privileged (DC {{ getEffectiveThreshold('privileged') }})
            </div>
            <div class="shared-field-value">
              <div class="shared-text-display">{{ reveal.level_2_content }}</div>
            </div>
          </div>
        </div>

        <div class="shared-field-column">
          <div v-if="reveal.level_3_content" class="shared-field">
            <div class="shared-field-label">
              Level 3: Exclusive (DC {{ getEffectiveThreshold('exclusive') }})
            </div>
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
          :enable-filtering="true"
          label="Characters"
        />

        <!-- Level 1 Content (Always Required) -->
        <div class="shared-field shared-field-full-width">
          <label class="shared-field-label">Level 1: Standard Content</label>
          <BaseTextareaWithCharacterCounter
            v-model="editForm.level_1_content"
            placeholder="Enter standard content..."
            :max-characters="500"
          />
        </div>

        <!-- Level 1 Threshold -->
        <div class="threshold-section">
          <div class="threshold-slider">
            <label class="threshold-label">
              Standard Content:
              {{ getDCLabel(editForm.standard_threshold) || `DC ${editForm.standard_threshold}` }}
            </label>
            <input
              type="range"
              v-model.number="editForm.standard_threshold"
              :min="gameData.threshold_limits.min"
              :max="gameData.threshold_limits.max"
              :step="gameData.threshold_limits.step"
              class="slider"
            />
          </div>
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
              placeholder="Enter privileged content (high influence required)..."
              :max-characters="500"
            />
          </div>
        </div>

        <!-- Level 2 Threshold -->
        <div v-if="editForm.enable_level_2" class="threshold-section">
          <div class="threshold-slider">
            <label class="threshold-label">
              Privileged Content:
              {{
                getDCLabel(editForm.privileged_threshold) || `DC ${editForm.privileged_threshold}`
              }}
            </label>
            <input
              type="range"
              v-model.number="editForm.privileged_threshold"
              :min="gameData.threshold_limits.min"
              :max="gameData.threshold_limits.max"
              :step="gameData.threshold_limits.step"
              class="slider"
            />
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
              placeholder="Enter exclusive content (maximum influence required)..."
              :max-characters="500"
            />
          </div>
        </div>

        <!-- Level 3 Threshold -->
        <div v-if="editForm.enable_level_3" class="threshold-section">
          <div class="threshold-slider">
            <label class="threshold-label">
              Exclusive Content:
              {{ getDCLabel(editForm.exclusive_threshold) || `DC ${editForm.exclusive_threshold}` }}
            </label>
            <input
              type="range"
              v-model.number="editForm.exclusive_threshold"
              :min="gameData.threshold_limits.min"
              :max="gameData.threshold_limits.max"
              :step="gameData.threshold_limits.step"
              class="slider"
            />
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
  import { useGameData } from '../composables/useGameData.js'
  import { getDCLabel } from '../utils/dcUtils.js'
  import { getCharacterName } from '../utils/characterUtils.js'

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
      currentInfluenceLevel: {
        type: Number,
        default: 0,
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const { gameData } = useGameData()
      const isEditing = ref(false)
      const editForm = reactive({
        title: '',
        character_ids: [],
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
        standard_threshold: 0, // Will be set from gameData
        privileged_threshold: 0, // Will be set from gameData
        exclusive_threshold: 0, // Will be set from gameData
      })

      // Pass the form directly to validation
      const { isFormValid } = useRevealValidation(editForm)

      const startEdit = () => {
        Object.assign(editForm, {
          title: props.reveal.title,
          character_ids: [...props.reveal.character_ids],
          level_1_content: props.reveal.level_1_content || '',
          level_2_content: props.reveal.level_2_content || '',
          level_3_content: props.reveal.level_3_content || '',
          enable_level_2: !!props.reveal.level_2_content,
          enable_level_3: !!props.reveal.level_3_content,
          standard_threshold: props.reveal.standard_threshold,
          privileged_threshold: props.reveal.privileged_threshold,
          exclusive_threshold: props.reveal.exclusive_threshold,
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
            character_ids: editForm.character_ids,
            level_1_content: editForm.level_1_content.trim(),
            level_2_content: editForm.enable_level_2 ? editForm.level_2_content.trim() : null,
            level_3_content: editForm.enable_level_3 ? editForm.level_3_content.trim() : null,
          }

          // Always include all thresholds since we always show sliders
          updateData.standard_threshold = editForm.standard_threshold
          updateData.privileged_threshold = editForm.enable_level_2
            ? editForm.privileged_threshold
            : null
          updateData.exclusive_threshold = editForm.enable_level_3
            ? editForm.exclusive_threshold
            : null

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

      const confirmDelete = () => {
        if (confirm(`Are you sure you want to delete this reveal?`)) {
          emit('delete', props.reveal.id)
        }
      }

      const getEffectiveThreshold = (level) => {
        switch (level) {
          case 'standard':
            return props.reveal.standard_threshold
          case 'privileged':
            return props.reveal.privileged_threshold
          case 'exclusive':
            return props.reveal.exclusive_threshold
          default:
            return 0
        }
      }

      return {
        gameData,
        isEditing,
        editForm,
        isFormValid,
        getCharacterName: (id) => getCharacterName(id, props.characters),
        startEdit,
        cancelEdit,
        saveEdit,
        confirmDelete,
        handleLevel2Toggle,
        handleLevel3Toggle,
        getEffectiveThreshold,
        getDCLabel: (value) => getDCLabel(value, gameData.value?.difficulty_classes),
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
