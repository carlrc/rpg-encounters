import { ref, computed } from 'vue'

export function useWordCounter(initialText = '', maxWords = 0) {
    const text = ref(initialText)

    const wordCount = computed(() => {
        return text.value.trim() ? text.value.trim().split(/\s+/).length : 0
    })

    const isOverLimit = computed(() => {
        return maxWords > 0 && wordCount.value > maxWords
    })

    const updateText = (newText) => {
        text.value = newText
    }

    const reset = () => {
        text.value = ''
    }

    return {
        text,
        wordCount,
        isOverLimit,
        updateText,
        reset
    }
}
