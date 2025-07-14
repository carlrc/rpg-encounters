<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="memory-display">
      <!-- Memory Title -->
      <h2 class="shared-title">{{ memory.title }}</h2>
      
      <!-- Linked Characters -->
      <div class="shared-field">
        <div class="shared-field-label">Linked Characters</div>
        <div class="shared-field-value">
          <span v-if="linkedCharacterNames.length > 0">
            {{ linkedCharacterNames.join(', ') }}
          </span>
          <span v-else class="shared-no-tags">No characters linked</span>
        </div>
      </div>
      
      <!-- Visibility Conditions -->
      <div class="shared-field">
        <div class="shared-field-label">Visibility</div>
        <div class="shared-field-value">
          <div class="visibility-display">
            <span class="visibility-type">{{ formatVisibilityType(memory.visibility_type) }}</span>
            <div v-if="memory.visibility_type !== 'always'" class="visibility-conditions">
              <div v-if="memory.visibility_type === 'keyword' && memory.keywords.length > 0">
                <strong>Keywords:</strong> {{ memory.keywords.join(', ') }}
              </div>
              <div v-if="memory.visibility_type === 'player_race' && memory.player_races.length > 0">
                <strong>Player Races:</strong> {{ memory.player_races.join(', ') }}
              </div>
              <div v-if="memory.visibility_type === 'player_alignment' && memory.player_alignments.length > 0">
                <strong>Player Alignments:</strong> {{ memory.player_alignments.join(', ') }}
              </div>
              <div v-if="memory.visibility_type === 'tags' && memory.player_tags.length > 0">
                <strong>Player Tags:</strong> {{ memory.player_tags.join(', ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Memory Text -->
      <div class="shared-field shared-field-full-width">
        <div class="shared-field-label">Memory Text</div>
        <div class="shared-field-value">
          <div class="memory-text-display">{{ memory.memory_text }}</div>
          <div class="character-limit-info">
            {{ memory.memory_text.length }}/{{ memory.character_limit }} characters
          </div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="confirmDelete" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>
    
    <div v-else class="memory-edit">
      <!-- Edit Form -->
      <div class="shared-form">
        <!-- Memory Title -->
        <input 
          v-model="editForm.title" 
          placeholder="Memory title"
          class="shared-input shared-input-name"
        />
        
        <!-- Linked Characters -->
        <div class="linked-characters-field">
          <label class="shared-field-label">Linked Characters</label>
          <select 
            v-model="selectedCharacterToAdd" 
            class="shared-select"
            @change="addLinkedCharacter"
          >
            <option value="">Select character to link...</option>
            <option 
              v-for="character in availableCharacters" 
              :key="character.id" 
              :value="character.id"
            >
              {{ character.name }}
            </option>
          </select>
          
          <div class="linked-characters-display">
            <span 
              v-for="characterId in editForm.linked_character_ids" 
              :key="characterId" 
              class="shared-tag-bubble editable"
            >
              {{ getCharacterName(characterId) }}
              <button @click="removeLinkedCharacter(characterId)" class="shared-tag-remove-btn" type="button">×</button>
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
                v-model="isAlwaysVisible"
                @change="handleAlwaysVisibleChange"
              />
              Always visible
            </label>
          </div>
          
          <div v-if="!isAlwaysVisible" class="visibility-conditions-form">
            <select v-model="editForm.visibility_type" class="shared-select">
              <option value="keyword">Keywords</option>
              <option value="player_race">Player Race</option>
              <option value="player_alignment">Player Alignment</option>
              <option value="tags">Player Tags</option>
            </select>
            
            <!-- Keywords Input -->
            <div v-if="editForm.visibility_type === 'keyword'" class="condition-input">
              <input 
                v-model="keywordInput"
                placeholder="Enter keywords (comma-separated)"
                class="shared-input"
                @keyup.enter="addKeywords"
              />
              <button @click="addKeywords" class="shared-btn shared-btn-success" type="button">Add</button>
            </div>
            
            <!-- Player Races Multi-select -->
            <div v-if="editForm.visibility_type === 'player_race'" class="condition-input">
              <select v-model="selectedRaceToAdd" class="shared-select" @change="addPlayerRace">
                <option value="">Select race...</option>
                <option v-for="race in availableRaces" :key="race" :value="race">{{ race }}</option>
              </select>
            </div>
            
            <!-- Player Alignments Multi-select -->
            <div v-if="editForm.visibility_type === 'player_alignment'" class="condition-input">
              <select v-model="selectedAlignmentToAdd" class="shared-select" @change="addPlayerAlignment">
                <option value="">Select alignment...</option>
                <option v-for="alignment in availableAlignments" :key="alignment" :value="alignment">{{ alignment }}</option>
              </select>
            </div>
            
            <!-- Player Tags Input -->
            <div v-if="editForm.visibility_type === 'tags'" class="condition-input">
              <input 
                v-model="playerTagInput"
                placeholder="Enter player tags (comma-separated)"
                class="shared-input"
                @keyup.enter="addPlayerTags"
              />
              <button @click="addPlayerTags" class="shared-btn shared-btn-success" type="button">Add</button>
            </div>
            
            <!-- Display Current Conditions -->
            <div class="current-conditions">
              <div v-if="editForm.visibility_type === 'keyword' && editForm.keywords.length > 0" class="shared-tags-edit-display">
                <span v-for="(keyword, index) in editForm.keywords" :key="index" class="shared-tag-bubble editable">
                  {{ keyword }}
                  <button @click="removeKeyword(index)" class="shared-tag-remove-btn" type="button">×</button>
                </span>
              </div>
              
              <div v-if="editForm.visibility_type === 'player_race' && editForm.player_races.length > 0" class="shared-tags-edit-display">
                <span v-for="(race, index) in editForm.player_races" :key="index" class="shared-tag-bubble editable">
                  {{ race }}
                  <button @click="removePlayerRace(index)" class="shared-tag-remove-btn" type="button">×</button>
                </span>
              </div>
              
              <div v-if="editForm.visibility_type === 'player_alignment' && editForm.player_alignments.length > 0" class="shared-tags-edit-display">
                <span v-for="(alignment, index) in editForm.player_alignments" :key="index" class="shared-tag-bubble editable">
                  {{ alignment }}
                  <button @click="removePlayerAlignment(index)" class="shared-tag-remove-btn" type="button">×</button>
                </span>
              </div>
              
              <div v-if="editForm.visibility_type === 'tags' && editForm.player_tags.length > 0" class="shared-tags-edit-display">
                <span v-for="(tag, index) in editForm.player_tags" :key="index" class="shared-tag-bubble editable">
                  {{ tag }}
                  <button @click="removePlayerTag(index)" class="shared-tag-remove-btn" type="button">×</button>
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Character Limit -->
        <div class="character-limit-field">
          <label class="shared-field-label">Character Limit</label>
          <input 
            v-model.number="editForm.character_limit" 
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
            v-model="editForm.memory_text"
            :placeholder="`Memory content (max ${editForm.character_limit} characters)`"
            :max-characters="editForm.character_limit"
          />
        </div>
        
        <!-- Actions -->
        <div class="shared-actions">
          <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">Save</button>
          <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
import { RACES, ALIGNMENTS } from '../constants/gameData.js'

export default {
  name: 'MemoryCard',
  components: {
    BaseTextareaWithCharacterCounter
  },
  props: {
    memory: {
      type: Object,
      required: true
    },
    characters: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    const selectedCharacterToAdd = ref('')
    const selectedRaceToAdd = ref('')
    const selectedAlignmentToAdd = ref('')
    const keywordInput = ref('')
    const playerTagInput = ref('')
    
    const editForm = reactive({
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
    
    const isAlwaysVisible = computed({
      get: () => editForm.visibility_type === 'always',
      set: (value) => {
        if (value) {
          editForm.visibility_type = 'always'
          // Clear all condition arrays when switching to always
          editForm.keywords = []
          editForm.player_races = []
          editForm.player_alignments = []
          editForm.player_tags = []
        } else {
          editForm.visibility_type = 'keyword'
        }
      }
    })
    
    const linkedCharacterNames = computed(() => {
      return props.memory.linked_character_ids.map(id => {
        const character = props.characters.find(c => c.id === id)
        return character ? character.name : `Character ${id}`
      })
    })
    
    const availableCharacters = computed(() => {
      return props.characters.filter(c => !editForm.linked_character_ids.includes(c.id))
    })
    
    const availableRaces = computed(() => {
      return RACES.filter(race => !editForm.player_races.includes(race))
    })
    
    const availableAlignments = computed(() => {
      return ALIGNMENTS.filter(alignment => !editForm.player_alignments.includes(alignment))
    })
    
    const isFormValid = computed(() => {
      return editForm.title.trim() && 
             editForm.memory_text.trim() && 
             editForm.memory_text.length <= editForm.character_limit
    })
    
    const formatVisibilityType = (type) => {
      const typeMap = {
        'always': 'Always Visible',
        'keyword': 'Keyword-based',
        'player_race': 'Player Race-based',
        'player_alignment': 'Player Alignment-based',
        'tags': 'Player Tag-based'
      }
      return typeMap[type] || type
    }
    
    const getCharacterName = (characterId) => {
      const character = props.characters.find(c => c.id === characterId)
      return character ? character.name : `Character ${characterId}`
    }
    
    const startEdit = () => {
      // Copy memory data to edit form
      Object.assign(editForm, {
        title: props.memory.title,
        linked_character_ids: [...props.memory.linked_character_ids],
        visibility_type: props.memory.visibility_type,
        keywords: [...props.memory.keywords],
        player_races: [...props.memory.player_races],
        player_alignments: [...props.memory.player_alignments],
        player_tags: [...props.memory.player_tags],
        memory_text: props.memory.memory_text,
        character_limit: props.memory.character_limit
      })
      isEditing.value = true
    }
    
    const cancelEdit = () => {
      isEditing.value = false
      // Reset form
      selectedCharacterToAdd.value = ''
      selectedRaceToAdd.value = ''
      selectedAlignmentToAdd.value = ''
      keywordInput.value = ''
      playerTagInput.value = ''
    }
    
    const saveEdit = () => {
      if (isFormValid.value) {
        emit('update', props.memory.id, {
          title: editForm.title.trim(),
          linked_character_ids: editForm.linked_character_ids,
          visibility_type: editForm.visibility_type,
          keywords: editForm.keywords,
          player_races: editForm.player_races,
          player_alignments: editForm.player_alignments,
          player_tags: editForm.player_tags,
          memory_text: editForm.memory_text.trim(),
          character_limit: editForm.character_limit
        })
        isEditing.value = false
      }
    }
    
    const confirmDelete = () => {
      if (confirm(`Are you sure you want to delete the memory "${props.memory.title}"?`)) {
        emit('delete', props.memory.id)
      }
    }
    
    const handleAlwaysVisibleChange = () => {
      if (isAlwaysVisible.value) {
        // Clear all condition arrays when switching to always
        editForm.keywords = []
        editForm.player_races = []
        editForm.player_alignments = []
        editForm.player_tags = []
      }
    }
    
    // Linked Characters Management
    const addLinkedCharacter = () => {
      if (selectedCharacterToAdd.value && !editForm.linked_character_ids.includes(parseInt(selectedCharacterToAdd.value))) {
        editForm.linked_character_ids.push(parseInt(selectedCharacterToAdd.value))
        selectedCharacterToAdd.value = ''
      }
    }
    
    const removeLinkedCharacter = (characterId) => {
      editForm.linked_character_ids = editForm.linked_character_ids.filter(id => id !== characterId)
    }
    
    // Keywords Management
    const addKeywords = () => {
      if (keywordInput.value.trim()) {
        const keywords = keywordInput.value.split(',').map(k => k.trim()).filter(k => k)
        keywords.forEach(keyword => {
          if (!editForm.keywords.includes(keyword)) {
            editForm.keywords.push(keyword)
          }
        })
        keywordInput.value = ''
      }
    }
    
    const removeKeyword = (index) => {
      editForm.keywords.splice(index, 1)
    }
    
    // Player Races Management
    const addPlayerRace = () => {
      if (selectedRaceToAdd.value && !editForm.player_races.includes(selectedRaceToAdd.value)) {
        editForm.player_races.push(selectedRaceToAdd.value)
        selectedRaceToAdd.value = ''
      }
    }
    
    const removePlayerRace = (index) => {
      editForm.player_races.splice(index, 1)
    }
    
    // Player Alignments Management
    const addPlayerAlignment = () => {
      if (selectedAlignmentToAdd.value && !editForm.player_alignments.includes(selectedAlignmentToAdd.value)) {
        editForm.player_alignments.push(selectedAlignmentToAdd.value)
        selectedAlignmentToAdd.value = ''
      }
    }
    
    const removePlayerAlignment = (index) => {
      editForm.player_alignments.splice(index, 1)
    }
    
    // Player Tags Management
    const addPlayerTags = () => {
      if (playerTagInput.value.trim()) {
        const tags = playerTagInput.value.split(',').map(t => t.trim()).filter(t => t)
        tags.forEach(tag => {
          if (!editForm.player_tags.includes(tag)) {
            editForm.player_tags.push(tag)
          }
        })
        playerTagInput.value = ''
      }
    }
    
    const removePlayerTag = (index) => {
      editForm.player_tags.splice(index, 1)
    }
    
    return {
      isEditing,
      editForm,
      isAlwaysVisible,
      selectedCharacterToAdd,
      selectedRaceToAdd,
      selectedAlignmentToAdd,
      keywordInput,
      playerTagInput,
      linkedCharacterNames,
      availableCharacters,
      availableRaces,
      availableAlignments,
      isFormValid,
      formatVisibilityType,
      getCharacterName,
      startEdit,
      cancelEdit,
      saveEdit,
      confirmDelete,
      handleAlwaysVisibleChange,
      addLinkedCharacter,
      removeLinkedCharacter,
      addKeywords,
      removeKeyword,
      addPlayerRace,
      removePlayerRace,
      addPlayerAlignment,
      removePlayerAlignment,
      addPlayerTags,
      removePlayerTag
    }
  }
}
</script>

<style scoped>
.memory-text-display {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  white-space: pre-wrap;
  line-height: 1.5;
  min-height: 60px;
}

.character-limit-info {
  font-size: 0.8em;
  color: #6c757d;
  text-align: right;
  margin-top: 4px;
}

.visibility-display {
  text-align: left;
}

.visibility-type {
  font-weight: 600;
  color: #007bff;
  display: block;
  margin-bottom: 8px;
}

.visibility-conditions {
  font-size: 0.9em;
  color: #495057;
}

.visibility-conditions > div {
  margin-bottom: 4px;
}

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

.visibility-conditions-form.disabled {
  opacity: 0.5;
  pointer-events: none;
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
</style>
