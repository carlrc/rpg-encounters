import { http } from './http'
import type {
  CreateCharacterRequest,
  CreateCharacterResponse,
  CreateEncounterRequest,
  CreateEncounterResponse,
  CreateMemoryRequest,
  CreateMemoryResponse,
  CreatePlayerLoginLinkResponse,
  CreatePlayerRequest,
  CreatePlayerResponse,
  CreateRevealRequest,
  CreateRevealResponse,
  CreateWorldResponse,
  GetCanvasResponse,
  GetCharacterResponse,
  GetCharactersResponse,
  GetConversationDataResponse,
  GetEncounterResponse,
  GetGameDataResponse,
  GetMemoriesResponse,
  GetMemoryResponse,
  GetPlayerEncounterResponse,
  GetPlayerResponse,
  GetPlayersResponse,
  GetProfileResponse,
  GetRevealResponse,
  GetRevealsResponse,
  GetTTSProvidersResponse,
  GetWorldsResponse,
  RequestMagicLinkRequest,
  SaveCanvasResponse,
  SaveCanvasRequest,
  SearchVoicesResponse,
  UpdateCharacterRequest,
  UpdateEncounterRequest,
  UpdateMemoryRequest,
  UpdatePlayerRequest,
  UpdateRevealRequest,
  UpdateCharacterResponse,
  UpdateEncounterResponse,
  UpdateMemoryResponse,
  UpdatePlayerResponse,
  UpdateRevealResponse,
} from '../types'

// Player CRUD operations
export const getPlayers = () => http.get<GetPlayersResponse>('/players')
export const getPlayer = (id: number) => http.get<GetPlayerResponse>(`/players/${id}`)
export const createPlayer = (playerData: CreatePlayerRequest) =>
  http.post<CreatePlayerResponse>('/players', playerData)
export const updatePlayer = (id: number, playerData: UpdatePlayerRequest) =>
  http.put<UpdatePlayerResponse>(`/players/${id}`, playerData)
export const deletePlayer = (id: number) => http.delete<null>(`/players/${id}`)

// Player login operations
export const createPlayerLoginLink = (playerId: number) =>
  http.post<CreatePlayerLoginLinkResponse>(`/players/${playerId}/login`)
export const getPlayerEncounter = (playerId: number) =>
  http.get<GetPlayerEncounterResponse>(`/players/${playerId}/encounter`)

// Character CRUD operations
export const getCharacters = () => http.get<GetCharactersResponse>('/characters')
export const getCharacter = (id: number) => http.get<GetCharacterResponse>(`/characters/${id}`)
export const createCharacter = (characterData: CreateCharacterRequest) =>
  http.post<CreateCharacterResponse>('/characters', characterData)
export const updateCharacter = (id: number, characterData: UpdateCharacterRequest) =>
  http.put<UpdateCharacterResponse>(`/characters/${id}`, characterData)
export const deleteCharacter = (id: number) => http.delete<null>(`/characters/${id}`)

// Reveal CRUD operations
export const getReveals = () => http.get<GetRevealsResponse>('/reveals')
export const getReveal = (id: number) => http.get<GetRevealResponse>(`/reveals/${id}`)
export const createReveal = (revealData: CreateRevealRequest) =>
  http.post<CreateRevealResponse>('/reveals', revealData)
export const updateReveal = (id: number, revealData: UpdateRevealRequest) =>
  http.put<UpdateRevealResponse>(`/reveals/${id}`, revealData)
export const deleteReveal = (id: number) => http.delete<null>(`/reveals/${id}`)

// Memory CRUD operations
export const getMemories = () => http.get<GetMemoriesResponse>('/memories')
export const getMemory = (id: number) => http.get<GetMemoryResponse>(`/memories/${id}`)
export const createMemory = (memoryData: CreateMemoryRequest) =>
  http.post<CreateMemoryResponse>('/memories', memoryData)
export const updateMemory = (id: number, memoryData: UpdateMemoryRequest) =>
  http.put<UpdateMemoryResponse>(`/memories/${id}`, memoryData)
export const deleteMemory = (id: number) => http.delete<null>(`/memories/${id}`)

// Encounter CRUD operations
export const getEncounters = () => http.get<GetCanvasResponse>('/canvas')
export const getEncounter = (id: number) => http.get<GetEncounterResponse>(`/encounters/${id}`)
export const createEncounter = (encounterData: CreateEncounterRequest) =>
  http.post<CreateEncounterResponse>('/encounters', encounterData)
export const updateEncounter = (id: number, encounterData: UpdateEncounterRequest) =>
  http.put<UpdateEncounterResponse>(`/encounters/${id}`, encounterData)
export const deleteEncounter = (id: number) => http.delete<null>(`/encounters/${id}`)

// Other operations
export const getConversationData = (encounterId: number, playerId: number, characterId: number) =>
  http.get<GetConversationDataResponse>(
    `/encounters/${encounterId}/conversation/${playerId}/${characterId}`
  )
export const deleteConversationHistory = (
  encounterId: number,
  playerId: number,
  characterId: number
) => http.delete<null>(`/encounters/${encounterId}/conversation/${playerId}/${characterId}`)
export const saveCanvas = (canvasData: SaveCanvasRequest) =>
  http.post<SaveCanvasResponse>('/canvas', canvasData)
export const getGameData = () => http.get<GetGameDataResponse>('/game')
export const getWorlds = () => http.get<GetWorldsResponse>('/worlds')
export const createWorld = () => http.post<CreateWorldResponse>('/worlds')
export const deleteWorld = (worldId: number) => http.delete<null>(`/worlds/${worldId}`)
export const getProfile = () => http.get<GetProfileResponse>('/profile')

// Voice operations
export const getTTSProviders = () => http.get<GetTTSProvidersResponse>('/voices/tts_providers')

export const searchVoices = (
  searchTerm: string,
  ttsProvider: string,
  pageToken: string | null = null
) => {
  const params = new URLSearchParams({
    search_term: searchTerm,
    tts_provider: ttsProvider,
  })
  if (pageToken) params.append('next_page_token', pageToken)
  return http.get<SearchVoicesResponse>(`/voices/search?${params}`)
}

export const getVoiceSample = async (voiceId: string, ttsProvider: string): Promise<Response> => {
  const response = await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/voices/${voiceId}/sample?tts_provider=${ttsProvider}`,
    {
      credentials: 'include',
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
  const { useWorldStore } = await import('../stores/world')
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
export const checkAuth = async (): Promise<boolean> => {
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/check`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
    },
  })

  return res.ok
}

export const requestMagicLink = async (email: string) => {
  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/request`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
    },
    body: JSON.stringify({ email } satisfies RequestMagicLinkRequest),
  })

  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }

  if (res.status === 204) return null
  return res.json()
}
export const consumeMagicLink = async (token: string): Promise<Response> => {
  // Use direct fetch to avoid world store access (this is only called from AuthCallbackPage)
  return await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/auth?token=${encodeURIComponent(token)}`,
    {
      method: 'GET',
      credentials: 'include',
    }
  )
}
export const logout = () => http.post<null>('/auth/logout')

// Player auth operations - separate from DM auth to avoid breaking existing flows
export const consumePlayerLogin = async (playerId: number, token: string): Promise<Response> => {
  // Use direct fetch for player login consumption
  return await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/players/${playerId}/login?token=${encodeURIComponent(token)}`,
    {
      method: 'GET',
      credentials: 'include',
    }
  )
}
