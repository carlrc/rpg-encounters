<template>
  <div class="shared-card">
    <div class="shared-form">
      <!-- Avatar Section -->
      <EntityAvatarSection v-model="formData.avatar" :name="formData.name" />

      <!-- Basic Fields -->
      <EntityBasicFields v-model="formData" :entity-type="entityType" :field-config="fieldConfig" />

      <!-- Text Fields -->
      <EntityTextFields
        v-model="formData"
        :entity-type="entityType"
        :field-config="textFieldConfig"
      />

      <!-- Entity-specific sections -->
      <slot name="additional-fields" :form-data="formData" :update-field="updateField" />

      <!-- Player Tags Section -->
      <div v-if="entityType === 'player'" class="shared-tags-field">
        <div class="shared-tags-input-container">
          <BaseFormField
            v-model="newTagInput"
            type="text"
            placeholder="Add tag"
            variant="compact"
            @keyup.enter="addTag"
          />
          <button @click="addTag" class="shared-btn shared-btn-success" type="button">Add</button>
        </div>
        <div class="shared-tags-edit-display">
          <span
            v-for="(tag, index) in formData.tags"
            :key="index"
            class="shared-tag-bubble editable"
          >
            {{ tag }}
            <button @click="removeTag(index)" class="shared-tag-remove-btn" type="button">×</button>
          </span>
        </div>
      </div>

      <!-- Reveal Character Selection -->
      <div v-if="entityType === 'reveal'" class="character-field">
        <label class="shared-field-label">Characters</label>
        <div class="character-selection">
          <div v-for="character in characters" :key="character.id" class="character-checkbox">
            <label class="shared-checkbox-option">
              <input type="checkbox" :value="character.id" v-model="formData.character_ids" />
              <span>{{ character.name }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Reveal Level Toggles -->
      <template v-if="entityType === 'reveal'">
        <!-- Level 2 Toggle -->
        <div class="shared-toggle">
          <label class="shared-toggle-option">
            <input type="checkbox" v-model="formData.enable_level_2" @change="handleLevel2Toggle" />
            <span>Add Level 2: Privileged Content</span>
          </label>
        </div>

        <!-- Level 3 Toggle -->
        <div class="shared-toggle">
          <label class="shared-toggle-option">
            <input type="checkbox" v-model="formData.enable_level_3" @change="handleLevel3Toggle" />
            <span>Add Level 3: Exclusive Content</span>
          </label>
        </div>

        <!-- Threshold Configuration -->
        <slot name="threshold-config" :form-data="formData" :update-field="updateField" />
      </template>

      <!-- Actions -->
      <div class="shared-actions">
        <button
          @click="handleSave"
          class="shared-btn shared-btn-success"
          :disabled="!isFormValid || isSaving"
        >
          <span v-if="isSaving">Saving...</span>
          <span v-else>Save</span>
        </button>
        <button @click="handleCancel" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, computed } from 'vue'
  import EntityAvatarSection from './EntityAvatarSection.vue'
  import EntityBasicFields from './EntityBasicFields.vue'
  import EntityTextFields from './EntityTextFields.vue'
  import BaseFormField from '../base/BaseFormField.vue'
  import { useEntityValidation } from '../../composables/useEntityValidation.js'

  export default {
    name: 'EntityCreateForm',
    components: {
      EntityAvatarSection,
      EntityBasicFields,
      EntityTextFields,
      BaseFormField,
    },
    props: {
      entityType: {
        type: String,
        required: true,
        validator: (value) => ['character', 'player', 'reveal'].includes(value.toLowerCase()),
      },
      initialData: {
        type: Object,
        default: () => ({}),
      },
      fieldConfig: {
        type: Object,
        default: () => ({}),
      },
      textFieldConfig: {
        type: Object,
        default: () => ({}),
      },
      characters: {
        type: Array,
        default: () => [],
      },
      isSaving: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['save', 'cancel'],
    setup(props, { emit }) {
      // Initialize form data based on entity type
      const getInitialFormData = () => {
        const baseData = {
          name: '',
          avatar: null,
          ...props.initialData,
        }

        switch (props.entityType.toLowerCase()) {
          case 'character':
            return {
              ...baseData,
              race: '',
              size: '',
              alignment: '',
              gender: '',
              profession: '',
              background: '',
              communication_style: '',
              motivation: '',
            }
          case 'player':
            return {
              ...baseData,
              appearance: '',
              race: '',
              class_name: '',
              size: '',
              alignment: '',
              gender: '',
              tags: [],
            }
          case 'reveal':
            return {
              ...baseData,
              title: '',
              character_ids: [],
              level_1_content: '',
              level_2_content: '',
              level_3_content: '',
              enable_level_2: false,
              enable_level_3: false,
            }
          default:
            return baseData
        }
      }

      const formData = reactive(getInitialFormData())
      const newTagInput = ref('')

      // Validation
      const { isFormValid, touchAllFields } = useEntityValidation(
        formData,
        props.entityType.toUpperCase()
      )

      // Tag management for players
      const convertToKebabCase = (text) => {
        const kebab = text.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
        return kebab.startsWith('#') ? kebab : `#${kebab}`
      }

      const addTag = () => {
        if (newTagInput.value.trim()) {
          const formattedTag = convertToKebabCase(newTagInput.value.trim())
          if (!formData.tags.includes(formattedTag)) {
            formData.tags.push(formattedTag)
          }
          newTagInput.value = ''
        }
      }

      const removeTag = (index) => {
        formData.tags.splice(index, 1)
      }

      // Reveal level toggles
      const handleLevel2Toggle = () => {
        if (!formData.enable_level_2) {
          formData.level_2_content = ''
        }
      }

      const handleLevel3Toggle = () => {
        if (!formData.enable_level_3) {
          formData.level_3_content = ''
        }
      }

      // Form actions
      const updateField = (fieldName, value) => {
        formData[fieldName] = value
      }

      const handleSave = () => {
        touchAllFields()
        if (isFormValid.value) {
          emit('save', { ...formData })
        }
      }

      const handleCancel = () => {
        emit('cancel')
      }

      return {
        formData,
        newTagInput,
        isFormValid,
        updateField,
        addTag,
        removeTag,
        handleLevel2Toggle,
        handleLevel3Toggle,
        handleSave,
        handleCancel,
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
</style>
