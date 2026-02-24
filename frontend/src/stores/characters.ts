import { createEntityStore } from '../composables/useEntityStore'
import * as api from '../services/api'

export const useCharacterStore = createEntityStore('Character', {
  getAll: api.getCharacters,
  getOne: api.getCharacter,
  create: api.createCharacter,
  update: api.updateCharacter,
  delete: api.deleteCharacter,
})
