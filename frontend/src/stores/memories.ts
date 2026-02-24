import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'

export const useMemoryStore = createEntityStore('Memory', {
  getAll: api.getMemories,
  getOne: api.getMemory,
  create: api.createMemory,
  update: api.updateMemory,
  delete: api.deleteMemory,
})
