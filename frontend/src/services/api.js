import { getCurrentWorldId } from './worldState.js'

// TODO: Env vars for base urls
const API_BASE_URL = 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this._cachedWorldId = null
  }

  _getWorldIdHeader() {
    // Cache world ID to avoid repeated function calls
    const currentWorldId = getCurrentWorldId()
    if (this._cachedWorldId !== currentWorldId) {
      this._cachedWorldId = currentWorldId
    }
    return this._cachedWorldId
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'X-World-Id': this._getWorldIdHeader(),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Handle 204 No Content responses
      if (response.status === 204) {
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Player CRUD operations
  async getPlayers() {
    return this.request('/players')
  }

  async getPlayer(id) {
    return this.request(`/players/${id}`)
  }

  async createPlayer(playerData) {
    return this.request('/players', {
      method: 'POST',
      body: JSON.stringify(playerData),
    })
  }

  async updatePlayer(id, playerData) {
    return this.request(`/players/${id}`, {
      method: 'PUT',
      body: JSON.stringify(playerData),
    })
  }

  async deletePlayer(id) {
    return this.request(`/players/${id}`, {
      method: 'DELETE',
    })
  }

  // Character CRUD operations
  async getCharacters() {
    return this.request('/characters')
  }

  async getCharacter(id) {
    return this.request(`/characters/${id}`)
  }

  async createCharacter(characterData) {
    return this.request('/characters', {
      method: 'POST',
      body: JSON.stringify(characterData),
    })
  }

  async updateCharacter(id, characterData) {
    return this.request(`/characters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(characterData),
    })
  }

  async deleteCharacter(id) {
    return this.request(`/characters/${id}`, {
      method: 'DELETE',
    })
  }

  // Reveal CRUD operations
  async getReveals() {
    return this.request('/reveals')
  }

  async getReveal(id) {
    return this.request(`/reveals/${id}`)
  }

  async createReveal(revealData) {
    return this.request('/reveals', {
      method: 'POST',
      body: JSON.stringify(revealData),
    })
  }

  async updateReveal(id, revealData) {
    return this.request(`/reveals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(revealData),
    })
  }

  async deleteReveal(id) {
    return this.request(`/reveals/${id}`, {
      method: 'DELETE',
    })
  }

  // Memory CRUD operations
  async getMemories() {
    return this.request('/memories')
  }

  async getMemory(id) {
    return this.request(`/memories/${id}`)
  }

  async createMemory(memoryData) {
    return this.request('/memories', {
      method: 'POST',
      body: JSON.stringify(memoryData),
    })
  }

  async updateMemory(id, memoryData) {
    return this.request(`/memories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(memoryData),
    })
  }

  async deleteMemory(id) {
    return this.request(`/memories/${id}`, {
      method: 'DELETE',
    })
  }

  // Encounter CRUD operations
  async getEncounters() {
    return this.request('/canvas')
  }

  async getEncounter(id) {
    return this.request(`/encounters/${id}`)
  }

  async createEncounter(encounterData) {
    return this.request('/encounters', {
      method: 'POST',
      body: JSON.stringify(encounterData),
    })
  }

  async updateEncounter(id, encounterData) {
    return this.request(`/encounters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(encounterData),
    })
  }

  async deleteEncounter(id) {
    return this.request(`/encounters/${id}`, {
      method: 'DELETE',
    })
  }

  async getConversationData(encounterId, playerId, characterId) {
    return this.request(`/encounters/${encounterId}/conversation/${playerId}/${characterId}`)
  }

  // Canvas save operation
  async saveCanvas(canvasData) {
    return this.request('/canvas', {
      method: 'POST',
      body: JSON.stringify(canvasData),
    })
  }

  // Game data operations
  async getGameData() {
    return this.request('/game')
  }

  // World management operations
  async getWorlds() {
    return this.request('/worlds')
  }

  async createWorld() {
    return this.request('/worlds', {
      method: 'POST',
    })
  }

  async deleteWorld(worldId) {
    return this.request(`/worlds/${worldId}`, {
      method: 'DELETE',
    })
  }

  // Note: Influence profiles are now integrated into character model
  // Influence profile data is managed through character endpoints
}

export default new ApiService()
