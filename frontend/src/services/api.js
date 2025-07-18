const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle 204 No Content responses
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Player CRUD operations
    async getPlayers() {
        return this.request('/players');
    }

    async getPlayer(id) {
        return this.request(`/players/${id}`);
    }

    async createPlayer(playerData) {
        return this.request('/players', {
            method: 'POST',
            body: JSON.stringify(playerData),
        });
    }

    async updatePlayer(id, playerData) {
        return this.request(`/players/${id}`, {
            method: 'PUT',
            body: JSON.stringify(playerData),
        });
    }

    async deletePlayer(id) {
        return this.request(`/players/${id}`, {
            method: 'DELETE',
        });
    }

    // Character CRUD operations
    async getCharacters() {
        return this.request('/characters');
    }

    async getCharacter(id) {
        return this.request(`/characters/${id}`);
    }

    async createCharacter(characterData) {
        return this.request('/characters', {
            method: 'POST',
            body: JSON.stringify(characterData),
        });
    }

    async updateCharacter(id, characterData) {
        return this.request(`/characters/${id}`, {
            method: 'PUT',
            body: JSON.stringify(characterData),
        });
    }

    async deleteCharacter(id) {
        return this.request(`/characters/${id}`, {
            method: 'DELETE',
        });
    }

    // Nugget CRUD operations
    async getNuggets() {
        return this.request('/trust/nuggets');
    }

    async getNugget(id) {
        return this.request(`/trust/nuggets/${id}`);
    }

    async createNugget(nuggetData) {
        return this.request('/trust/nuggets', {
            method: 'POST',
            body: JSON.stringify(nuggetData),
        });
    }

    async updateNugget(id, nuggetData) {
        return this.request(`/trust/nuggets/${id}`, {
            method: 'PUT',
            body: JSON.stringify(nuggetData),
        });
    }

    async deleteNugget(id) {
        return this.request(`/trust/nuggets/${id}`, {
            method: 'DELETE',
        });
    }

    // Trust Profile CRUD operations
    async getTrustProfile(characterId) {
        return this.request(`/trust/profiles/${characterId}`);
    }

    async createTrustProfile(trustProfileData) {
        return this.request('/trust/profiles', {
            method: 'POST',
            body: JSON.stringify(trustProfileData),
        });
    }

    async updateTrustProfile(characterId, trustProfileData) {
        return this.request(`/trust/profiles/${characterId}`, {
            method: 'PUT',
            body: JSON.stringify(trustProfileData),
        });
    }

    async deleteTrustProfile(characterId) {
        return this.request(`/trust/profiles/${characterId}`, {
            method: 'DELETE',
        });
    }
}

export default new ApiService();
