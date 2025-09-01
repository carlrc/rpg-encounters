import { createEntityStore } from '@/composables/useEntityStore'
import * as api from '@/services/api'

export const useRevealStore = createEntityStore('Reveal', {
  getAll: api.getReveals,
  getOne: api.getReveal,
  create: api.createReveal,
  update: api.updateReveal,
  delete: api.deleteReveal,
})
