import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWorldStore = defineStore('world', () => {
  const currentWorldId = ref(null)

  const setCurrentWorldId = (id) => {
    currentWorldId.value = id
  }

  return {
    currentWorldId,
    setCurrentWorldId,
  }
})
