<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Memories"
    create-button-text="Add Memory"
    empty-message="No memories yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #detail-content>
      <div v-if="loading" class="loading">Loading memories...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      
      <EmptyState
        v-else-if="!selectedMemory && !showCreateForm"
        icon="🧠"
        title="No Memory Selected"
        message="Select a memory from the list to view details, or create a new one."
      />
      
      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Memory Title -->
          <input 
            v-model="createForm.title" 
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
                v-for="characterId in createForm.linked_character_ids" 
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
              <select v-model="createForm.visibility_type" class="shared-select">
                <option value="keyword">Keywords</option>
                <option value="player_race">Player Race</option>
                <option value="player_alignment">Player Alignment</option>
                <option value="tags">Player Tags</option>
              </select>
              
              <!-- Keywords Input -->
              <div v-if="createForm.visibility_type === 'keyword'" class="condition-input">
                <input 
                  v-model="keywordInput"
                  placeholder="Enter keywords (comma-separated)"
                  class="shared-input"
                  @keyup.enter="addKeywords"
                />
                <button @click="addKeywords" class="shared-btn shared-btn-success" type="button">Add</button>
              </div>
              
              <!-- Player Races Multi-select -->
              <div v-if="createForm.visibility_type === 'player_race'" class="condition-input">
                <select v-model="selectedRaceToAdd" class="shared-select" @change="addPlayerRace">
                  <option value="">Select race...</option>
                  <option v-for="race in availableRaces" :key="race" :value="race">{{ race }}</option>
                </select>
              </div>
              
              <!-- Player Alignments Multi-select -->
              <div v-if="createForm.visibility_type === 'player_alignment'" class="condition-input">
                <select v-model="selectedAlignmentToAdd" class="shared-select" @change="addPlayerAlignment">
                  <option value="">Select alignment...</option>
                  <option v-for="alignment in availableAlignments" :key="alignment" :value="alignment">{{ alignment }}</option>
                </select>
              </div>
              
              <!-- Player Tags Input -->
              <div v-if="createForm.visibility_type === 'tags'" class="condition-input">
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
                <div v-if="createForm.visibility_type === 'keyword' && createForm.keywords.length > 0" class="shared-tags-edit-display">
                  <span v-for="(keyword, index) in createForm.keywords" :key="index" class="shared-tag-bubble editable">
                    {{ keyword }}
                    <button @click="removeKeyword(index)" class="shared-tag-remove-btn" type="button">×</button>
                  </span>
                </div>
                
                <div v-if="createForm.visibility_type === 'player_race' && createForm.player_races.length > 0" class="shared-tags-edit-display">
                  <span v-for="(race, index) in createForm.player_races" :key="index" class="shared-tag-bubble editable">
                    {{ race }}
                    <button @click="removePlayerRace(index)" class="shared-tag-remove-btn" type="button">×</button>
                  </span>
                </div>
                
                <div v-if="createForm.visibility_type === 'player_alignment' && createForm.player_alignments.length > 0" class="shared-tags-edit-display">
                  <span v-for="(alignment, index) in createForm.player_alignments" :key="index" class="shared-tag-bubble editable">
                    {{ alignment }}
                    <button @click="removePlayerAlignment(index)" class="shared-tag-remove-btn" type="button">×</button>
                  </span>
                </div>
                
                <div v-if="createForm.visibility_type === 'tags' && createForm.player_tags.length > 0" class="shared-tags-edit-display">
                  <span v-for="(tag, index) in createForm.player_tags" :key="index" class="shared-tag-bubble editable">
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
              v-model.number="createForm.character_limit" 
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
              v-model="createForm.memory_text"
              :placeholder="`Memory content (max ${createForm.character_limit} characters)`"
              :max-characters="createForm.character_limit"
            />
          </div>
          
          <!-- Actions -->
          <div class="shared-actions">
            <button @click="saveCreate" class="shared-btn shared-btn-success" :disabled="!isCreateFormValid">Save</button>
            <button @click="cancelCreate" class="shared-btn shared-btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
      
      <MemoryCard
        v-else-if="selectedMemory"
        :memory="selectedMemory"
        :characters="characters"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import MemoryCard from '../components/MemoryCard.vue'
import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
import { useEntityCRUD } from '../utils/useEntityCRUD.js'
import apiService from '../services/api.js'
import { RACES, ALIGNMENTS } from '../constants/gameData.js'

