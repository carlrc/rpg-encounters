import { ref } from 'vue'

// Reactive global variable for current world ID
const currentWorldId = ref(1)

export const setCurrentWorldId = (id) => {
  currentWorldId.value = id
}

export const getCurrentWorldIdRef = () => {
  return currentWorldId
}

// For backward compatibility and non-reactive access
export const getCurrentWorldId = () => {
  return currentWorldId.value
}
