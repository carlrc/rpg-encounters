<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ getPageTitle(activeTab) }}</h1>
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
        
        <div v-if="loading" class="loading">Loading {{ activeTab === 'characters' ? 'characters' : 'players' }}...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        
        <!-- Players Tab Content -->
        <div v-else-if="activeTab === 'players'" class="players-split-view">
          <!-- Left Pane - Player List -->
          <div class="player-list-pane">
            <div class="player-list-header">
              <h3>Players</h3>
            </div>
            
            <div class="player-list-content">
              <div 
                v-for="player in players" 
                :key="player.id"
                :class="['player-list-item', { active: selectedPlayerId === player.id }]"
                @click="selectPlayer(player.id)"
              >
                {{ player.name }}
              </div>
              
              <div v-if="players.length === 0" class="empty-state">
                No players yet
              </div>
            </div>
            
            <div class="player-list-footer">
              <button @click="startCreate" class="add-player-btn">
                <span class="plus-icon">+</span>
                Add Player
              </button>
              
              <input 
                ref="playerFileInput"
                type="file" 
                accept=".md,.markdown,.json" 
                @change="handleImportFile"
                style="display: none"
              />
              <button 
                @click="$refs.playerFileInput.click()" 
                class="import-players-btn"
                :disabled="importing"
              >
                <span v-if="importing">Importing...</span>
                <span v-else>Import Players</span>
              </button>
            </div>
          </div>
          
          <!-- Right Pane - Player Detail -->
          <div class="player-detail-pane">
            <div v-if="!selectedPlayer && !showCreateForm" class="empty-detail-state">
              <div class="empty-icon">👤</div>
              <h3>No Player Selected</h3>
              <p>Select a player from the list to view details, or create a new one.</p>
            </div>
            
            <div v-else-if="showCreateForm" class="shared-card">
              <div class="shared-form">
                <!-- Avatar Upload -->
                <div class="shared-avatar-edit-section">
                  <div class="shared-avatar-container">
                    <img v-if="createForm.avatar" :src="createForm.avatar" :alt="createForm.name" class="shared-avatar-image" />
                    <div v-else class="shared-avatar-placeholder">
                      <span class="shared-avatar-initials">{{ getInitials(createForm.name) }}</span>
                    </div>
                  </div>
                  <input 
                    ref="playerAvatarInput"
                    type="file" 
                    accept="image/*" 
                    @change="handlePlayerAvatarUpload"
                    style="display: none"
                  />
                  <button @click="$refs.playerAvatarInput.click()" class="shared-avatar-btn shared-avatar-upload-btn">
                    {{ createForm.avatar ? 'Change Avatar' : 'Add Avatar' }}
                  </button>
                  <button v-if="createForm.avatar" @click="removePlayerAvatar" class="shared-avatar-btn shared-avatar-remove-btn">
                    Remove
                  </button>
                </div>
                
                <!-- Name -->
                <input 
                  v-model="createForm.name" 
                  placeholder="Player name"
                  class="shared-input shared-input-name"
                />
                
                <!-- Two Column Layout for Create -->
                <div class="shared-field-columns">
                  <!-- Left Column -->
                  <div class="shared-field-column">
                    <select v-model="createForm.race" class="shared-select">
                      <option value="">Select Race</option>
                      <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
                    </select>
                    
                    <select v-model="createForm.class_name" class="shared-select">
                      <option value="">Select Class</option>
                      <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">{{ playerClass }}</option>
                    </select>
                    
                    <div class="shared-word-counter-field">
                      <textarea 
                        v-model="createForm.appearance" 
                        placeholder="Player appearance (max 40 words)"
                        class="shared-textarea"
                        @input="updateCreateWordCount"
                      ></textarea>
                      <div class="shared-word-counter" :class="{ 'over-limit': createWordCount > 40 }">
                        {{ createWordCount }}/40 words
                      </div>
                    </div>
                  </div>
                  
                  <!-- Right Column -->
                  <div class="shared-field-column">
                    <select v-model="createForm.size" class="shared-select">
                      <option value="">Select Size</option>
                      <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
                    </select>
                    
                    <select v-model="createForm.alignment" class="shared-select">
                      <option value="">Select Alignment</option>
                      <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
                    </select>
                  </div>
                </div>
                
                <!-- Tags Section -->
                <div class="shared-tags-field">
                  <div class="shared-tags-input-container">
                    <input 
                      v-model="newCreateTagInput"
                      placeholder="Add tag"
                      class="shared-input shared-tag-input"
                      @keyup.enter="addCreateTag"
                    />
                    <button @click="addCreateTag" class="shared-btn shared-btn-success" type="button">Add</button>
                  </div>
                  <div class="shared-tags-edit-display">
                    <span 
                      v-for="(tag, index) in createForm.tags" 
                      :key="index" 
                      class="shared-tag-bubble editable"
                    >
                      {{ tag }}
                      <button @click="removeCreateTag(index)" class="shared-tag-remove-btn" type="button">×</button>
                    </span>
                  </div>
                </div>
                
                <div class="shared-actions">
                  <button @click="saveCreate" class="shared-btn shared-btn-success" :disabled="!isCreateFormValid">Save</button>
                  <button @click="cancelCreate" class="shared-btn shared-btn-secondary">Cancel</button>
                </div>
              </div>
            </div>
            
            <PlayerCard
              v-else-if="selectedPlayer"
              :player="selectedPlayer"
              @update="updatePlayer"
              @delete="deletePlayer"
            />
          </div>
        </div>
        
        <!-- Characters Tab Content -->
        <div v-else-if="activeTab === 'characters'" class="characters-split-view">
          <!-- Left Pane - Character List -->
          <div class="character-list-pane">
            <div class="character-list-header">
              <h3>Characters</h3>
            </div>
            
            <div class="character-list-content">
              <div 
                v-for="character in characters" 
                :key="character.id"
                :class="['character-list-item', { active: selectedCharacterId === character.id }]"
                @click="selectCharacter(character.id)"
              >
                {{ character.name }}
              </div>
              
              <div v-if="characters.length === 0" class="empty-state">
                No characters yet
              </div>
            </div>
            
            <div class="character-list-footer">
              <button @click="startCreateCharacter" class="add-character-btn">
                <span class="plus-icon">+</span>
                Add Character
              </button>
              
              <input 
                ref="characterFileInput"
                type="file" 
                accept=".md,.markdown,.json" 
                @change="handleImportFile"
                style="display: none"
              />
              <button 
                @click="$refs.characterFileInput.click()" 
                class="import-characters-btn"
                :disabled="importing"
              >
                <span v-if="importing">Importing...</span>
                <span v-else>Import Characters</span>
              </button>
            </div>
          </div>
          
          <!-- Right Pane - Character Detail -->
          <div class="character-detail-pane">
            <div v-if="!selectedCharacter && !showCreateCharacterForm" class="empty-detail-state">
              <div class="empty-icon">👤</div>
              <h3>No Character Selected</h3>
              <p>Select a character from the list to view details, or create a new one.</p>
            </div>
            
            <div v-else-if="showCreateCharacterForm" class="shared-card">
              <div class="shared-form">
                <!-- Avatar Upload -->
                <div class="shared-avatar-edit-section">
                  <div class="shared-avatar-container">
                    <img v-if="createCharacterForm.avatar" :src="createCharacterForm.avatar" :alt="createCharacterForm.name" class="shared-avatar-image" />
                    <div v-else class="shared-avatar-placeholder">
                      <span class="shared-avatar-initials">{{ getInitials(createCharacterForm.name) }}</span>
                    </div>
                  </div>
                  <input 
                    ref="avatarInput"
                    type="file" 
                    accept="image/*" 
                    @change="handleAvatarUpload"
                    style="display: none"
                  />
                  <button @click="$refs.avatarInput.click()" class="shared-avatar-btn shared-avatar-upload-btn">
                    {{ createCharacterForm.avatar ? 'Change Avatar' : 'Add Avatar' }}
                  </button>
                  <button v-if="createCharacterForm.avatar" @click="removeAvatar" class="shared-avatar-btn shared-avatar-remove-btn">
                    Remove
                  </button>
                </div>
                
                <!-- Name -->
                <input 
                  v-model="createCharacterForm.name" 
                  placeholder="Character name"
                  class="shared-input shared-input-name"
                />
                
                <!-- Two Column Layout for Create -->
                <div class="shared-field-columns">
                  <!-- Left Column -->
                  <div class="shared-field-column">
                    <select v-model="createCharacterForm.race" class="shared-select">
                      <option value="">Select Race</option>
                      <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
                    </select>
                    
                    <select v-model="createCharacterForm.alignment" class="shared-select">
                      <option value="">Select Alignment</option>
                      <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
                    </select>
                    
                    <div class="shared-word-counter-field">
                      <textarea 
                        v-model="createCharacterForm.background" 
                        placeholder="Character background (max 80 words)"
                        class="shared-textarea"
                        @input="updateCreateBackgroundWordCount"
                      ></textarea>
                      <div class="shared-word-counter" :class="{ 'over-limit': createBackgroundWordCount > 80 }">
                        {{ createBackgroundWordCount }}/80 words
                      </div>
                    </div>
                  </div>
                  
                  <!-- Right Column -->
                  <div class="shared-field-column">
                    <select v-model="createCharacterForm.size" class="shared-select">
                      <option value="">Select Size</option>
                      <option v-for="size in characterSizes" :key="size" :value="size">{{ size }}</option>
                    </select>
                    
                    <input 
                      v-model="createCharacterForm.profession" 
                      placeholder="Profession"
                      class="shared-input"
                    />
                    
                    <div class="shared-word-counter-field">
                      <textarea 
                        v-model="createCharacterForm.communication_style" 
                        placeholder="Communication style (max 30 words)"
                        class="shared-textarea"
                        @input="updateCreateCommunicationWordCount"
                      ></textarea>
                      <div class="shared-word-counter" :class="{ 'over-limit': createCommunicationWordCount > 30 }">
                        {{ createCommunicationWordCount }}/30 words
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Tags Section -->
                <div class="shared-tags-field">
                  <div class="shared-tags-input-container">
                    <input 
                      v-model="newCreateCharacterTagInput"
                      placeholder="Add tag"
                      class="shared-input shared-tag-input"
                      @keyup.enter="addCreateCharacterTag"
                    />
                    <button @click="addCreateCharacterTag" class="shared-btn shared-btn-success" type="button">Add</button>
                  </div>
                  <div class="shared-tags-edit-display">
                    <span 
                      v-for="(tag, index) in createCharacterForm.tags" 
                      :key="index" 
                      class="shared-tag-bubble editable"
                    >
                      {{ tag }}
                      <button @click="removeCreateCharacterTag(index)" class="shared-tag-remove-btn" type="button">×</button>
                    </span>
                  </div>
                </div>
                
                <div class="shared-actions">
                  <button @click="saveCreateCharacter" class="shared-btn shared-btn-success" :disabled="!isCreateCharacterFormValid">Save</button>
                  <button @click="cancelCreateCharacter" class="shared-btn shared-btn-secondary">Cancel</button>
                </div>
              </div>
            </div>
            
            <CharacterCard
              v-else-if="selectedCharacter"
              :character="selectedCharacter"
              @update="updateCharacter"
              @delete="deleteCharacter"
            />
          </div>
        </div>
        
        <!-- Memories Tab Content -->
        <div v-else-if="activeTab === 'memories'" class="memories-split-view">
          <!-- Left Pane - Memory List -->
          <div class="memory-list-pane">
            <div class="memory-list-header">
              <h3>Memories</h3>
            </div>
            
            <div class="memory-list-content">
              <div 
                v-for="memory in memories" 
                :key="memory.id"
                :class="['memory-list-item', { active: selectedMemoryId === memory.id }]"
                @click="selectMemory(memory.id)"
              >
                {{ memory.title }}
              </div>
              
              <div v-if="memories.length === 0" class="empty-state">
                No memories yet
              </div>
            </div>
            
            <div class="memory-list-footer">
              <button @click="startCreateMemory" class="add-memory-btn">
                <span class="plus-icon">+</span>
                Add Memory
              </button>
            </div>
          </div>
          
          <!-- Right Pane - Memory Detail -->
          <div class="memory-detail-pane">
            <div v-if="!selectedMemory && !showCreateMemoryForm" class="empty-detail-state">
              <div class="empty-icon">🧠</div>
              <h3>No Memory Selected</h3>
              <p>Select a memory from the list to view details, or create a new one.</p>
            </div>
            
            <div v-else-if="showCreateMemoryForm" class="shared-card">
              <div class="shared-form">
                <!-- Memory Title -->
                <input 
                  v-model="createMemoryForm.title" 
                  placeholder="Memory title"
                  class="shared-input shared-input-name"
                />
                
                <!-- Linked Characters -->
                <div class="linked-characters-field">
                  <label class="shared-field-label">Linked Characters</label>
                  <select 
                    v-model="selectedCharacterToAdd" 
                    class="shared-select"
                    @change="addLinkedCharacterToCreate"
                  >
                    <option value="">Select character to link...</option>
                    <option 
                      v-for="character in availableCharactersForCreate" 
                      :key="character.id" 
                      :value="character.id"
                    >
                      {{ character.name }}
                    </option>
                  </select>
                  
                  <div class="linked-characters-display">
                    <span 
                      v-for="characterId in createMemoryForm.linked_character_ids" 
                      :key="characterId" 
                      class="shared-tag-bubble editable"
                    >
                      {{ getCharacterName(characterId) }}
                      <button @click="removeLinkedCharacterFromCreate(characterId)" class="shared-tag-remove-btn" type="button">×</button>
                    </span>
                  </div>
                </div>
                
                <!-- Visibility Type -->
                <div class="visibility-field">
                  <label class="shared-field-label">Visibility Conditions</label>
                  <div class="visibility-always-checkbox">
                    <label>
                      <input 
                        type="checkbox" 
                        v-model="isCreateAlwaysVisible"
                        @change="handleCreateAlwaysVisibleChange"
                      />
                      Always visible
                    </label>
                  </div>
                  
                  <div v-if="!isCreateAlwaysVisible" class="visibility-conditions-form">
                    <select v-model="createMemoryForm.visibility_type" class="shared-select">
                      <option value="keyword">Keywords</option>
                      <option value="player_race">Player Race</option>
                      <option value="player_alignment">Player Alignment</option>
                      <option value="tags">Player Tags</option>
                    </select>
                    
                    <!-- Keywords Input -->
                    <div v-if="createMemoryForm.visibility_type === 'keyword'" class="condition-input">
                      <input 
                        v-model="createKeywordInput"
                        placeholder="Enter keywords (comma-separated)"
                        class="shared-input"
                        @keyup.enter="addCreateKeywords"
                      />
                      <button @click="addCreateKeywords" class="shared-btn shared-btn-success" type="button">Add</button>
                    </div>
                    
                    <!-- Player Races Multi-select -->
                    <div v-if="createMemoryForm.visibility_type === 'player_race'" class="condition-input">
                      <select v-model="createSelectedRaceToAdd" class="shared-select" @change="addCreatePlayerRace">
                        <option value="">Select race...</option>
                        <option v-for="race in availableRacesForCreate" :key="race" :value="race">{{ race }}</option>
                      </select>
                    </div>
                    
                    <!-- Player Alignments Multi-select -->
                    <div v-if="createMemoryForm.visibility_type === 'player_alignment'" class="condition-input">
                      <select v-model="createSelectedAlignmentToAdd" class="shared-select" @change="addCreatePlayerAlignment">
                        <option value="">Select alignment...</option>
                        <option v-for="alignment in availableAlignmentsForCreate" :key="alignment" :value="alignment">{{ alignment }}</option>
                      </select>
                    </div>
                    
                    <!-- Player Tags Input -->
                    <div v-if="createMemoryForm.visibility_type === 'tags'" class="condition-input">
                      <input 
                        v-model="createPlayerTagInput"
                        placeholder="Enter player tags (comma-separated)"
                        class="shared-input"
                        @keyup.enter="addCreatePlayerTags"
                      />
                      <button @click="addCreatePlayerTags" class="shared-btn shared-btn-success" type="button">Add</button>
                    </div>
                    
                    <!-- Display Current Conditions -->
                    <div class="current-conditions">
                      <div v-if="createMemoryForm.visibility_type === 'keyword' && createMemoryForm.keywords.length > 0" class="shared-tags-edit-display">
                        <span v-for="(keyword, index) in createMemoryForm.keywords" :key="index" class="shared-tag-bubble editable">
                          {{ keyword }}
                          <button @click="removeCreateKeyword(index)" class="shared-tag-remove-btn" type="button">×</button>
                        </span>
                      </div>
                      
                      <div v-if="createMemoryForm.visibility_type === 'player_race' && createMemoryForm.player_races.length > 0" class="shared-tags-edit-display">
                        <span v-for="(race, index) in createMemoryForm.player_races" :key="index" class="shared-tag-bubble editable">
                          {{ race }}
                          <button @click="removeCreatePlayerRace(index)" class="shared-tag-remove-btn" type="button">×</button>
                        </span>
                      </div>
                      
                      <div v-if="createMemoryForm.visibility_type === 'player_alignment' && createMemoryForm.player_alignments.length > 0" class="shared-tags-edit-display">
                        <span v-for="(alignment, index) in createMemoryForm.player_alignments" :key="index" class="shared-tag-bubble editable">
                          {{ alignment }}
                          <button @click="removeCreatePlayerAlignment(index)" class="shared-tag-remove-btn" type="button">×</button>
                        </span>
                      </div>
                      
                      <div v-if="createMemoryForm.visibility_type === 'tags' && createMemoryForm.player_tags.length > 0" class="shared-tags-edit-display">
                        <span v-for="(tag, index) in createMemoryForm.player_tags" :key="index" class="shared-tag-bubble editable">
                          {{ tag }}
                          <button @click="removeCreatePlayerTag(index)" class="shared-tag-remove-btn" type="button">×</button>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Character Limit -->
                <div class="character-limit-field">
                  <label class="shared-field-label">Character Limit</label>
                  <input 
                    v-model.number="createMemoryForm.character_limit" 
                    type="number"
                    min="1"
                    max="10000"
                    class="shared-input"
                  />
                </div>
                
                <!-- Memory Text -->
                <div class="memory-text-field">
                  <label class="shared-field-label">Memory Text</label>
                  <BaseTextareaWithCharacterCounter
                    v-model="createMemoryForm.memory_text"
                    :placeholder="`Memory content (max ${createMemoryForm.character_limit} characters)`"
                    :max-characters="createMemoryForm.character_limit"
                  />
                </div>
                
                <!-- Actions -->
                <div class="shared-actions">
                  <button @click="saveCreateMemory" class="shared-btn shared-btn-success" :disabled="!isCreateMemoryFormValid">Save</button>
                  <button @click="cancelCreateMemory" class="shared-btn shared-btn-secondary">Cancel</button>
                </div>
              </div>
            </div>
            
            <MemoryCard
              v-else-if="selectedMemory"
              :memory="selectedMemory"
              :characters="characters"
              @update="updateMemory"
              @delete="deleteMemory"
            />
          </div>
        </div>
        
        <!-- Other tabs placeholder -->
        <div v-else class="placeholder-content">
          <h2>{{ activeTab.charAt(0).toUpperCase() + activeTab.slice(1) }}</h2>
          <p>This section is coming soon...</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed } from 'vue'
