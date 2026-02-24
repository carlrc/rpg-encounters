import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'

export const usePlayerStore = createEntityStore('Player', {
  getAll: api.getPlayers,
  getOne: api.getPlayer,
  create: api.createPlayer,
  update: api.updatePlayer,
  delete: api.deletePlayer,
})
