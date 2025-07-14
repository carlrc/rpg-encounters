<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Characters"
    create-button-text="Add Character"
    empty-message="No characters yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #footer-actions>
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
    </template>

    <template #detail-content>
      <div v-if="loading" class="loading">Loading characters...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      
      <EmptyState
        v-else-if="!selectedCharacter && !showCreateForm"
        icon="👤"
        title="No Character Selected"
        message="Select a character from the list to view details, or create a new one."
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
              ref="avatarInput"
              type="file" 
              accept="image/*" 
              @change="handleAvatarUpload"
              style="display: none"
            />
            <button @click="$refs.avatarInput.click()" class="shared-avatar-btn shared-avatar-upload-btn">
              {{ createForm.avatar ? 'Change Avatar' : 'Add Avatar' }}
            </button>
            <button v-if="createForm.avatar" @click="removeAvatar" class="shared-avatar-btn shared-avatar-remove-btn">
              Remove
            </button>
          </div>
          
          <!-- Name -->
          <input 
            v-model="createForm.name" 
            placeholder="Character name"
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
              
              <select v-model="createForm.alignment" class="shared-select">
                <option value="">Select Alignment</option>
                <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
              </select>
              
              <div class="shared-word-counter-field">
                <textarea 
                  v-model="createForm.background" 
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
              <select v-model="createForm.size" class="shared-select">
                <option value="">Select Size</option>
                <option v-for="size in characterSizes" :key="size" :value="size">{{ size }}</option>
              </select>
              
              <input 
                v-model="createForm.profession" 
                placeholder="Profession"
                class="shared-input"
              />
              
              <div class="shared-word-counter-field">
                <textarea 
                  v-model="createForm.communication_style" 
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
      
      <CharacterCard
        v-else-if="selectedCharacter"
        :character="selectedCharacter"
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
import CharacterCard from '../components/CharacterCard.vue'
import { useEntityCRUD } from '../utils/useEntityCRUD.js'
import { useFileImport } from '../utils/useFileImport.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import { RACES, SIZES, ALIGNMENTS } from '../constants/gameData.js'

export default {
  name: 'CharactersPage',
  components: {
    SplitViewLayout,
    EmptyState,
    CharacterCard
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
    } = useEntityCRUD('Character')

    const { importing, handleImportFile: handleFileImport } = useFileImport('Character')

    const createForm = reactive({
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

    const newCreateTagInput = ref('')
    const createBackgroundWordCount = ref(0)
    const createCommunicationWordCount = ref(0)

    const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'CHARACTER')

    const selectedCharacter = computed(() => {
      return entities.value.find(c => c.id === selectedEntityId.value) || null
    })

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
    }

    const updateCreateBackgroundWordCount = () => {
      createBackgroundWordCount.value = createForm.background.trim() ? createForm.background.trim().split(/\s+/).length : 0
    }

    const updateCreateCommunicationWordCount = () => {
      createCommunicationWordCount.value = createForm.communication_style.trim() ? createForm.communication_style.trim().split(/\s+/).length : 0
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

    const handleAvatarUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          createForm.avatar = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const removeAvatar = () => {
      createForm.avatar = null
    }

    const resetCreateForm = () => {
      createForm.name = ''
      createForm.avatar = null
      createForm.race = ''
      createForm.size = ''
      createForm.alignment = ''
      createForm.profession = ''
      createForm.background = ''
      createForm.communication_style = ''
      createForm.tags = []
      newCreateTagInput.value = ''
      createBackgroundWordCount.value = 0
      createCommunicationWordCount.value = 0
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          await createEntity({
            name: createForm.name.trim(),
            avatar: createForm.avatar,
            race: createForm.race,
            size: createForm.size,
            alignment: createForm.alignment,
            profession: createForm.profession.trim(),
            background: createForm.background.trim(),
            communication_style: createForm.communication_style.trim(),
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
      selectedCharacter,
      createForm,
      newCreateTagInput,
      createBackgroundWordCount,
      createCommunicationWordCount,
      importing,
      races: RACES,
      characterSizes: SIZES.CHARACTER,
      alignments: ALIGNMENTS,
      isCreateFormValid,
      selectEntity,
      startCreate,
      updateEntity,
      deleteEntity,
      getInitials,
      updateCreateBackgroundWordCount,
      updateCreateCommunicationWordCount,
      addCreateTag,
      removeCreateTag,
      handleAvatarUpload,
      removeAvatar,
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
</style>