export default {
  name: 'MemoriesPage',
  components: {
    SplitViewLayout,
    EmptyState,
    MemoryCard,
    BaseTextareaWithCharacterCounter
  },
  setup() {
    const {
      entities,
      loading,
      error,
      selectedEntityId,
      showCreateForm,
      loadEntities,
      createEntity,
      updateEntity,
      deleteEntity,
      selectEntity,
      startCreate,
      cancelCreate
    } = useEntityCRUD('Memory')

    const characters = ref([])

    const createForm = reactive({
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
    const keywordInput = ref('')
    const playerTagInput = ref('')
    const selectedRaceToAdd = ref('')
    const selectedAlignmentToAdd = ref('')

    const isAlwaysVisible = computed({
      get: () => createForm.visibility_type === 'always',
      set: (value) => {
        if (value) {
          createForm.visibility_type = 'always'
          createForm.keywords = []
          createForm.player_races = []
          createForm.player_alignments = []
          createForm.player_tags = []
        } else {
          createForm.visibility_type = 'keyword'
        }
      }
    })

    const availableCharacters = computed(() => {
      return characters.value.filter(c => !createForm.linked_character_ids.includes(c.id))
    })

    const availableRaces = computed(() => {
      return RACES.filter(race => !createForm.player_races.includes(race))
    })

    const availableAlignments = computed(() => {
      return ALIGNMENTS.filter(alignment => !createForm.player_alignments.includes(alignment))
    })

    const isCreateFormValid = computed(() => {
      return createForm.title.trim() && 
             createForm.memory_text.trim() && 
             createForm.memory_text.length <= createForm.character_limit
    })

    const selectedMemory = computed(() => {
      return entities.value.find(m => m.id === selectedEntityId.value) || null
    })

    const getCharacterName = (characterId) => {
      const character = characters.value.find(c => c.id === characterId)
      return character ? character.name : `Character ${characterId}`
    }

    const loadCharacters = async () => {
      try {
        characters.value = await apiService.getCharacters()
      } catch (err) {
        console.error('Error loading characters:', err)
      }
    }

    const handleAlwaysVisibleChange = () => {
      if (isAlwaysVisible.value) {
        createForm.keywords = []
        createForm.player_races = []
        createForm.player_alignments = []
        createForm.player_tags = []
      }
    }

    const addLinkedCharacter = () => {
      if (selectedCharacterToAdd.value && !createForm.linked_character_ids.includes(parseInt(selectedCharacterToAdd.value))) {
        createForm.linked_character_ids.push(parseInt(selectedCharacterToAdd.value))
        selectedCharacterToAdd.value = ''
      }
    }

    const removeLinkedCharacter = (characterId) => {
      createForm.linked_character_ids = createForm.linked_character_ids.filter(id => id !== characterId)
    }

    const addKeywords = () => {
      if (keywordInput.value.trim()) {
        const keywords = keywordInput.value.split(',').map(k => k.trim()).filter(k => k)
        keywords.forEach(keyword => {
          if (!createForm.keywords.includes(keyword)) {
            createForm.keywords.push(keyword)
          }
        })
        keywordInput.value = ''
      }
    }

    const removeKeyword = (index) => {
      createForm.keywords.splice(index, 1)
    }

    const addPlayerRace = () => {
      if (selectedRaceToAdd.value && !createForm.player_races.includes(selectedRaceToAdd.value)) {
        createForm.player_races.push(selectedRaceToAdd.value)
        selectedRaceToAdd.value = ''
      }
    }

    const removePlayerRace = (index) => {
      createForm.player_races.splice(index, 1)
    }

    const addPlayerAlignment = () => {
      if (selectedAlignmentToAdd.value && !createForm.player_alignments.includes(selectedAlignmentToAdd.value)) {
        createForm.player_alignments.push(selectedAlignmentToAdd.value)
        selectedAlignmentToAdd.value = ''
      }
    }

    const removePlayerAlignment = (index) => {
      createForm.player_alignments.splice(index, 1)
    }

    const addPlayerTags = () => {
      if (playerTagInput.value.trim()) {
        const tags = playerTagInput.value.split(',').map(t => t.trim()).filter(t => t)
        tags.forEach(tag => {
          if (!createForm.player_tags.includes(tag)) {
            createForm.player_tags.push(tag)
          }
        })
        playerTagInput.value = ''
      }
    }

    const removePlayerTag = (index) => {
      createForm.player_tags.splice(index, 1)
    }

    const resetCreateForm = () => {
      Object.assign(createForm, {
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
      keywordInput.value = ''
      playerTagInput.value = ''
      selectedRaceToAdd.value = ''
      selectedAlignmentToAdd.value = ''
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          await createEntity({
            title: createForm.title.trim(),
            linked_character_ids: createForm.linked_character_ids,
            visibility_type: createForm.visibility_type,
            keywords: createForm.keywords,
            player_races: createForm.player_races,
            player_alignments: createForm.player_alignments,
            player_tags: createForm.player_tags,
            memory_text: createForm.memory_text.trim(),
            character_limit: createForm.character_limit
          })
          resetCreateForm()
        } catch (err) {
          // Error handling is done in useEntityCRUD
        }
      }
    }

    const handleCancelCreate = () => {
      cancelCreate()
      resetCreateForm()
    }

    onMounted(async () => {
      await loadEntities()
      await loadCharacters()
    })

    return {
      entities,
      loading,
      error,
      selectedEntityId,
      showCreateForm,
      selectedMemory,
      characters,
      createForm,
      selectedCharacterToAdd,
      keywordInput,
      playerTagInput,
      selectedRaceToAdd,
      selectedAlignmentToAdd,
      isAlwaysVisible,
      availableCharacters,
      availableRaces,
      availableAlignments,
      isCreateFormValid,
      selectEntity,
      startCreate,
      updateEntity,
      deleteEntity,
      getCharacterName,
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
      removePlayerTag,
      saveCreate,
      cancelCreate: handleCancelCreate
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
</style>
