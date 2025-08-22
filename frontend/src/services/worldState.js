import { ref } from 'vue'

// Reactive global variable for current world ID
const currentWorldId = ref(1)

export function setCurrentWorldId(id) {
  currentWorldId.value = id
}

export function getCurrentWorldIdRef() {
  return currentWorldId
}

// For backward compatibility and non-reactive access
export function getCurrentWorldId() {
  return currentWorldId.value
}
