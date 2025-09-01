import { createEntityStore } from '@/composables/useEntityStore'
import * as api from '@/services/api'

export const useEncounterStore = createEntityStore('Encounter', {
  getAll: api.getEncounters,
  getOne: api.getEncounter,
  create: api.createEncounter,
  update: api.updateEncounter,
  delete: api.deleteEncounter,
})
