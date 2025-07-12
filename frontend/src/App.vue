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
              <div class="appearance-field">
                <textarea 
                  v-model="createForm.appearance" 
                  placeholder="Player appearance"
                  class="edit-textarea"
                  @input="updateCreateWordCount"
                ></textarea>
                <div class="word-counter" :class="{ 'over-limit': createWordCount > 40 }">
                  {{ createWordCount }}/40 words
                </div>
              </div>
              <select v-model="createForm.race" class="edit-select">
                <option value="">Select Race</option>
                <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
              </select>
              <select v-model="createForm.class_name" class="edit-select">
                <option value="">Select Class</option>
                <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">{{ playerClass }}</option>
              </select>
              <div class="groups-field">
                <div class="groups-input-container">
                  <input 
                    v-model="newCreateGroupInput"
                    placeholder="Add group"
                    class="edit-input group-input"
                    @keyup.enter="addCreateGroup"
                  />
                  <button @click="addCreateGroup" class="add-group-btn" type="button">Add</button>
                </div>
                <div class="groups-edit-display">
                  <span 
                    v-for="(group, index) in createForm.groups" 
                    :key="index" 
                    class="group-bubble editable"
                  >
                    {{ group }}
                    <button @click="removeCreateGroup(index)" class="remove-group-btn" type="button">×</button>
                  </span>
                </div>
              </div>
              <div class="edit-actions">
                <button @click="cancelCreate" class="cancel-btn">Cancel</button>
                <button @click="saveCreate" class="save-btn" :disabled="!isCreateFormValid">Save</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed } from 'vue'
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
    const newCreateGroupInput = ref('')
    const createWordCount = ref(0)
    
    const createForm = reactive({
      name: '',
      appearance: '',
      race: '',
      class_name: '',
      groups: []
    })

    const races = [
      'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
      'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
    ]

    const classes = [
      'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 
      'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 
      'Warlock', 'Wizard'
    ]
    
    const navigationTabs = [
      { id: 'players', label: 'Players' },
      { id: 'characters', label: 'Characters' },
      { id: 'lorebooks', label: 'Lorebooks' },
      { id: 'encounters', label: 'Encounters' }
    ]

    const isCreateFormValid = computed(() => {
      return createForm.name.trim() && 
             createForm.appearance.trim() && 
             createForm.race && 
             createForm.class_name &&
             createWordCount.value <= 40
    })

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

    const updateCreateWordCount = () => {
      createWordCount.value = createForm.appearance.trim() ? createForm.appearance.trim().split(/\s+/).length : 0
    }

    const convertToKebabCase = (text) => {
      const kebab = text.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
      return kebab.startsWith('#') ? kebab : `#${kebab}`
    }

    const addCreateGroup = () => {
      if (newCreateGroupInput.value.trim()) {
        const formattedGroup = convertToKebabCase(newCreateGroupInput.value.trim())
        if (!createForm.groups.includes(formattedGroup)) {
          createForm.groups.push(formattedGroup)
        }
        newCreateGroupInput.value = ''
      }
    }

    const removeCreateGroup = (index) => {
      createForm.groups.splice(index, 1)
    }

    const cancelCreate = () => {
      showCreateForm.value = false
      createForm.name = ''
      createForm.appearance = ''
      createForm.race = ''
      createForm.class_name = ''
      createForm.groups = []
      newCreateGroupInput.value = ''
      createWordCount.value = 0
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          const newPlayer = await apiService.createPlayer({
            name: createForm.name.trim(),
            appearance: createForm.appearance.trim(),
            race: createForm.race,
            class_name: createForm.class_name,
            groups: createForm.groups
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
      newCreateGroupInput,
      createWordCount,
      races,
      classes,
      isCreateFormValid,
      setActiveTab,
      updatePlayer,
      deletePlayer,
      startCreate,
      updateCreateWordCount,
      addCreateGroup,
      removeCreateGroup,
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

.edit-input, .edit-textarea, .edit-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  transition: border-color 0.2s;
}

.edit-input:focus, .edit-textarea:focus, .edit-select:focus {
  outline: none;
  border-color: #007bff;
}

.edit-textarea {
  min-height: 60px;
  resize: vertical;
}

.appearance-field {
  position: relative;
}

.word-counter {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 0.8em;
  color: #666;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 3px;
}

.word-counter.over-limit {
  color: #dc3545;
  font-weight: bold;
}

.groups-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.groups-input-container {
  display: flex;
  gap: 8px;
}

.group-input {
  flex: 1;
}

.add-group-btn {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.add-group-btn:hover {
  background-color: #218838;
}

.groups-edit-display {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 30px;
  align-items: flex-start;
}

.group-bubble {
  background-color: #007bff;
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: 500;
}

.group-bubble.editable {
  background-color: #6c757d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remove-group-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.remove-group-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
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
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
  font-weight: 600;
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.save-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  color: white;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.3);
  font-weight: 600;
}

.cancel-btn:hover {
  background: linear-gradient(135deg, #5a6268, #495057);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108, 117, 125, 0.4);
}
</style>
