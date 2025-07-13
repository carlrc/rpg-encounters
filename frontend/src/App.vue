<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">Player page</h1>
        <div class="header-actions">
          <input 
            ref="fileInput"
            type="file" 
            accept=".md,.markdown" 
            @change="handleImportFile"
            style="display: none"
          />
          <button 
            @click="$refs.fileInput.click()" 
            class="import-btn"
            :disabled="importing"
          >
            <span v-if="importing">Importing...</span>
            <span v-else>Import Players</span>
          </button>
        </div>
      </div>
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
        <!-- Success Toast -->
        <div v-if="successMessage" class="success-toast">
          {{ successMessage }}
        </div>
        
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
              <select v-model="createForm.size" class="edit-select">
                <option value="">Select Size</option>
                <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
              </select>
              <select v-model="createForm.alignment" class="edit-select">
                <option value="">Select Alignment</option>
                <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
              </select>
              <div class="tags-field">
                <div class="tags-input-container">
                  <input 
                    v-model="newCreateTagInput"
                    placeholder="Add tag"
                    class="edit-input tag-input"
                    @keyup.enter="addCreateTag"
                  />
                  <button @click="addCreateTag" class="add-tag-btn" type="button">Add</button>
                </div>
                <div class="tags-edit-display">
                  <span 
                    v-for="(tag, index) in createForm.tags" 
                    :key="index" 
                    class="tag-bubble editable"
                  >
                    {{ tag }}
                    <button @click="removeCreateTag(index)" class="remove-tag-btn" type="button">×</button>
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
    const newCreateTagInput = ref('')
    const createWordCount = ref(0)
    const importing = ref(false)
    const successMessage = ref('')
    
    const createForm = reactive({
      name: '',
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: '',
      tags: []
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

    const sizes = [
      'Small', 'Medium'
    ]

    const alignments = [
      'Lawful Good', 'Neutral Good', 'Chaotic Good',
      'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
      'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
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
             createForm.size &&
             createForm.alignment &&
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

    const addCreateTag = () => {
      if (newCreateTagInput.value.trim()) {
        const formattedTag = convertToKebabCase(newCreateTagInput.value.trim())
        if (!createForm.tags.includes(formattedTag)) {
          createForm.tags.push(formattedTag)
        }
        newCreateTagInput.value = ''
      }
    }

    const removeCreateTag = (index) => {
      createForm.tags.splice(index, 1)
    }

    const cancelCreate = () => {
      showCreateForm.value = false
      createForm.name = ''
      createForm.appearance = ''
      createForm.race = ''
      createForm.class_name = ''
      createForm.size = ''
      createForm.alignment = ''
      createForm.tags = []
      newCreateTagInput.value = ''
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
            size: createForm.size,
            alignment: createForm.alignment,
            tags: createForm.tags
          })
          players.value.push(newPlayer)
          cancelCreate() // Reset form and hide it
        } catch (err) {
          error.value = 'Failed to create player'
          console.error('Error creating player:', err)
        }
      }
    }

    // Import functionality
    const handleImportFile = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      try {
        importing.value = true
        error.value = ''
        
        const content = await readFileContent(file)
        const parsedPlayers = parseMarkdownPlayers(content)
        
        if (parsedPlayers.length === 0) {
          error.value = 'No valid players found in the markdown file'
          return
        }

        await importPlayersFromMarkdown(parsedPlayers)
        
        // Reset file input
        event.target.value = ''
        
      } catch (err) {
        error.value = `Import failed: ${err.message}`
        console.error('Import error:', err)
      } finally {
        importing.value = false
      }
    }

    const readFileContent = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => resolve(e.target.result)
        reader.onerror = (e) => reject(new Error('Failed to read file'))
        reader.readAsText(file)
      })
    }

    const parseMarkdownPlayers = (content) => {
      const players = []
      
      // Split by main headers (# or ## followed by any text)
      const sections = content.split(/^#\s+/m).filter(section => section.trim())
      
      for (const section of sections) {
        try {
          const player = parsePlayerSection(section)
          if (player) {
            players.push(player)
          }
        } catch (err) {
          console.warn('Failed to parse player section:', err.message)
        }
      }
      
      return players
    }

    const parsePlayerSection = (section) => {
      const lines = section.split('\n')
      const player = {
        name: '',
        appearance: '',
        race: '',
        class_name: '',
        size: '',
        alignment: '',
        tags: []
      }

      let currentField = null
      let currentContent = []

      for (const line of lines) {
        const trimmedLine = line.trim()
        
        // Check for field headers
        if (trimmedLine.match(/^##\s*name/i)) {
          currentField = 'name'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*appearance/i)) {
          currentField = 'appearance'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*race/i)) {
          currentField = 'race'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*class/i)) {
          currentField = 'class_name'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*size/i)) {
          currentField = 'size'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*alignment/i)) {
          currentField = 'alignment'
          currentContent = []
        } else if (trimmedLine.match(/^##\s*(tags|groups)/i)) {
          currentField = 'tags'
          currentContent = []
        } else if (trimmedLine.startsWith('##')) {
          // Unknown field, stop processing current field
          currentField = null
          currentContent = []
        } else if (currentField && trimmedLine) {
          // Add content to current field
          if (currentField === 'tags') {
            // Parse bullet points for tags
            if (trimmedLine.match(/^[-*]\s+(.+)/)) {
              const tagName = trimmedLine.replace(/^[-*]\s+/, '').trim()
              if (tagName) {
                currentContent.push(tagName)
              }
            }
          } else {
            currentContent.push(trimmedLine)
          }
        } else if (currentField && currentContent.length > 0) {
          // End of field content, save it
          if (currentField === 'tags') {
            player[currentField] = currentContent
          } else {
            player[currentField] = currentContent.join(' ').trim()
          }
          currentField = null
          currentContent = []
        }
      }

      // Handle any remaining content
      if (currentField && currentContent.length > 0) {
        if (currentField === 'tags') {
          player[currentField] = currentContent
        } else {
          player[currentField] = currentContent.join(' ').trim()
        }
      }

      // Validate required fields - size and alignment are now required
      if (!player.name || !player.appearance || !player.race || !player.class_name || !player.size || !player.alignment) {
        throw new Error(`Missing required fields for player: ${player.name || 'Unknown'}`)
      }

      return player
    }

    const importPlayersFromMarkdown = async (parsedPlayers) => {
      let successCount = 0
      const errors = []

      for (const playerData of parsedPlayers) {
        try {
          const newPlayer = await apiService.createPlayer(playerData)
          players.value.push(newPlayer)
          successCount++
        } catch (err) {
          // Extract more detailed error information
          let errorMessage = `Failed to create ${playerData.name || 'Unknown Player'}`
          
          if (err.response && err.response.data) {
            // Handle API validation errors
            if (err.response.data.detail) {
              if (Array.isArray(err.response.data.detail)) {
                // Pydantic validation errors
                const validationErrors = err.response.data.detail.map(detail => {
                  const field = detail.loc ? detail.loc.join('.') : 'unknown field'
                  return `${field}: ${detail.msg}`
                }).join(', ')
                errorMessage += ` - Validation errors: ${validationErrors}`
              } else {
                errorMessage += ` - ${err.response.data.detail}`
              }
            } else {
              errorMessage += ` - ${JSON.stringify(err.response.data)}`
            }
          } else if (err.message) {
            errorMessage += ` - ${err.message}`
          } else {
            errorMessage += ' - Unknown error occurred'
          }
          
          errors.push(errorMessage)
          console.error(`Failed to create player ${playerData.name}:`, err)
        }
      }

      // Show results with detailed error information
      if (successCount > 0) {
        const message = `Successfully imported ${successCount} player${successCount > 1 ? 's' : ''}`
        if (errors.length > 0) {
          error.value = `${message}. However, ${errors.length} player${errors.length > 1 ? 's' : ''} failed to import:\n\n${errors.join('\n\n')}`
        } else {
          // Show success toast briefly then clear
          successMessage.value = message
          setTimeout(() => {
            successMessage.value = ''
          }, 1500)
        }
      } else {
        error.value = `Import failed - no players were successfully imported:\n\n${errors.join('\n\n')}`
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
      successMessage,
      showCreateForm,
      createForm,
      newCreateTagInput,
      createWordCount,
      importing,
      races,
      classes,
      sizes,
      alignments,
      isCreateFormValid,
      setActiveTab,
      updatePlayer,
      deletePlayer,
      startCreate,
      updateCreateWordCount,
      addCreateTag,
      removeCreateTag,
      cancelCreate,
      saveCreate,
      handleImportFile
    }
  }
}
</script>

<style scoped>
/* Header Styles */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.import-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  min-width: 140px;
}

.import-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.import-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.success-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
  font-size: 0.9em;
  font-weight: 600;
  z-index: 1000;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1em;
}

.error {
  text-align: left;
  padding: 20px;
  color: #dc3545;
  font-size: 0.95em;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin: 20px;
  white-space: pre-line;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
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

.player-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
  align-items: start;
}

/* Ensure all cards in grid have consistent alignment */
.player-cards-grid > * {
  align-self: start;
}

/* Create card styling only - PlayerCard component handles its own styling */
.player-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e9ea;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.player-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}
</style>
