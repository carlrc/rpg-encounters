import { http } from './http.js'

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
export const searchVoices = (searchTerm, ttsProvider, pageToken = null) => {
  const params = new URLSearchParams({
    search_term: searchTerm,
    tts_provider: ttsProvider,
  })
  if (pageToken) params.append('next_page_token', pageToken)
  return http.get(`/voices/search?${params}`)
}

export const getVoiceSample = async (voiceId, ttsProvider) => {
  // Use the http client which already includes world ID headers
  const response = await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/voices/${voiceId}/sample?tts_provider=${ttsProvider}`,
    {
      headers: {
        'X-World-Id': await getCurrentWorldIdFromStore(),
      },
    }
  )

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response
}

// Helper function to get world ID without circular dependency
const getCurrentWorldIdFromStore = async () => {
  const { useWorldStore } = await import('@/stores/world')
  const worldStore = useWorldStore()
  return worldStore.currentWorldId
}

// Utility function for backward compatibility
export const getAllVoices = async (ttsProvider = 'google') => {
  // Force english voices for now
  const response = await searchVoices('en', ttsProvider)
  return response.voices || []
}

// Auth operations - use fetch directly to avoid world store dependency
export const checkAuth = async () => {
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/check`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
    },
  })

  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }

  return res.json()
}

export const requestMagicLink = async (email) => {
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/request`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
    },
    body: JSON.stringify({ email }),
  })

  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }

  if (res.status === 204) return null
  return res.json()
}
export const consumeMagicLink = async (token) => {
  // Use direct fetch to avoid world store access (this is only called from AuthCallbackPage)
  return await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/auth?token=${encodeURIComponent(token)}`,
    {
      method: 'GET',
      credentials: 'include',
    }
  )
}
export const logout = () => http.post('/auth/logout')
