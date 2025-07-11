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
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
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

    onMounted(() => {
      loadPlayers()
    })

    return {
      activeTab,
      navigationTabs,
      players,
      loading,
      error,
      setActiveTab,
      updatePlayer,
      deletePlayer
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
</style>
