import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'
import type { CreateMemoryRequest, Memory, UpdateMemoryRequest } from '../types'

export const useMemoryStore = createEntityStore<Memory, CreateMemoryRequest, UpdateMemoryRequest>(
  'Memory',
  {
    getAll: api.getMemories,
    getOne: api.getMemory,
    create: api.createMemory,
    update: api.updateMemory,
    delete: api.deleteMemory,
  }
)
