import { ref, computed } from 'vue'

export function useCharacterCounter(initialText = '', maxCharacters = 0) {
  const text = ref(initialText)

  const characterCount = computed(() => {
    return text.value.length
  })

  const isOverLimit = computed(() => {
    return maxCharacters > 0 && characterCount.value > maxCharacters
  })

  const remainingCharacters = computed(() => {
    return maxCharacters > 0 ? maxCharacters - characterCount.value : 0
  })

  const updateText = (newText) => {
    text.value = newText
  }

  const reset = () => {
    text.value = ''
  }

  return {
    text,
    characterCount,
    isOverLimit,
    remainingCharacters,
    updateText,
    reset,
  }
}
