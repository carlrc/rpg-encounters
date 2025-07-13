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
      <div class="shared-avatar-edit-section">
        <div class="shared-avatar-container">
          <img v-if="editForm.avatar" :src="editForm.avatar" :alt="editForm.name" class="shared-avatar-image" />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(editForm.name) }}</span>
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
          {{ editForm.avatar ? 'Change Avatar' : 'Add Avatar' }}
        </button>
        <button v-if="editForm.avatar" @click="removeAvatar" class="shared-avatar-btn shared-avatar-remove-btn">
          Remove
        </button>
      </div>
      
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
          
          <div class="shared-word-counter-field">
            <textarea 
              v-model="editForm.background" 
              placeholder="Character background (max 80 words)"
              class="shared-textarea"
              @input="updateBackgroundWordCount"
            ></textarea>
            <div class="shared-word-counter" :class="{ 'over-limit': backgroundWordCount > 80 }">
              {{ backgroundWordCount }}/80 words
            </div>
          </div>
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
          
          <div class="shared-word-counter-field">
            <textarea 
              v-model="editForm.communication_style" 
              placeholder="Communication style (max 30 words)"
              class="shared-textarea"
              @input="updateCommunicationWordCount"
            ></textarea>
            <div class="shared-word-counter" :class="{ 'over-limit': communicationWordCount > 30 }">
              {{ communicationWordCount }}/30 words
            </div>
          </div>
        </div>
      </div>
      
      <!-- Tags Section -->
      <div class="shared-tags-field">
        <div class="shared-tags-input-container">
          <input 
            v-model="newTagInput"
            placeholder="Add tag"
            class="shared-input shared-tag-input"
            @keyup.enter="addTag"
          />
          <button @click="addTag" class="shared-btn shared-btn-success" type="button">Add</button>
        </div>
        <div class="shared-tags-edit-display">
          <span 
            v-for="(tag, index) in editForm.tags" 
            :key="index" 
            class="shared-tag-bubble editable"
          >
            {{ tag }}
            <button @click="removeTag(index)" class="shared-tag-remove-btn" type="button">×</button>
          </span>
        </div>
      </div>
      
      <div class="shared-actions">
        <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">Save</button>
        <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'

export default {
  name: 'CharacterCard',
  props: {
    character: {
      type: Object,
      required: true
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    const newTagInput = ref('')
    const backgroundWordCount = ref(0)
    const communicationWordCount = ref(0)
    
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

    const races = [
      'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
      'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
    ]

    const sizes = [
      'Small', 'Medium', 'Large'
    ]

    const alignments = [
      'Lawful Good', 'Neutral Good', 'Chaotic Good',
      'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
      'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
    ]

    const isFormValid = computed(() => {
      return editForm.name.trim() && 
             editForm.race && 
             editForm.size &&
             editForm.alignment &&
             editForm.profession.trim() &&
             editForm.background.trim() &&
             editForm.communication_style.trim() &&
             backgroundWordCount.value <= 80 &&
             communicationWordCount.value <= 30
    })

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
    }

    const updateBackgroundWordCount = () => {
      backgroundWordCount.value = editForm.background.trim() ? editForm.background.trim().split(/\s+/).length : 0
    }

    const updateCommunicationWordCount = () => {
      communicationWordCount.value = editForm.communication_style.trim() ? editForm.communication_style.trim().split(/\s+/).length : 0
    }

    const convertToKebabCase = (text) => {
      const kebab = text.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
      return kebab.startsWith('#') ? kebab : `#${kebab}`
    }

    const addTag = () => {
      if (newTagInput.value.trim()) {
        const formattedTag = convertToKebabCase(newTagInput.value.trim())
        if (!editForm.tags.includes(formattedTag)) {
          editForm.tags.push(formattedTag)
        }
        newTagInput.value = ''
      }
    }

    const removeTag = (index) => {
      editForm.tags.splice(index, 1)
    }

    const handleAvatarUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          editForm.avatar = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const removeAvatar = () => {
      editForm.avatar = null
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
      updateBackgroundWordCount()
      updateCommunicationWordCount()
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      newTagInput.value = ''
      backgroundWordCount.value = 0
      communicationWordCount.value = 0
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
        newTagInput.value = ''
        backgroundWordCount.value = 0
        communicationWordCount.value = 0
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
      newTagInput,
      backgroundWordCount,
      communicationWordCount,
      races,
      sizes,
      alignments,
      isFormValid,
      getInitials,
      updateBackgroundWordCount,
      updateCommunicationWordCount,
      addTag,
      removeTag,
      handleAvatarUpload,
      removeAvatar,
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
