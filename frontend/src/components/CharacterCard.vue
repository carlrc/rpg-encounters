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
            
            <div class="shared-field">
              <label class="shared-field-label">Background</label>
              <p class="shared-field-value shared-text-italic">{{ character.background }}</p>
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
            
            <div class="shared-field">
              <label class="shared-field-label">Communication Style</label>
              <p class="shared-field-value shared-text-italic">{{ character.communication_style }}</p>
            </div>
          </div>
        </div>
        
        <!-- Tags Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <label class="shared-field-label">Tags</label>
          <div class="shared-tags-display">
            <span 
              v-for="tag in character.tags" 
              :key="tag" 
              class="shared-tag-bubble"
            >
              {{ tag }}
            </span>
            <span v-if="!character.tags || character.tags.length === 0" class="shared-no-tags">
              No tags assigned
            </span>
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
          
          <BaseTextarea 
            v-model="editForm.background"
            placeholder="Character background (max 80 words)"
            :max-words="backgroundWordLimit"
          />
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
          
          <BaseTextarea 
            v-model="editForm.communication_style"
            placeholder="Communication style (max 30 words)"
            :max-words="communicationWordLimit"
          />
        </div>
      </div>
      
      <!-- Tags Section -->
      <TagManager v-model="editForm.tags" />
      
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
import { WORD_LIMITS } from '../constants/validation.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import TagManager from './forms/TagManager.vue'
import AvatarUpload from './base/AvatarUpload.vue'
import BaseTextarea from './base/BaseTextarea.vue'

export default {
  name: 'CharacterCard',
  components: {
    TagManager,
    AvatarUpload,
    BaseTextarea
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
      tags: []
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
      editForm.tags = [...(props.character.tags || [])]
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
          tags: editForm.tags
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
      backgroundWordLimit: WORD_LIMITS.CHARACTER_BACKGROUND,
      communicationWordLimit: WORD_LIMITS.CHARACTER_COMMUNICATION,
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
</style>
