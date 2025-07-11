<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header">
      <h1 class="page-title">Player page</h1>
    </header>

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left Sidebar Navigation -->
      <nav class="sidebar">
        <button 
          v-for="tab in navigationTabs" 
          :key="tab.id"
          :class="['nav-button', { active: activeTab === tab.id }]"
          @click="setActiveTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </nav>

      <!-- Main Content Area -->
      <main class="content-area">
        <div v-if="loading" class="loading">Loading players...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="player-cards-grid">
          <PlayerCard
            v-for="player in players"
            :key="player.id"
            :player="player"
            @update="updatePlayer"
            @delete="deletePlayer"
          />
          
          <!-- Create Player Card -->
          <div class="player-card">
            <div v-if="!showCreateForm" class="create-player-button" @click="startCreate">
              <div class="plus-icon">+</div>
              <p class="create-text">Add New Player</p>
            </div>
            
            <div v-else class="player-edit-form">
              <input 
                v-model="createForm.name" 
                placeholder="Player name"
                class="edit-input"
              />
              <textarea 
                v-model="createForm.description" 
                placeholder="Player description"
                class="edit-textarea"
              ></textarea>
              <div class="edit-actions">
                <button @click="cancelCreate" class="cancel-btn">Cancel</button>
                <button @click="saveCreate" class="save-btn">Save</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import PlayerCard from './components/PlayerCard.vue'
import apiService from './services/api.js'

export default {
  name: 'App',
  components: {
    PlayerCard
  },
  setup() {
    const activeTab = ref('players')
    const players = ref([])
    const loading = ref(false)
    const error = ref('')
    const showCreateForm = ref(false)
    const createForm = reactive({
      name: '',
      description: ''
    })
    
    const navigationTabs = [
      { id: 'players', label: 'Players' },
      { id: 'characters', label: 'Characters' },
      { id: 'lorebooks', label: 'Lorebooks' },
      { id: 'encounters', label: 'Encounters' }
    ]

    const setActiveTab = (tabId) => {
      activeTab.value = tabId
    }

    const loadPlayers = async () => {
      loading.value = true
      error.value = ''
      try {
        players.value = await apiService.getPlayers()
      } catch (err) {
        error.value = 'Failed to load players. Make sure the backend is running.'
        console.error('Error loading players:', err)
      } finally {
        loading.value = false
      }
    }

    const updatePlayer = async (playerId, playerData) => {
      try {
        const updatedPlayer = await apiService.updatePlayer(playerId, playerData)
        const index = players.value.findIndex(p => p.id === playerId)
        if (index !== -1) {
          players.value[index] = updatedPlayer
        }
      } catch (err) {
        error.value = 'Failed to update player'
        console.error('Error updating player:', err)
      }
    }

    const deletePlayer = async (playerId) => {
      try {
        await apiService.deletePlayer(playerId)
        players.value = players.value.filter(p => p.id !== playerId)
      } catch (err) {
        error.value = 'Failed to delete player'
        console.error('Error deleting player:', err)
      }
    }

    const startCreate = () => {
      showCreateForm.value = true
    }

    const cancelCreate = () => {
      showCreateForm.value = false
      createForm.name = ''
      createForm.description = ''
    }

    const saveCreate = async () => {
      if (createForm.name.trim() && createForm.description.trim()) {
        try {
          const newPlayer = await apiService.createPlayer({
            name: createForm.name.trim(),
            description: createForm.description.trim()
          })
          players.value.push(newPlayer)
          cancelCreate() // Reset form and hide it
        } catch (err) {
          error.value = 'Failed to create player'
          console.error('Error creating player:', err)
        }
      }
    }

    onMounted(() => {
      loadPlayers()
    })

    return {
      activeTab,
      navigationTabs,
      players,
      loading,
      error,
      showCreateForm,
      createForm,
      setActiveTab,
      updatePlayer,
      deletePlayer,
      startCreate,
      cancelCreate,
      saveCreate
    }
  }
}
</script>

<style scoped>
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1em;
}

.error {
  text-align: center;
  padding: 40px;
  color: #dc3545;
  font-size: 1.1em;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin: 20px;
}

/* Create Player Card Styles */
.create-player-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 120px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.create-player-button:hover {
  color: #007bff;
}

.plus-icon {
  font-size: 3em;
  font-weight: bold;
  margin-bottom: 8px;
}

.create-text {
  margin: 0;
  font-size: 0.9em;
}

/* Reuse PlayerCard styles for consistency */
.player-edit-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-input, .edit-textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.edit-textarea {
  min-height: 60px;
  resize: vertical;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn, .save-btn, .cancel-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.save-btn:hover {
  background-color: #218838;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}
</style>