import PlayerCard from './components/PlayerCard.vue'
import CharacterCard from './components/CharacterCard.vue'
import MemoryCard from './components/MemoryCard.vue'
import TagManager from './components/forms/TagManager.vue'
import AvatarUpload from './components/base/AvatarUpload.vue'
import BaseTextarea from './components/base/BaseTextarea.vue'
import BaseTextareaWithCharacterCounter from './components/base/BaseTextareaWithCharacterCounter.vue'
import apiService from './services/api.js'
import { RACES, CLASSES, SIZES, ALIGNMENTS, NAVIGATION_TABS } from './constants/gameData.js'
import { WORD_LIMITS } from './constants/validation.js'
import { useFormValidation } from './utils/useFormValidation.js'

export default {
  name: 'App',
  components: {
    PlayerCard,
    CharacterCard,
    MemoryCard,
    TagManager,
    AvatarUpload,
    BaseTextarea,
    BaseTextareaWithCharacterCounter
  },
  setup() {
    const activeTab = ref('players')
    const players = ref([])
    const characters = ref([])
    const memories = ref([])
    const loading = ref(false)
    const error = ref('')
    const showCreateForm = ref(false)
    const showCreateCharacterForm = ref(false)
    const importing = ref(false)
    const successMessage = ref('')
    const selectedCharacterId = ref(null)
    const selectedPlayerId = ref(null)
    const selectedMemoryId = ref(null)
    const showCreateMemoryForm = ref(false)
    
    const createForm = reactive({
      name: '',
      avatar: null,
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: '',
      tags: []
    })

    const createCharacterForm = reactive({
      name: '',
      avatar: null,
      race: '',
      size: '',
      alignment: '',
      profession: '',
      background: '',
      communication_style: '',
      tags: []
    })

    const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'PLAYER')
    const { isFormValid: isCreateCharacterFormValid } = useFormValidation(createCharacterForm, 'CHARACTER')

    const getPageTitle = (tabId) => {
      const titleMap = {
        'players': 'Players',
        'characters': 'Characters',
        'memories': 'Memories',
        'encounters': 'Encounters'
      }
      return titleMap[tabId] || tabId.charAt(0).toUpperCase() + tabId.slice(1)
    }

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
      createForm.avatar = null
      createForm.appearance = ''
      createForm.race = ''
      createForm.class_name = ''
      createForm.size = ''
      createForm.alignment = ''
      createForm.tags = []
      newCreateTagInput.value = ''
      createWordCount.value = 0
    }

    const handlePlayerAvatarUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          createForm.avatar = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const removePlayerAvatar = () => {
      createForm.avatar = null
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          const newPlayer = await apiService.createPlayer({
            name: createForm.name.trim(),
            avatar: createForm.avatar,
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

    // Character functionality - isCreateCharacterFormValid already defined above via useFormValidation

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
    }

    const loadCharacters = async () => {
      loading.value = true
      error.value = ''
      try {
        characters.value = await apiService.getCharacters()
      } catch (err) {
        error.value = 'Failed to load characters. Make sure the backend is running.'
        console.error('Error loading characters:', err)
      } finally {
        loading.value = false
      }
    }

    const updateCharacter = async (characterId, characterData) => {
      try {
        const updatedCharacter = await apiService.updateCharacter(characterId, characterData)
        const index = characters.value.findIndex(c => c.id === characterId)
        if (index !== -1) {
          characters.value[index] = updatedCharacter
        }
      } catch (err) {
        error.value = 'Failed to update character'
        console.error('Error updating character:', err)
      }
    }

    const deleteCharacter = async (characterId) => {
      try {
        await apiService.deleteCharacter(characterId)
        characters.value = characters.value.filter(c => c.id !== characterId)
      } catch (err) {
        error.value = 'Failed to delete character'
        console.error('Error deleting character:', err)
      }
    }

    const startCreateCharacter = () => {
      showCreateCharacterForm.value = true
    }

    const updateCreateBackgroundWordCount = () => {
      createBackgroundWordCount.value = createCharacterForm.background.trim() ? createCharacterForm.background.trim().split(/\s+/).length : 0
    }

    const updateCreateCommunicationWordCount = () => {
      createCommunicationWordCount.value = createCharacterForm.communication_style.trim() ? createCharacterForm.communication_style.trim().split(/\s+/).length : 0
    }

    const addCreateCharacterTag = () => {
      if (newCreateCharacterTagInput.value.trim()) {
        const formattedTag = convertToKebabCase(newCreateCharacterTagInput.value.trim())
        if (!createCharacterForm.tags.includes(formattedTag)) {
          createCharacterForm.tags.push(formattedTag)
        }
        newCreateCharacterTagInput.value = ''
      }
    }

    const removeCreateCharacterTag = (index) => {
      createCharacterForm.tags.splice(index, 1)
    }

    const handleAvatarUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          createCharacterForm.avatar = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const removeAvatar = () => {
      createCharacterForm.avatar = null
    }

    const cancelCreateCharacter = () => {
      showCreateCharacterForm.value = false
      createCharacterForm.name = ''
      createCharacterForm.avatar = null
      createCharacterForm.race = ''
      createCharacterForm.size = ''
      createCharacterForm.alignment = ''
      createCharacterForm.profession = ''
      createCharacterForm.background = ''
      createCharacterForm.communication_style = ''
      createCharacterForm.tags = []
      newCreateCharacterTagInput.value = ''
      createBackgroundWordCount.value = 0
      createCommunicationWordCount.value = 0
    }

    const saveCreateCharacter = async () => {
      if (isCreateCharacterFormValid.value) {
        try {
          const newCharacter = await apiService.createCharacter({
            name: createCharacterForm.name.trim(),
            avatar: createCharacterForm.avatar,
            race: createCharacterForm.race,
            size: createCharacterForm.size,
            alignment: createCharacterForm.alignment,
            profession: createCharacterForm.profession.trim(),
            background: createCharacterForm.background.trim(),
            communication_style: createCharacterForm.communication_style.trim(),
            tags: createCharacterForm.tags
          })
          characters.value.push(newCharacter)
          selectedCharacterId.value = newCharacter.id // Auto-select the new character
          cancelCreateCharacter() // Reset form and hide it
        } catch (err) {
          error.value = 'Failed to create character'
          console.error('Error creating character:', err)
        }
      }
    }

    // Player selection functionality
    const selectedPlayer = computed(() => {
      return players.value.find(p => p.id === selectedPlayerId.value) || null
    })

    const selectPlayer = (playerId) => {
      selectedPlayerId.value = playerId
      showCreateForm.value = false // Hide create form when selecting a player
    }

    // Character selection functionality
    const selectedCharacter = computed(() => {
      return characters.value.find(c => c.id === selectedCharacterId.value) || null
    })

    const selectCharacter = (characterId) => {
      selectedCharacterId.value = characterId
      showCreateCharacterForm.value = false // Hide create form when selecting a character
    }

    // Auto-select first character when characters load
    const autoSelectFirstCharacter = () => {
      if (characters.value.length > 0 && !selectedCharacterId.value) {
        selectedCharacterId.value = characters.value[0].id
      }
    }

    // Update delete character to handle selection
    const deleteCharacterWithSelection = async (characterId) => {
      try {
        await apiService.deleteCharacter(characterId)
        characters.value = characters.value.filter(c => c.id !== characterId)
        
        // If we deleted the selected character, select another one
        if (selectedCharacterId.value === characterId) {
          if (characters.value.length > 0) {
            selectedCharacterId.value = characters.value[0].id
          } else {
            selectedCharacterId.value = null
          }
        }
      } catch (err) {
        error.value = 'Failed to delete character'
        console.error('Error deleting character:', err)
      }
    }

    onMounted(async () => {
      await loadPlayers()
      await loadCharacters()
      await loadMemories()
      autoSelectFirstCharacter()
    })

    // Add missing reactive variables
    const newCreateTagInput = ref('')
    const newCreateCharacterTagInput = ref('')
    const createWordCount = ref(0)
    const createBackgroundWordCount = ref(0)
    const createCommunicationWordCount = ref(0)

    // Memory functionality
    const createMemoryForm = reactive({
      title: '',
      linked_character_ids: [],
      visibility_type: 'always',
      keywords: [],
      player_races: [],
      player_alignments: [],
      player_tags: [],
      memory_text: '',
      character_limit: 500
    })

    const selectedCharacterToAdd = ref('')
    const createKeywordInput = ref('')
    const createPlayerTagInput = ref('')
    const createSelectedRaceToAdd = ref('')
    const createSelectedAlignmentToAdd = ref('')

    const isCreateAlwaysVisible = computed({
      get: () => createMemoryForm.visibility_type === 'always',
      set: (value) => {
        if (value) {
          createMemoryForm.visibility_type = 'always'
          createMemoryForm.keywords = []
          createMemoryForm.player_races = []
          createMemoryForm.player_alignments = []
          createMemoryForm.player_tags = []
        } else {
          createMemoryForm.visibility_type = 'keyword'
        }
      }
    })

    const availableCharactersForCreate = computed(() => {
      return characters.value.filter(c => !createMemoryForm.linked_character_ids.includes(c.id))
    })

    const availableRacesForCreate = computed(() => {
      return RACES.filter(race => !createMemoryForm.player_races.includes(race))
    })

    const availableAlignmentsForCreate = computed(() => {
      return ALIGNMENTS.filter(alignment => !createMemoryForm.player_alignments.includes(alignment))
    })

    const isCreateMemoryFormValid = computed(() => {
      return createMemoryForm.title.trim() && 
             createMemoryForm.memory_text.trim() && 
             createMemoryForm.memory_text.length <= createMemoryForm.character_limit
    })

    const selectedMemory = computed(() => {
      return memories.value.find(m => m.id === selectedMemoryId.value) || null
    })

    const getCharacterName = (characterId) => {
      const character = characters.value.find(c => c.id === characterId)
      return character ? character.name : `Character ${characterId}`
    }

    const loadMemories = async () => {
      loading.value = true
      error.value = ''
      try {
        memories.value = await apiService.getMemories()
      } catch (err) {
        error.value = 'Failed to load memories. Make sure the backend is running.'
        console.error('Error loading memories:', err)
      } finally {
        loading.value = false
      }
    }

    const selectMemory = (memoryId) => {
      selectedMemoryId.value = memoryId
      showCreateMemoryForm.value = false
    }

    const startCreateMemory = () => {
      showCreateMemoryForm.value = true
      selectedMemoryId.value = null
    }

    const cancelCreateMemory = () => {
      showCreateMemoryForm.value = false
      Object.assign(createMemoryForm, {
        title: '',
        linked_character_ids: [],
        visibility_type: 'always',
        keywords: [],
        player_races: [],
        player_alignments: [],
        player_tags: [],
        memory_text: '',
        character_limit: 500
      })
      selectedCharacterToAdd.value = ''
      createKeywordInput.value = ''
      createPlayerTagInput.value = ''
      createSelectedRaceToAdd.value = ''
      createSelectedAlignmentToAdd.value = ''
    }

    const saveCreateMemory = async () => {
      if (isCreateMemoryFormValid.value) {
        try {
          const newMemory = await apiService.createMemory({
            title: createMemoryForm.title.trim(),
            linked_character_ids: createMemoryForm.linked_character_ids,
            visibility_type: createMemoryForm.visibility_type,
            keywords: createMemoryForm.keywords,
            player_races: createMemoryForm.player_races,
            player_alignments: createMemoryForm.player_alignments,
            player_tags: createMemoryForm.player_tags,
            memory_text: createMemoryForm.memory_text.trim(),
            character_limit: createMemoryForm.character_limit
          })
          memories.value.push(newMemory)
          selectedMemoryId.value = newMemory.id
          cancelCreateMemory()
        } catch (err) {
          error.value = 'Failed to create memory'
          console.error('Error creating memory:', err)
        }
      }
    }

    const updateMemory = async (memoryId, memoryData) => {
      try {
        const updatedMemory = await apiService.updateMemory(memoryId, memoryData)
        const index = memories.value.findIndex(m => m.id === memoryId)
        if (index !== -1) {
          memories.value[index] = updatedMemory
        }
      } catch (err) {
        error.value = 'Failed to update memory'
        console.error('Error updating memory:', err)
      }
    }

    const deleteMemory = async (memoryId) => {
      try {
        await apiService.deleteMemory(memoryId)
        memories.value = memories.value.filter(m => m.id !== memoryId)
        if (selectedMemoryId.value === memoryId) {
          selectedMemoryId.value = null
        }
      } catch (err) {
        error.value = 'Failed to delete memory'
        console.error('Error deleting memory:', err)
      }
    }

    const handleCreateAlwaysVisibleChange = () => {
      if (isCreateAlwaysVisible.value) {
        createMemoryForm.keywords = []
        createMemoryForm.player_races = []
        createMemoryForm.player_alignments = []
        createMemoryForm.player_tags = []
      }
    }

    const addLinkedCharacterToCreate = () => {
      if (selectedCharacterToAdd.value && !createMemoryForm.linked_character_ids.includes(parseInt(selectedCharacterToAdd.value))) {
        createMemoryForm.linked_character_ids.push(parseInt(selectedCharacterToAdd.value))
        selectedCharacterToAdd.value = ''
      }
    }

    const removeLinkedCharacterFromCreate = (characterId) => {
      createMemoryForm.linked_character_ids = createMemoryForm.linked_character_ids.filter(id => id !== characterId)
    }

    const addCreateKeywords = () => {
      if (createKeywordInput.value.trim()) {
        const keywords = createKeywordInput.value.split(',').map(k => k.trim()).filter(k => k)
        keywords.forEach(keyword => {
          if (!createMemoryForm.keywords.includes(keyword)) {
            createMemoryForm.keywords.push(keyword)
          }
        })
        createKeywordInput.value = ''
      }
    }

    const removeCreateKeyword = (index) => {
      createMemoryForm.keywords.splice(index, 1)
    }

    const addCreatePlayerRace = () => {
      if (createSelectedRaceToAdd.value && !createMemoryForm.player_races.includes(createSelectedRaceToAdd.value)) {
        createMemoryForm.player_races.push(createSelectedRaceToAdd.value)
        createSelectedRaceToAdd.value = ''
      }
    }

    const removeCreatePlayerRace = (index) => {
      createMemoryForm.player_races.splice(index, 1)
    }

    const addCreatePlayerAlignment = () => {
      if (createSelectedAlignmentToAdd.value && !createMemoryForm.player_alignments.includes(createSelectedAlignmentToAdd.value)) {
        createMemoryForm.player_alignments.push(createSelectedAlignmentToAdd.value)
        createSelectedAlignmentToAdd.value = ''
      }
    }

    const removeCreatePlayerAlignment = (index) => {
      createMemoryForm.player_alignments.splice(index, 1)
    }

    const addCreatePlayerTags = () => {
      if (createPlayerTagInput.value.trim()) {
        const tags = createPlayerTagInput.value.split(',').map(t => t.trim()).filter(t => t)
        tags.forEach(tag => {
          if (!createMemoryForm.player_tags.includes(tag)) {
            createMemoryForm.player_tags.push(tag)
          }
        })
        createPlayerTagInput.value = ''
      }
    }

    const removeCreatePlayerTag = (index) => {
      createMemoryForm.player_tags.splice(index, 1)
    }

    return {
      activeTab,
      navigationTabs: NAVIGATION_TABS,
      players,
      characters,
      memories,
      loading,
      error,
      successMessage,
      showCreateForm,
      showCreateCharacterForm,
      showCreateMemoryForm,
      createForm,
      createCharacterForm,
      createMemoryForm,
      newCreateTagInput,
      newCreateCharacterTagInput,
      createWordCount,
      createBackgroundWordCount,
      createCommunicationWordCount,
      importing,
      selectedCharacterId,
      selectedCharacter,
      selectedPlayerId,
      selectedPlayer,
      selectedMemoryId,
      selectedMemory,
      selectedCharacterToAdd,
      createKeywordInput,
      createPlayerTagInput,
      createSelectedRaceToAdd,
      createSelectedAlignmentToAdd,
      isCreateAlwaysVisible,
      availableCharactersForCreate,
      availableRacesForCreate,
      availableAlignmentsForCreate,
      isCreateMemoryFormValid,
      races: RACES,
      classes: CLASSES,
      sizes: SIZES.PLAYER,
      characterSizes: SIZES.CHARACTER,
      alignments: ALIGNMENTS,
      isCreateFormValid,
      isCreateCharacterFormValid,
      getInitials,
      getPageTitle,
      getCharacterName,
      setActiveTab,
      updatePlayer,
      deletePlayer,
      updateCharacter,
      deleteCharacter: deleteCharacterWithSelection,
      selectCharacter,
      selectPlayer,
      selectMemory,
      startCreate,
      startCreateCharacter,
      startCreateMemory,
      updateCreateWordCount,
      updateCreateBackgroundWordCount,
      updateCreateCommunicationWordCount,
      addCreateTag,
      removeCreateTag,
      addCreateCharacterTag,
      removeCreateCharacterTag,
      handleAvatarUpload,
      removeAvatar,
      handlePlayerAvatarUpload,
      removePlayerAvatar,
      cancelCreate,
      cancelCreateCharacter,
      cancelCreateMemory,
      saveCreate,
      saveCreateCharacter,
      saveCreateMemory,
      updateMemory,
      deleteMemory,
      handleCreateAlwaysVisibleChange,
      addLinkedCharacterToCreate,
      removeLinkedCharacterFromCreate,
      addCreateKeywords,
      removeCreateKeyword,
      addCreatePlayerRace,
      removeCreatePlayerRace,
      addCreatePlayerAlignment,
      removeCreatePlayerAlignment,
      addCreatePlayerTags,
      removeCreatePlayerTag,
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

/* App.vue now uses shared styles - minimal custom styles needed */

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

/* Character Card Styles */
.character-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  padding: 20px;
  align-items: start;
}

.character-cards-grid > * {
  align-self: start;
}

.character-card {
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

.character-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.create-character-button {
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

.create-character-button:hover {
  color: #007bff;
}

.character-edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.avatar-edit-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.avatar-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #007bff, #0056b3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-initials {
  color: white;
  font-size: 1.5em;
  font-weight: bold;
}

.avatar-upload-btn, .avatar-remove-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: all 0.2s ease;
}

.avatar-upload-btn {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
}

.avatar-upload-btn:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
}

.avatar-remove-btn {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.avatar-remove-btn:hover {
  background: linear-gradient(135deg, #c82333, #a71e2a);
}

.name-input {
  text-align: center;
  font-size: 1.2em;
  font-weight: 600;
}

.edit-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.edit-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.background-field, .communication-field {
  position: relative;
}

.tags-field {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-input-container {
  display: flex;
  gap: 10px;
}

.tag-input {
  flex: 1;
}

.add-tag-btn {
  padding: 12px 18px;
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.add-tag-btn:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.tags-edit-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  align-items: flex-start;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
}

.tag-bubble {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.8em;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.tag-bubble.editable {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  display: flex;
  align-items: center;
  gap: 6px;
  padding-right: 6px;
}

.remove-tag-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1em;
  cursor: pointer;
  padding: 2px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.remove-tag-btn:hover {
  background: rgba(255, 255, 255, 0.4);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
  text-align: center;
}

.placeholder-content h2 {
  margin: 0 0 16px 0;
  font-size: 2em;
  color: #333;
}

.placeholder-content p {
  margin: 0;
  font-size: 1.1em;
}

/* Players Split View Layout */
.players-split-view {
  display: flex;
  height: 100%;
  gap: 0;
}

.player-list-pane {
  width: 25%;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-right: 2px solid #e9ecef;
}

.player-list-header {
  padding: 20px 16px 16px 16px;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.player-list-header h3 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
}

.player-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.player-list-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
  color: #495057;
  background: white;
  margin: 2px 8px;
  border-radius: 6px;
  border: 1px solid transparent;
}

.player-list-item:hover {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
}

.player-list-item.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-left-color: #004085;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.player-list-item.active:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
}

.player-list-footer {
  padding: 16px;
  border-top: 1px solid #e9ecef;
  background: white;
}

.add-player-btn {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.add-player-btn:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.add-player-btn .plus-icon {
  font-size: 1.2em;
  font-weight: bold;
}

.import-players-btn {
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  margin-top: 8px;
}

.import-players-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.import-players-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.player-detail-pane {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #ffffff;
}

/* Characters Split View Layout */
.characters-split-view {
  display: flex;
  height: 100%;
  gap: 0;
}

.character-list-pane {
  width: 25%;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-right: 2px solid #e9ecef;
}

.character-list-header {
  padding: 20px 16px 16px 16px;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.character-list-header h3 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
}

.character-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.character-list-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
  color: #495057;
  background: white;
  margin: 2px 8px;
  border-radius: 6px;
  border: 1px solid transparent;
}

.character-list-item:hover {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
}

.character-list-item.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-left-color: #004085;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.character-list-item.active:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
}

.empty-state {
  padding: 40px 16px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
  font-size: 0.9em;
}

.character-list-footer {
  padding: 16px;
  border-top: 1px solid #e9ecef;
  background: white;
}

.add-character-btn {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.add-character-btn:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.add-character-btn .plus-icon {
  font-size: 1.2em;
  font-weight: bold;
}

.import-characters-btn {
  width: 100%;
  padding: 10px 16px;
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  margin-top: 8px;
}

.import-characters-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.import-characters-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.character-detail-pane {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #ffffff;
}

.empty-detail-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
  text-align: center;
  padding: 40px;
}

.empty-detail-state .empty-icon {
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-detail-state h3 {
  margin: 0 0 12px 0;
  font-size: 1.5em;
  color: #495057;
}

.empty-detail-state p {
  margin: 0;
  font-size: 1em;
  line-height: 1.5;
}

/* Scrollbar styling for character list */
.character-list-content::-webkit-scrollbar {
  width: 6px;
}

.character-list-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.character-list-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.character-list-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Memories Split View Layout */
.memories-split-view {
  display: flex;
  height: 100%;
  gap: 0;
}

.memory-list-pane {
  width: 25%;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-right: 2px solid #e9ecef;
}

.memory-list-header {
  padding: 20px 16px 16px 16px;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

.memory-list-header h3 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
}

.memory-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.memory-list-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
  color: #495057;
  background: white;
  margin: 2px 8px;
  border-radius: 6px;
  border: 1px solid transparent;
}

.memory-list-item:hover {
  background: #e3f2fd;
  color: #1976d2;
  border-color: #bbdefb;
}

.memory-list-item.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-left-color: #004085;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.memory-list-item.active:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
}

.memory-list-footer {
  padding: 16px;
  border-top: 1px solid #e9ecef;
  background: white;
}

.add-memory-btn {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.add-memory-btn:hover {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.add-memory-btn .plus-icon {
  font-size: 1.2em;
  font-weight: bold;
}

.memory-detail-pane {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #ffffff;
}

/* Memory form specific styles */
.linked-characters-field,
.visibility-field,
.character-limit-field,
.memory-text-field {
  margin-bottom: 16px;
}

.linked-characters-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
  min-height: 40px;
  align-items: flex-start;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
}

.visibility-always-checkbox {
  margin-bottom: 12px;
}

.visibility-always-checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
}

.visibility-conditions-form {
  opacity: 1;
  transition: opacity 0.3s ease;
}

.condition-input {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}

.condition-input .shared-input {
  flex: 1;
}

.current-conditions {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .edit-columns {
    grid-template-columns: 1fr;
  }
  
  .character-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .characters-split-view, .memories-split-view {
    flex-direction: column;
  }
  
  .character-list-pane, .memory-list-pane {
    width: 100%;
    min-width: unset;
    max-height: 200px;
  }
  
  .character-detail-pane, .memory-detail-pane {
    flex: 1;
    padding: 16px;
  }
}
</style>
