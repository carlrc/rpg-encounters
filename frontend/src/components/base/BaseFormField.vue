<template>
  <div class="base-form-field" :class="fieldClasses">
    <label v-if="label" class="shared-field-label" :for="fieldId">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>

    <div class="field-wrapper">
      <!-- Input Field -->
      <input
        v-if="type === 'text' || type === 'email' || type === 'password'"
        :id="fieldId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :class="inputClasses"
        :disabled="disabled"
        @input="handleInput"
        @blur="handleBlur"
      />

      <!-- Textarea Field -->
      <textarea
        v-else-if="type === 'textarea'"
        :id="fieldId"
        :value="modelValue"
        :placeholder="placeholder"
        :class="textareaClasses"
        :disabled="disabled"
        @input="handleInput"
        @blur="handleBlur"
      ></textarea>

      <!-- Select Field -->
      <select
        v-else-if="type === 'select'"
        :id="fieldId"
        :value="modelValue"
        :class="selectClasses"
        :disabled="disabled"
        @change="handleInput"
        @blur="handleBlur"
      >
        <option value="" v-if="placeholder">{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="typeof option === 'object' ? option.value : option"
          :value="typeof option === 'object' ? option.value : option"
        >
          {{ typeof option === 'object' ? option.label : option }}
        </option>
      </select>

      <!-- Character/Word Counter -->
      <div
        v-if="showCounter && (type === 'textarea' || maxLength)"
        class="shared-word-counter"
        :class="{ 'over-limit': isOverLimit }"
      >
        {{ counterText }}
      </div>
    </div>

    <!-- Error Messages -->
    <div v-if="errors.length > 0" class="field-errors">
      <div v-for="error in errors" :key="error" class="field-error">
        {{ error }}
      </div>
    </div>

    <!-- Help Text -->
    <div v-if="helpText" class="field-help">
      {{ helpText }}
    </div>
  </div>
</template>

<script>
  import { computed, ref } from 'vue'

  export default {
    name: 'BaseFormField',
    props: {
      modelValue: {
        type: [String, Number],
        default: '',
      },
      type: {
        type: String,
        default: 'text',
        validator: (value) => ['text', 'email', 'password', 'textarea', 'select'].includes(value),
      },
      label: {
        type: String,
        default: '',
      },
      placeholder: {
        type: String,
        default: '',
      },
      required: {
        type: Boolean,
        default: false,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
      errors: {
        type: Array,
        default: () => [],
      },
      helpText: {
        type: String,
        default: '',
      },
      options: {
        type: Array,
        default: () => [],
      },
      maxLength: {
        type: Number,
        default: null,
      },
      maxWords: {
        type: Number,
        default: null,
      },
      showCounter: {
        type: Boolean,
        default: false,
      },
      variant: {
        type: String,
        default: 'default',
        validator: (value) => ['default', 'name', 'compact'].includes(value),
      },
      fullWidth: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['update:modelValue', 'blur'],
    setup(props, { emit }) {
      const fieldId = ref(`field-${Math.random().toString(36).substr(2, 9)}`)

      const fieldClasses = computed(() => ({
        'field-full-width': props.fullWidth,
        'field-has-errors': props.errors.length > 0,
        'field-disabled': props.disabled,
        [`field-variant-${props.variant}`]: true,
      }))

      const inputClasses = computed(() => [
        'shared-input',
        {
          'shared-input-name': props.variant === 'name',
          'field-error': props.errors.length > 0,
        },
      ])

      const textareaClasses = computed(() => [
        'shared-textarea',
        {
          'field-error': props.errors.length > 0,
        },
      ])

      const selectClasses = computed(() => [
        'shared-select',
        {
          'field-error': props.errors.length > 0,
        },
      ])

      const characterCount = computed(() => {
        return props.modelValue ? props.modelValue.toString().length : 0
      })

      const wordCount = computed(() => {
        if (!props.modelValue) return 0
        return props.modelValue
          .toString()
          .trim()
          .split(/\s+/)
          .filter((word) => word.length > 0).length
      })

      const isOverLimit = computed(() => {
        if (props.maxLength && characterCount.value > props.maxLength) return true
        if (props.maxWords && wordCount.value > props.maxWords) return true
        return false
      })

      const counterText = computed(() => {
        if (props.maxWords) {
          return `${wordCount.value}/${props.maxWords} words`
        }
        if (props.maxLength) {
          return `${characterCount.value}/${props.maxLength} characters`
        }
        return `${characterCount.value} characters`
      })

      const handleInput = (event) => {
        emit('update:modelValue', event.target.value)
      }

      const handleBlur = (event) => {
        emit('blur', event)
      }

      return {
        fieldId,
        fieldClasses,
        inputClasses,
        textareaClasses,
        selectClasses,
        characterCount,
        wordCount,
        isOverLimit,
        counterText,
        handleInput,
        handleBlur,
      }
    },
  }
</script>

<style scoped>
  .base-form-field {
    margin-bottom: var(--spacing-lg);
  }

  .field-wrapper {
    position: relative;
  }

  .field-full-width {
    width: 100%;
  }

  .field-error {
    border-color: var(--danger-color) !important;
  }

  .field-errors {
    margin-top: var(--spacing-xs);
  }

  .field-error {
    color: var(--danger-color);
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-xs);
  }

  .field-error:last-child {
    margin-bottom: 0;
  }

  .field-help {
    color: var(--text-muted);
    font-size: var(--font-size-sm);
    margin-top: var(--spacing-xs);
  }

  .required {
    color: var(--danger-color);
    font-weight: var(--font-weight-bold);
  }

  .field-disabled {
    opacity: 0.6;
  }

  .field-variant-compact .shared-field-label {
    font-size: var(--font-size-sm);
    margin-bottom: var(--spacing-xs);
  }

  /* Counter positioning for textarea */
  .field-wrapper:has(.shared-textarea) {
    position: relative;
  }

  .field-wrapper .shared-word-counter {
    position: absolute;
    bottom: var(--spacing-sm);
    right: var(--spacing-sm);
  }
</style>
