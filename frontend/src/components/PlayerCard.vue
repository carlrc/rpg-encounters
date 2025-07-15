<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="player-content">
      <!-- Avatar Section -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img v-if="player.avatar" :src="player.avatar" :alt="player.name" class="shared-avatar-image" />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(player.name) }}</span>
          </div>
        </div>
      </div>
      
      <h3 class="shared-title">{{ player.name }}</h3>
      
      <!-- Two Column Layout -->
      <div class="player-fields">
        <div class="shared-field-columns">
          <!-- Left Column -->
          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Race</label>
              <p class="shared-field-value">{{ player.race }}</p>
            </div>
            
            <div class="shared-field">
              <label class="shared-field-label">Class</label>
              <p class="shared-field-value">{{ player.class_name }}</p>
            </div>
          </div>
          
          <!-- Right Column -->
          <div class="shared-field-column">
            <div class="shared-field">
              <label class="shared-field-label">Size</label>
              <p class="shared-field-value">{{ player.size }}</p>
            </div>
            
            <div class="shared-field">
              <label class="shared-field-label">Alignment</label>
              <p class="shared-field-value">{{ player.alignment }}</p>
            </div>
          </div>
        </div>
        
        <!-- Appearance Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Appearance</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ player.appearance }}</div>
            <div class="character-limit-info">
              {{ (player.appearance || '').length }}/{{ CHARACTER_LIMITS.PLAYER_APPEARANCE }} characters
            </div>
          </div>
        </div>
        
      </div>
      
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deletePlayer" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>
    
    <div v-else class="shared-form">
      <!-- Avatar Upload -->
      <AvatarUpload v-model="editForm.avatar" :name="editForm.name" />
      
      <!-- Name -->
      <input 
        v-model="editForm.name" 
        placeholder="Player name"
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
          
          <select v-model="editForm.class_name" class="shared-select">
            <option value="">Select Class</option>
            <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">{{ playerClass }}</option>
          </select>
        </div>
        
        <!-- Right Column -->
        <div class="shared-field-column">
          <select v-model="editForm.size" class="shared-select">
            <option value="">Select Size</option>
            <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
          </select>
          
          <select v-model="editForm.alignment" class="shared-select">
            <option value="">Select Alignment</option>
            <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
          </select>
        </div>
      </div>
      
      <!-- Appearance Field (Full Width) -->
      <div class="appearance-field">
        <label class="shared-field-label">Appearance</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.appearance"
          :placeholder="`Player appearance (max ${appearanceCharacterLimit} characters)`"
          :max-characters="appearanceCharacterLimit"
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
import { RACES, CLASSES, SIZES, ALIGNMENTS } from '../constants/gameData.js'
import { CHARACTER_LIMITS } from '../constants/validation.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import AvatarUpload from './base/AvatarUpload.vue'
import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'

export default {
  name: 'PlayerCard',
  components: {
    AvatarUpload,
    BaseTextareaWithCharacterCounter
  },
  props: {
    player: {
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
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: ''
    })

    const { isFormValid } = useFormValidation(editForm, 'PLAYER')

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
    }

    const startEdit = () => {
      editForm.name = props.player.name || ''
      editForm.avatar = props.player.avatar || null
      editForm.appearance = props.player.appearance || ''
      editForm.race = props.player.race || ''
      editForm.class_name = props.player.class_name || ''
      editForm.size = props.player.size || ''
      editForm.alignment = props.player.alignment || ''
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
    }

    const saveEdit = () => {
      if (isFormValid.value) {
        emit('update', props.player.id, {
          name: editForm.name.trim(),
          avatar: editForm.avatar,
          appearance: editForm.appearance.trim(),
          race: editForm.race,
          class_name: editForm.class_name,
          size: editForm.size,
          alignment: editForm.alignment
        })
        isEditing.value = false
      }
    }

    const deletePlayer = () => {
      if (confirm(`Are you sure you want to delete ${props.player.name}?`)) {
        emit('delete', props.player.id)
      }
    }

    return {
      isEditing,
      editForm,
      races: RACES,
      classes: CLASSES,
      sizes: SIZES.PLAYER,
      alignments: ALIGNMENTS,
      appearanceCharacterLimit: CHARACTER_LIMITS.PLAYER_APPEARANCE,
      CHARACTER_LIMITS,
      isFormValid,
      getInitials,
      startEdit,
      cancelEdit,
      saveEdit,
      deletePlayer
    }
  }
}
</script>

<style scoped>
/* PlayerCard now uses shared styles - minimal custom styles needed */
.player-fields {
  flex: 1;
}


.character-limit-info {
  font-size: 0.8em;
  color: #6c757d;
  text-align: right;
  margin-top: 4px;
}

.appearance-field {
  margin-bottom: 16px;
}
</style>
