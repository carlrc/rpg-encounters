<template>
  <div class="shared-form">
    <!-- Title -->
    <input v-model="form.title" placeholder="Memory title" class="shared-input shared-input-name" />

    <!-- Content -->
    <div class="content-field">
      <label class="shared-field-label">Content <span class="required">*</span></label>
      <BaseTextareaWithCharacterCounter
        v-model="form.content"
        :placeholder="`Memory content (max ${gameData?.validation_limits?.memory_content || 1000} characters)`"
        :max-characters="gameData?.validation_limits?.memory_content || 1000"
      />
    </div>

    <!-- Character Selection -->
    <CharacterSelector
      v-model="form.character_ids"
      :characters="characters"
      :enable-filtering="true"
      selection-mode="checklist"
      label="Characters"
    />

    <div class="shared-actions">
      <button @click="handleSave" class="shared-btn shared-btn-success" :disabled="!isFormValid">
        {{ isEditing ? 'Save' : 'Create' }}
      </button>
      <button @click="handleCancel" class="shared-btn shared-btn-secondary">Cancel</button>
    </div>
  </div>
</template>

<script>
  import { reactive, computed } from 'vue'
  import { storeToRefs } from 'pinia'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from './entity/CharacterSelector.vue'
  import { useGameDataStore } from '../stores/gameData'

  const CONTENT_WORD_LIMIT = 200

  export default {
    name: 'MemoryForm',
    components: {
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
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

      // Initialize form with either initial data or empty values
      const form = reactive({
        title: props.initialData.title || '',
        content: props.initialData.content || '',
        character_ids: [...(props.initialData.character_ids || [])],
      })

      const isFormValid = computed(() => {
        return (
          form.title.trim().length > 0 &&
          form.content.trim().length > 0 &&
          form.character_ids.length > 0 &&
          form.content.trim().split(' ').length <= CONTENT_WORD_LIMIT
        )
      })

      // Form actions
      const handleSave = () => {
        if (isFormValid.value) {
          const formData = {
            title: form.title.trim(),
            content: form.content.trim(),
            character_ids: form.character_ids,
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
        handleSave,
        handleCancel,
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .content-field {
    margin-bottom: var(--spacing-xxl);
  }

  .required {
    color: var(--danger-color);
    font-weight: var(--font-weight-bold);
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
