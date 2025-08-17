<template>
  <div class="textarea-with-counter">
    <textarea
      :value="modelValue"
      @input="handleInput"
      :placeholder="placeholder"
      class="shared-textarea"
      :class="{ 'over-limit': isOverLimit }"
    />
    <div class="counter" :class="{ 'over-limit': isOverLimit }">
      {{ currentCount }}/{{ maxCount }} {{ counterType }}
    </div>
  </div>
</template>

<script>
  import { computed } from 'vue'

  export default {
    name: 'BaseTextareaWithCounter',
    props: {
      modelValue: {
        type: String,
        default: '',
      },
      placeholder: {
        type: String,
        default: '',
      },
      maxCount: {
        type: Number,
        required: true,
        validator: (value) => value > 0,
      },
      counterType: {
        type: String,
        default: 'characters',
        validator: (value) => ['characters', 'words'].includes(value),
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const currentCount = computed(() => {
        if (!props.modelValue) return 0

        if (props.counterType === 'words') {
          return props.modelValue
            .trim()
            .split(/\s+/)
            .filter((w) => w.length > 0).length
        }
        return props.modelValue.length
      })

      const isOverLimit = computed(() => currentCount.value > props.maxCount)

      const handleInput = (event) => {
        emit('update:modelValue', event.target.value)
      }

      return {
        currentCount,
        isOverLimit,
        handleInput,
      }
    },
  }
</script>

<style scoped>
  .textarea-with-counter {
    position: relative;
    width: 100%;
  }

  .shared-textarea {
    width: 100%;
    box-sizing: border-box;
    padding-bottom: 2.5rem; /* Make room for counter */
    min-height: 100px;
    resize: vertical;
  }

  .shared-textarea.over-limit {
    border-color: var(--danger-color);
    background-color: rgba(220, 53, 69, 0.05);
  }

  .shared-textarea.over-limit:focus {
    box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
  }

  .counter {
    position: absolute;
    bottom: var(--spacing-sm);
    right: var(--spacing-sm);
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.95);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-xl);
    font-weight: var(--font-weight-semibold);
    border: 1px solid var(--border-default);
    pointer-events: none;
  }

  .counter.over-limit {
    color: var(--danger-color);
    background: rgba(220, 53, 69, 0.1);
    border-color: var(--danger-color);
  }
</style>
