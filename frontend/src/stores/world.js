import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWorldStore = defineStore('world', () => {
  const currentWorldId = ref(1)

  const setCurrentWorldId = (id) => {
    currentWorldId.value = id
  }

  return {
    currentWorldId,
    setCurrentWorldId,
  }
})
