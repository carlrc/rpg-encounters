<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="character-content">
      <!-- Avatar Section -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img v-if="character.avatar" :src="character.avatar" :alt="character.name" class="shared-avatar-image" />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Name -->
      <h3 class="shared-title">{{ character.name }}</h3>
      
      <!-- Two Column Layout -->
      <div class="character-fields">
        <div class="shared-field-columns">
          <!-- Left Column -->
          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Race</label>
              <p class="shared-field-value">{{ character.race }}</p>
            </div>
            
            <div class="shared-field">
              <label class="shared-field-label">Alignment</label>
              <p class="shared-field-value">{{ character.alignment }}</p>
            </div>
          </div>
          
          <!-- Right Column -->
          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Size</label>
              <p class="shared-field-value">{{ character.size }}</p>
            </div>
            
            <div class="shared-field">
              <label class="shared-field-label">Profession</label>
              <p class="shared-field-value">{{ character.profession }}</p>
            </div>
          </div>
        </div>
        
        <!-- Background Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Background</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ character.background }}</div>
            <div class="character-limit-info">
              {{ (character.background || '').length }}/{{ CHARACTER_LIMITS.CHARACTER_BACKGROUND }} characters
            </div>
          </div>
        </div>
        
        <!-- Communication Style Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Communication Style</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ character.communication_style }}</div>
            <div class="character-limit-info">
              {{ (character.communication_style || '').length }}/{{ CHARACTER_LIMITS.CHARACTER_COMMUNICATION }} characters
            </div>
          </div>
        </div>
        
        <!-- Motivation Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Motivation</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ character.motivation }}</div>
            <div class="character-limit-info">
              {{ (character.motivation || '').length }}/{{ CHARACTER_LIMITS.CHARACTER_MOTIVATION }} characters
            </div>
          </div>
        </div>
      </div>
      
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deleteCharacter" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>
    
    <div v-else class="shared-form">
      <!-- Avatar Upload -->
      <AvatarUpload v-model="editForm.avatar" :name="editForm.name" />
      
      <!-- Name -->
      <input 
        v-model="editForm.name" 
        placeholder="Character name"
        class="shared-input shared-input-name"
      />
      
      <!-- Two Column Layout for Edit -->
      <div class="shared-field-columns">
        <!-- Left Column -->
        <div class="shared-field-column">
          <select v-model="editForm.race" class="shared-select">
            <option value="">Select Race</option>
            <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
          </select>
          
          <select v-model="editForm.alignment" class="shared-select">
            <option value="">Select Alignment</option>
            <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
          </select>
        </div>
        
        <!-- Right Column -->
        <div class="shared-field-column">
          <select v-model="editForm.size" class="shared-select">
            <option value="">Select Size</option>
            <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
          </select>
          
          <input 
            v-model="editForm.profession" 
            placeholder="Profession"
            class="shared-input"
          />
        </div>
      </div>
      
      <!-- Background Field (Full Width) -->
      <div class="background-field">
        <label class="shared-field-label">Background</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.background"
          :placeholder="`Character background (max ${backgroundCharacterLimit} characters)`"
          :max-characters="backgroundCharacterLimit"
        />
      </div>
      
      <!-- Communication Style Field (Full Width) -->
      <div class="communication-field">
        <label class="shared-field-label">Communication Style</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.communication_style"
          :placeholder="`Communication style (max ${communicationCharacterLimit} characters)`"
          :max-characters="communicationCharacterLimit"
        />
      </div>
      
      <!-- Motivation Field (Full Width) -->
      <div class="motivation-field">
        <label class="shared-field-label">Motivation</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.motivation"
          :placeholder="`Character motivation (max ${motivationCharacterLimit} characters)`"
          :max-characters="motivationCharacterLimit"
        />
      </div>
      
      <div class="shared-actions">
        <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">Save</button>
        <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { RACES, SIZES, ALIGNMENTS } from '../constants/gameData.js'
import { CHARACTER_LIMITS } from '../constants/validation.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import AvatarUpload from './base/AvatarUpload.vue'
import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'

export default {
  name: 'CharacterCard',
  components: {
    AvatarUpload,
    BaseTextareaWithCharacterCounter
  },
  props: {
    character: {
      type: Object,
      required: true
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    
    const editForm = reactive({
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

    const { isFormValid } = useFormValidation(editForm, 'CHARACTER')

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
    }

    const startEdit = () => {
      editForm.name = props.character.name || ''
      editForm.avatar = props.character.avatar || null
      editForm.race = props.character.race || ''
      editForm.size = props.character.size || ''
      editForm.alignment = props.character.alignment || ''
      editForm.profession = props.character.profession || ''
      editForm.background = props.character.background || ''
      editForm.communication_style = props.character.communication_style || ''
      editForm.motivation = props.character.motivation || ''
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
    }

    const saveEdit = () => {
      if (isFormValid.value) {
        emit('update', props.character.id, {
          name: editForm.name.trim(),
          avatar: editForm.avatar,
          race: editForm.race,
          size: editForm.size,
          alignment: editForm.alignment,
          profession: editForm.profession.trim(),
          background: editForm.background.trim(),
          communication_style: editForm.communication_style.trim(),
          motivation: editForm.motivation.trim()
        })
        isEditing.value = false
      }
    }

    const deleteCharacter = () => {
      if (confirm(`Are you sure you want to delete ${props.character.name}?`)) {
        emit('delete', props.character.id)
      }
    }

    return {
      isEditing,
      editForm,
      races: RACES,
      sizes: SIZES.CHARACTER,
      alignments: ALIGNMENTS,
      backgroundCharacterLimit: CHARACTER_LIMITS.CHARACTER_BACKGROUND,
      communicationCharacterLimit: CHARACTER_LIMITS.CHARACTER_COMMUNICATION,
      motivationCharacterLimit: CHARACTER_LIMITS.CHARACTER_MOTIVATION,
      CHARACTER_LIMITS,
      isFormValid,
      getInitials,
      startEdit,
      cancelEdit,
      saveEdit,
      deleteCharacter
    }
  }
}
</script>

<style scoped>
/* CharacterCard now uses shared styles - minimal custom styles needed */
.character-fields {
  flex: 1;
}


.character-limit-info {
  font-size: 0.8em;
  color: #6c757d;
  text-align: right;
  margin-top: 4px;
}

.background-field,
.communication-field,
.motivation-field {
  margin-bottom: 16px;
}
</style>
