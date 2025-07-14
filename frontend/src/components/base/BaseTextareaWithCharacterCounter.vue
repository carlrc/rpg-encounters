<template>
  <div class="shared-word-counter-field">
    <textarea 
      :value="modelValue"
      @input="updateValue"
      :placeholder="placeholder"
      class="shared-textarea"
    ></textarea>
    <div class="shared-word-counter" :class="{ 'over-limit': isOverLimit }">
      {{ characterCount }}/{{ maxCharacters }} characters
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'BaseTextareaWithCharacterCounter',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    maxCharacters: {
      type: Number,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const characterCount = computed(() => {
      return props.modelValue.length
    })
    
    const isOverLimit = computed(() => {
      return characterCount.value > props.maxCharacters
    })
    
    const updateValue = (event) => {
      emit('update:modelValue', event.target.value)
    }
    
    return {
      characterCount,
      isOverLimit,
      updateValue
    }
  }
}
</script>
