<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Players"
    create-button-text="Add Player"
    empty-message="No players yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #footer-actions>
      <input 
        ref="playerFileInput"
        type="file" 
        accept=".md,.markdown,.json" 
        @change="handleImportFile"
        style="display: none"
      />
      <button 
        @click="$refs.playerFileInput.click()" 
        class="shared-import-btn"
        :disabled="importing"
      >
        <span v-if="importing">Importing...</span>
        <span v-else>Import Players</span>
      </button>
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading players...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>
      
      <EmptyState
        v-else-if="!selectedPlayer && !showCreateForm"
        icon="👤"
        title="No Player Selected"
        message="Select a player from the list to view details, or create a new one."
      />
      
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
          
          <!-- Gender Field (Full Width) -->
          <select v-model="createForm.gender" class="shared-select">
            <option value="">Select Gender</option>
            <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
          </select>
          
          <!-- Reopen the field columns div for tags -->
          <div class="shared-field-columns">
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
import PlayerCard from '../components/PlayerCard.vue'
import { useEntityCRUD } from '../utils/useEntityCRUD.js'
import { useFileImport } from '../utils/useFileImport.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import { getInitials, handleAvatarUpload } from '../utils/avatarUtils.js'
import { RACES, CLASSES, SIZES, ALIGNMENTS } from '../constants/gameData.js'

export default {
  name: 'PlayersPage',
  components: {
    SplitViewLayout,
    EmptyState,
    PlayerCard
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
    } = useEntityCRUD('Player')

    const { importing, handleImportFile: handleFileImport } = useFileImport('Player')

    const createForm = reactive({
      name: '',
      avatar: null,
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: '',
      gender: '',
      tags: []
    })

    const newCreateTagInput = ref('')
    const createWordCount = ref(0)

    const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'PLAYER')

    // Gender options (not in gameData.js)
    const genders = ['male', 'female', 'nonbinary']

    const selectedPlayer = computed(() => {
      return entities.value.find(p => p.id === selectedEntityId.value) || null
    })

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

    const handlePlayerAvatarUpload = (event) => {
      handleAvatarUpload(event, (result) => {
        createForm.avatar = result
      })
    }

    const removePlayerAvatar = () => {
      createForm.avatar = null
    }

    const resetCreateForm = () => {
      createForm.name = ''
      createForm.avatar = null
      createForm.appearance = ''
      createForm.race = ''
      createForm.class_name = ''
      createForm.size = ''
      createForm.alignment = ''
      createForm.gender = ''
      createForm.tags = []
      newCreateTagInput.value = ''
      createWordCount.value = 0
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          await createEntity({
            name: createForm.name.trim(),
            avatar: createForm.avatar,
            appearance: createForm.appearance.trim(),
            race: createForm.race,
            class_name: createForm.class_name,
            size: createForm.size,
            alignment: createForm.alignment,
            gender: createForm.gender,
            tags: createForm.tags
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

    const handleImportFile = (event) => {
      handleFileImport(
        event,
        createEntity,
        (message) => {
          // Success message - could emit to parent or use toast
          console.log('Import success:', message)
        },
        (errorMessage) => {
          error.value = errorMessage
        }
      )
    }

    onMounted(() => {
      loadEntities()
    })

    return {
      entities,
      loading,
      error,
      selectedEntityId,
      showCreateForm,
      selectedPlayer,
      createForm,
      newCreateTagInput,
      createWordCount,
      importing,
      races: RACES,
      classes: CLASSES,
      genders,
      sizes: SIZES.PLAYER,
      alignments: ALIGNMENTS,
      isCreateFormValid,
      selectEntity,
      startCreate,
      updateEntity,
      deleteEntity,
      getInitials,
      updateCreateWordCount,
      addCreateTag,
      removeCreateTag,
      handlePlayerAvatarUpload,
      removePlayerAvatar,
      saveCreate,
      cancelCreate: handleCancelCreate,
      handleImportFile
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
</style>
