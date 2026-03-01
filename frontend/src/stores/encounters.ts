import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'
import type { CreateEncounterRequest, Encounter, UpdateEncounterRequest } from '../types'

export const useEncounterStore = createEntityStore<
  Encounter,
  CreateEncounterRequest,
  UpdateEncounterRequest
>('Encounter', {
  getAll: async () => (await api.getEncounters()).encounters,
  getOne: api.getEncounter,
  create: api.createEncounter,
  update: api.updateEncounter,
  delete: api.deleteEncounter,
})
