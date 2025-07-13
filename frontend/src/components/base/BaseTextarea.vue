<template>
  <div class="shared-word-counter-field">
    <textarea 
      :value="modelValue"
      @input="updateValue"
      :placeholder="placeholder"
      class="shared-textarea"
    ></textarea>
    <div class="shared-word-counter" :class="{ 'over-limit': isOverLimit }">
      {{ wordCount }}/{{ maxWords }} words
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'BaseTextarea',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    maxWords: {
      type: Number,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const wordCount = computed(() => {
      return props.modelValue.trim() ? props.modelValue.trim().split(/\s+/).length : 0
    })
    
    const isOverLimit = computed(() => {
      return wordCount.value > props.maxWords
    })
    
    const updateValue = (event) => {
      emit('update:modelValue', event.target.value)
    }
    
    return {
      wordCount,
      isOverLimit,
      updateValue
    }
  }
}
</script>
