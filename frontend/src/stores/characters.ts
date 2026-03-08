import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'
import type { Character, CreateCharacterRequest, UpdateCharacterRequest } from '../types'

export const useCharacterStore = createEntityStore<
  Character,
  CreateCharacterRequest,
  UpdateCharacterRequest
>('Character', {
  getAll: api.getCharacters,
  getOne: api.getCharacter,
  create: api.createCharacter,
  update: api.updateCharacter,
  delete: api.deleteCharacter,
})
