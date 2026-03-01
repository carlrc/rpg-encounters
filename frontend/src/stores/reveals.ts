import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'
import type { CreateRevealRequest, Reveal, UpdateRevealRequest } from '../types'

export const useRevealStore = createEntityStore<Reveal, CreateRevealRequest, UpdateRevealRequest>(
  'Reveal',
  {
    getAll: api.getReveals,
    getOne: api.getReveal,
    create: api.createReveal,
    update: api.updateReveal,
    delete: api.deleteReveal,
  }
)
