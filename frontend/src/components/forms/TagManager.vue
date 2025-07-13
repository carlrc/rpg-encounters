<template>
  <div class="shared-tags-field">
    <div class="shared-tags-input-container">
      <input 
        v-model="newTagInput"
        placeholder="Add tag"
        class="shared-input shared-tag-input"
        @keyup.enter="addTag"
      />
      <button @click="addTag" class="shared-btn shared-btn-success" type="button">Add</button>
    </div>
    <div class="shared-tags-edit-display">
      <span 
        v-for="(tag, index) in modelValue" 
        :key="index" 
        class="shared-tag-bubble editable"
      >
        {{ tag }}
        <button @click="removeTag(index)" class="shared-tag-remove-btn" type="button">×</button>
      </span>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'TagManager',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const newTagInput = ref('')
    
    const convertToKebabCase = (text) => {
      const kebab = text.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
      return kebab.startsWith('#') ? kebab : `#${kebab}`
    }
    
    const addTag = () => {
      if (newTagInput.value.trim()) {
        const formattedTag = convertToKebabCase(newTagInput.value.trim())
        if (!props.modelValue.includes(formattedTag)) {
          const updatedTags = [...props.modelValue, formattedTag]
          emit('update:modelValue', updatedTags)
        }
        newTagInput.value = ''
      }
    }
    
    const removeTag = (index) => {
      const updatedTags = props.modelValue.filter((_, i) => i !== index)
      emit('update:modelValue', updatedTags)
    }
    
    return {
      newTagInput,
      addTag,
      removeTag
    }
  }
}
</script>
