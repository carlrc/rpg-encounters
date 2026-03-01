import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'
import type { CreatePlayerRequest, Player, UpdatePlayerRequest } from '../types'

export const usePlayerStore = createEntityStore<Player, CreatePlayerRequest, UpdatePlayerRequest>(
  'Player',
  {
    getAll: api.getPlayers,
    getOne: api.getPlayer,
    create: api.createPlayer,
    update: api.updatePlayer,
    delete: api.deletePlayer,
  }
)
