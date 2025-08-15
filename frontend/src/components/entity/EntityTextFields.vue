<template>
  <div class="entity-text-fields">
    <!-- Background Field (Characters only) -->
    <BaseFormField
      v-if="showField('background')"
      v-model="localData.background"
      type="textarea"
      label="Background"
      :placeholder="`Character background (max ${limits.background} characters)`"
      :max-length="limits.background"
      show-counter
      full-width
      @update:modelValue="updateField('background', $event)"
    />

    <!-- Communication Style Field (Characters only) -->
    <BaseFormField
      v-if="showField('communication_style')"
      v-model="localData.communication_style"
      type="textarea"
      label="Communication Style"
      :placeholder="`Communication style (max ${limits.communication_style} characters)`"
      :max-length="limits.communication_style"
      show-counter
      full-width
      @update:modelValue="updateField('communication_style', $event)"
    />

    <!-- Motivation Field (Characters only) -->
    <BaseFormField
      v-if="showField('motivation')"
      v-model="localData.motivation"
      type="textarea"
      label="Motivation"
      :placeholder="`Character motivation (max ${limits.motivation} characters)`"
      :max-length="limits.motivation"
      show-counter
      full-width
      @update:modelValue="updateField('motivation', $event)"
    />

    <!-- Appearance Field (Players only) -->
    <BaseFormField
      v-if="showField('appearance')"
      v-model="localData.appearance"
      type="textarea"
      label="Appearance"
      :placeholder="`Player appearance (max ${limits.appearance} words)`"
      :max-words="limits.appearance"
      show-counter
      full-width
      @update:modelValue="updateField('appearance', $event)"
    />

    <!-- Level Content Fields (Reveals only) -->
    <template v-if="entityType === 'reveal'">
      <!-- Level 1 Content (Always Required) -->
      <BaseFormField
        v-model="localData.level_1_content"
        type="textarea"
        label="Level 1: Standard Content"
        placeholder="Enter standard content (always accessible)..."
        :max-length="500"
        show-counter
        required
        full-width
        @update:modelValue="updateField('level_1_content', $event)"
      />

      <!-- Level 2 Content -->
      <div v-if="localData.enable_level_2" class="level-content-section">
        <BaseFormField
          v-model="localData.level_2_content"
          type="textarea"
          label="Level 2: Privileged Content"
          placeholder="Enter privileged content (high influence required)..."
          :max-length="500"
          show-counter
          full-width
          @update:modelValue="updateField('level_2_content', $event)"
        />
      </div>

      <!-- Level 3 Content -->
      <div v-if="localData.enable_level_3" class="level-content-section">
        <BaseFormField
          v-model="localData.level_3_content"
          type="textarea"
          label="Level 3: Exclusive Content"
          placeholder="Enter exclusive content (maximum influence required)..."
          :max-length="500"
          show-counter
          full-width
          @update:modelValue="updateField('level_3_content', $event)"
        />
      </div>
    </template>
  </div>
</template>

<script>
  import { reactive, computed, watch } from 'vue'
  import BaseFormField from '../base/BaseFormField.vue'
  import { useGameData } from '../../composables/useGameData.js'

  export default {
    name: 'EntityTextFields',
    components: {
      BaseFormField,
    },
    props: {
      modelValue: {
        type: Object,
        required: true,
      },
      entityType: {
        type: String,
        required: true,
        validator: (value) => ['character', 'player', 'reveal'].includes(value.toLowerCase()),
      },
      fieldConfig: {
        type: Object,
        default: () => ({}),
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const { gameData } = useGameData()

      // Local reactive copy of the data
      const localData = reactive({
        background: '',
        communication_style: '',
        motivation: '',
        appearance: '',
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
        ...props.modelValue,
      })

      // Field limits based on entity type
      const limits = computed(() => {
        switch (props.entityType.toLowerCase()) {
          case 'character':
            return {
              background: gameData.value.validation_limits.character_background,
              communication_style: gameData.value.validation_limits.character_communication,
              motivation: gameData.value.validation_limits.character_motivation,
            }
          case 'player':
            return {
              appearance: gameData.value.validation_limits.player_appearance, // This is in words
            }
          case 'reveal':
            return {
              level_1_content: 500,
              level_2_content: 500,
              level_3_content: 500,
            }
          default:
            return {}
        }
      })

      // Default field configurations for different entity types
      const defaultFieldConfigs = {
        character: {
          background: { show: true },
          communication_style: { show: true },
          motivation: { show: true },
          appearance: { show: false },
        },
        player: {
          appearance: { show: true },
          background: { show: false },
          communication_style: { show: false },
          motivation: { show: false },
        },
        reveal: {
          level_1_content: { show: true },
          level_2_content: { show: true },
          level_3_content: { show: true },
        },
      }

      const fieldConfig = computed(() => ({
        ...defaultFieldConfigs[props.entityType.toLowerCase()],
        ...props.fieldConfig,
      }))

      const showField = (fieldName) => {
        const config = fieldConfig.value[fieldName]
        return config?.show !== false
      }

      const updateField = (fieldName, value) => {
        localData[fieldName] = value
        emit('update:modelValue', { ...localData })
      }

      // Watch for external changes to modelValue
      watch(
        () => props.modelValue,
        (newValue) => {
          Object.assign(localData, newValue)
        },
        { deep: true }
      )

      return {
        gameData,
        localData,
        limits,
        fieldConfig,
        showField,
        updateField,
      }
    },
  }
</script>

<style scoped>
  .entity-text-fields {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .level-content-section {
    border-top: 2px solid var(--border-default);
    padding-top: var(--spacing-lg);
    margin-top: var(--spacing-lg);
  }
</style>
