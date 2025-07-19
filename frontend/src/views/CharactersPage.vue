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
        class="shared-import-btn"
        :disabled="importing"
      >
        <span v-if="importing">Importing...</span>
        <span v-else>Import Characters</span>
      </button>
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading characters...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>
      
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
              @change="onAvatarUpload"
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
              
              <BaseTextareaWithCharacterCounter
                v-model="createForm.background"
                :placeholder="`Character background (max ${CHARACTER_LIMITS.CHARACTER_BACKGROUND} characters)`"
                :max-characters="CHARACTER_LIMITS.CHARACTER_BACKGROUND"
              />
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
              
              <BaseTextareaWithCharacterCounter
                v-model="createForm.communication_style"
                :placeholder="`Communication style (max ${CHARACTER_LIMITS.CHARACTER_COMMUNICATION} characters)`"
                :max-characters="CHARACTER_LIMITS.CHARACTER_COMMUNICATION"
              />
            </div>
          </div>
          
          <!-- Motivation Field (Full Width) -->
          <BaseTextareaWithCharacterCounter
            v-model="createForm.motivation"
            :placeholder="`Character motivation (max ${CHARACTER_LIMITS.CHARACTER_MOTIVATION} characters)`"
            :max-characters="CHARACTER_LIMITS.CHARACTER_MOTIVATION"
          />
          
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
import { getInitials, handleAvatarUpload } from '../utils/avatarUtils.js'
import { RACES, SIZES, ALIGNMENTS } from '../constants/gameData.js'
import { CHARACTER_LIMITS } from '../constants/validation.js'
import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'

export default {
  name: 'CharactersPage',
  components: {
    SplitViewLayout,
    EmptyState,
    CharacterCard,
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
      motivation: ''
    })

    const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'CHARACTER')

    const selectedCharacter = computed(() => {
      return entities.value.find(c => c.id === selectedEntityId.value) || null
    })

    const onAvatarUpload = (event) => {
      handleAvatarUpload(event, (result) => {
        createForm.avatar = result
      })
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
      createForm.motivation = ''
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
            motivation: createForm.motivation.trim(),
            // Initialize empty trust profile fields
            race_preferences: {},
            class_preferences: {},
            gender_preferences: {},
            size_preferences: {},
            appearance_keywords: [],
            storytelling_keywords: []
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
      importing,
      races: RACES,
      characterSizes: SIZES.CHARACTER,
      alignments: ALIGNMENTS,
      CHARACTER_LIMITS,
      isCreateFormValid,
      selectEntity,
      startCreate,
      updateEntity,
      deleteEntity,
      getInitials,
      onAvatarUpload,
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
