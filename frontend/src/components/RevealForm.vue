<template>
  <div class="shared-form">
    <!-- Title -->
    <input v-model="form.title" placeholder="Reveal title" class="shared-input shared-input-name" />

    <!-- Character Selection -->
    <CharacterSelector
      v-model="form.character_ids"
      :characters="characters"
      :enable-filtering="true"
      selection-mode="checklist"
      label="Characters"
    />

    <!-- Level 1 Content (Always Required) -->
    <div class="shared-field shared-field-full-width">
      <label class="shared-field-label"
        >Level 1: Standard Content <span class="required">*</span></label
      >
      <BaseTextareaWithCharacterCounter
        v-model="form.level_1_content"
        placeholder="Enter standard content..."
        :max-characters="500"
      />
    </div>

    <!-- Level 1 Threshold -->
    <div class="threshold-section">
      <RangeSliderControl
        v-model="form.standard_threshold"
        label="Standard Content"
        :min="gameData?.threshold_limits?.min || 5"
        :max="gameData?.threshold_limits?.max || 25"
        :step="gameData?.threshold_limits?.step || 1"
        :formatter="(value) => getDCLabel(value) || `DC ${value}`"
      />
    </div>

    <!-- Level 2 Content -->
    <div class="shared-field shared-field-full-width">
      <div class="level-toggle level-toggle-in-divider">
        <label class="level-toggle-option">
          <input type="checkbox" v-model="form.enable_level_2" @change="handleLevel2Toggle" />
          <span>Add Level 2: Privileged Content</span>
        </label>
      </div>

      <div v-if="form.enable_level_2">
        <label class="shared-field-label">Level 2: Privileged Content</label>
        <BaseTextareaWithCharacterCounter
          v-model="form.level_2_content"
          placeholder="Enter privileged content (high influence required)..."
          :max-characters="500"
        />
      </div>
    </div>

    <!-- Level 2 Threshold -->
    <div v-if="form.enable_level_2" class="threshold-section">
      <RangeSliderControl
        v-model="form.privileged_threshold"
        label="Privileged Content"
        :min="gameData?.threshold_limits?.min || 5"
        :max="gameData?.threshold_limits?.max || 25"
        :step="gameData?.threshold_limits?.step || 1"
        :formatter="(value) => getDCLabel(value) || `DC ${value}`"
      />
    </div>

    <!-- Level 3 Content -->
    <div class="shared-field shared-field-full-width">
      <div class="level-toggle level-toggle-in-divider">
        <label class="level-toggle-option">
          <input type="checkbox" v-model="form.enable_level_3" @change="handleLevel3Toggle" />
          <span>Add Level 3: Exclusive Content</span>
        </label>
      </div>

      <div v-if="form.enable_level_3">
        <label class="shared-field-label">Level 3: Exclusive Content</label>
        <BaseTextareaWithCharacterCounter
          v-model="form.level_3_content"
          placeholder="Enter exclusive content (maximum influence required)..."
          :max-characters="500"
        />
      </div>
    </div>

    <!-- Level 3 Threshold -->
    <div v-if="form.enable_level_3" class="threshold-section">
      <RangeSliderControl
        v-model="form.exclusive_threshold"
        label="Exclusive Content"
        :min="gameData?.threshold_limits?.min || 5"
        :max="gameData?.threshold_limits?.max || 25"
        :step="gameData?.threshold_limits?.step || 1"
        :formatter="(value) => getDCLabel(value) || `DC ${value}`"
      />
    </div>

    <!-- Actions -->
    <div class="shared-actions">
      <button @click="handleSave" class="shared-btn shared-btn-success" :disabled="!isFormValid">
        {{ isEditing ? 'Save' : 'Create' }}
      </button>
      <button @click="handleCancel" class="shared-btn shared-btn-secondary">Cancel</button>
    </div>
  </div>
</template>

<script>
  import { reactive } from 'vue'
  import { storeToRefs } from 'pinia'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from './entity/CharacterSelector.vue'
  import RangeSliderControl from './base/RangeSliderControl.vue'
  import { useRevealValidation } from '../composables/useRevealValidation'
  import { useGameDataStore } from '../stores/gameData'
  import { getDCLabel } from '../utils/dcUtils'

  export default {
    name: 'RevealForm',
    components: {
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
      RangeSliderControl,
    },
    props: {
      initialData: {
        type: Object,
        default: () => ({}),
      },
      characters: {
        type: Array,
        default: () => [],
      },
      isEditing: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['save', 'cancel'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)

      const form = reactive({
        title: props.initialData.title || '',
        character_ids: [...(props.initialData.character_ids || [])],
        level_1_content: props.initialData.level_1_content || '',
        level_2_content: props.initialData.level_2_content || '',
        level_3_content: props.initialData.level_3_content || '',
        enable_level_2: !!props.initialData.level_2_content,
        enable_level_3: !!props.initialData.level_3_content,
        standard_threshold:
          props.initialData.standard_threshold ||
          gameData.value?.default_thresholds?.standard ||
          10,
        privileged_threshold:
          props.initialData.privileged_threshold ||
          gameData.value?.default_thresholds?.privileged ||
          15,
        exclusive_threshold:
          props.initialData.exclusive_threshold ||
          gameData.value?.default_thresholds?.exclusive ||
          20,
      })

      const { isFormValid } = useRevealValidation(form)

      const handleLevel2Toggle = () => {
        if (!form.enable_level_2) {
          form.level_2_content = ''
        }
      }

      const handleLevel3Toggle = () => {
        if (!form.enable_level_3) {
          form.level_3_content = ''
        }
      }

      const handleSave = () => {
        if (isFormValid.value) {
          const formData = {
            title: form.title.trim(),
            character_ids: form.character_ids.map((id) => parseInt(id)),
            level_1_content: form.level_1_content.trim(),
            standard_threshold: form.standard_threshold,
          }

          if (form.enable_level_2) {
            formData.level_2_content = form.level_2_content.trim()
            formData.privileged_threshold = form.privileged_threshold
          }
          if (form.enable_level_3) {
            formData.level_3_content = form.level_3_content.trim()
            formData.exclusive_threshold = form.exclusive_threshold
          }

          emit('save', formData)
        }
      }

      const handleCancel = () => {
        emit('cancel')
      }

      return {
        form,
        gameData,
        isFormValid,
        handleLevel2Toggle,
        handleLevel3Toggle,
        handleSave,
        handleCancel,
        getDCLabel: (value) => getDCLabel(value, gameData.value?.difficulty_classes),
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .required {
    color: var(--danger-color);
    font-weight: var(--font-weight-bold);
  }

  /* Level toggle styles */
  .level-toggle {
    margin-bottom: var(--spacing-lg);
  }

  .level-toggle-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    padding: var(--spacing-md);
    border: 2px solid var(--border-dashed);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
    transition: all var(--transition-fast);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
  }

  .level-toggle-option:hover {
    border-color: var(--primary-color);
    background: #e3f2fd;
  }

  .level-toggle-option input[type='checkbox'] {
    margin: 0;
    transform: scale(1.1);
  }

  /* Level divider toggle styles */
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
