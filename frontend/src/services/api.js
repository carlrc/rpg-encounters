import { http } from './http.js'
import { useWorldStore } from '@/stores/world'

// Player CRUD operations
export const getPlayers = () => http.get('/players')
export const getPlayer = (id) => http.get(`/players/${id}`)
export const createPlayer = (playerData) => http.post('/players', playerData)
export const updatePlayer = (id, playerData) => http.put(`/players/${id}`, playerData)
export const deletePlayer = (id) => http.delete(`/players/${id}`)

// Character CRUD operations
export const getCharacters = () => http.get('/characters')
export const getCharacter = (id) => http.get(`/characters/${id}`)
export const createCharacter = (characterData) => http.post('/characters', characterData)
export const updateCharacter = (id, characterData) => http.put(`/characters/${id}`, characterData)
export const deleteCharacter = (id) => http.delete(`/characters/${id}`)

// Reveal CRUD operations
export const getReveals = () => http.get('/reveals')
export const getReveal = (id) => http.get(`/reveals/${id}`)
export const createReveal = (revealData) => http.post('/reveals', revealData)
export const updateReveal = (id, revealData) => http.put(`/reveals/${id}`, revealData)
export const deleteReveal = (id) => http.delete(`/reveals/${id}`)

// Memory CRUD operations
export const getMemories = () => http.get('/memories')
export const getMemory = (id) => http.get(`/memories/${id}`)
export const createMemory = (memoryData) => http.post('/memories', memoryData)
export const updateMemory = (id, memoryData) => http.put(`/memories/${id}`, memoryData)
export const deleteMemory = (id) => http.delete(`/memories/${id}`)

// Encounter CRUD operations
export const getEncounters = () => http.get('/canvas')
export const getEncounter = (id) => http.get(`/encounters/${id}`)
export const createEncounter = (encounterData) => http.post('/encounters', encounterData)
export const updateEncounter = (id, encounterData) => http.put(`/encounters/${id}`, encounterData)
export const deleteEncounter = (id) => http.delete(`/encounters/${id}`)

// Other operations
export const getConversationData = (encounterId, playerId, characterId) =>
  http.get(`/encounters/${encounterId}/conversation/${playerId}/${characterId}`)
export const saveCanvas = (canvasData) => http.post('/canvas', canvasData)
export const getGameData = () => http.get('/game')
export const getWorlds = () => http.get('/worlds')
export const createWorld = () => http.post('/worlds')
export const deleteWorld = (worldId) => http.delete(`/worlds/${worldId}`)

// Voice operations
export const searchVoices = (searchTerm, pageToken = null) => {
  const params = new URLSearchParams({ search_term: searchTerm })
  if (pageToken) params.append('next_page_token', pageToken)
  return http.get(`/voices/search?${params}`)
}

export const getVoiceSample = async (voiceId) => {
  const worldStore = useWorldStore()
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/voices/${voiceId}/sample`,
    {
      headers: {
        'X-World-Id': worldStore.currentWorldId,
      },
    }
  )

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response
}

// Utility function for backward compatibility
export const getAllVoices = async () => {
  // Use broad search terms to get all available voices
  // We'll search for common vowels which should match most voice names
  const response = await searchVoices('a')
  return response.voices || []
}
