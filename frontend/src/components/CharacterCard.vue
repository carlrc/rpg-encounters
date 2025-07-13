<template>
  <div class="character-card">
    <div v-if="!isEditing" class="character-content">
      <!-- Avatar Section -->
      <div class="avatar-section">
        <div class="avatar-container">
          <img v-if="character.avatar" :src="character.avatar" :alt="character.name" class="avatar-image" />
          <div v-else class="avatar-placeholder">
            <span class="avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Name -->
      <h3 class="character-name">{{ character.name }}</h3>
      
      <!-- Two Column Layout -->
      <div class="character-fields">
        <div class="field-columns">
          <!-- Left Column -->
          <div class="field-column">
            <div class="character-field">
              <label class="field-label">Race</label>
              <p class="field-value">{{ character.race }}</p>
            </div>
            
            <div class="character-field">
              <label class="field-label">Alignment</label>
              <p class="field-value">{{ character.alignment }}</p>
            </div>
            
            <div class="character-field">
              <label class="field-label">Background</label>
              <p class="field-value background-text">{{ character.background }}</p>
            </div>
          </div>
          
          <!-- Right Column -->
          <div class="field-column">
            <div class="character-field">
              <label class="field-label">Size</label>
              <p class="field-value">{{ character.size }}</p>
            </div>
            
            <div class="character-field">
              <label class="field-label">Profession</label>
              <p class="field-value">{{ character.profession }}</p>
            </div>
            
            <div class="character-field">
              <label class="field-label">Communication Style</label>
              <p class="field-value communication-text">{{ character.communication_style }}</p>
            </div>
          </div>
        </div>
        
        <!-- Tags Section (Full Width) -->
        <div class="character-field tags-section">
          <label class="field-label">Tags</label>
          <div class="tags-display">
            <span 
              v-for="tag in character.tags" 
              :key="tag" 
              class="tag-bubble"
            >
              {{ tag }}
            </span>
            <span v-if="!character.tags || character.tags.length === 0" class="no-tags">
              No tags assigned
            </span>
          </div>
        </div>
      </div>
      
      <div class="character-actions">
        <button @click="startEdit" class="edit-btn">Edit</button>
        <button @click="deleteCharacter" class="delete-btn">Delete</button>
      </div>
    </div>
    
    <div v-else class="character-edit-form">
      <!-- Avatar Upload -->
      <div class="avatar-edit-section">
        <div class="avatar-container">
          <img v-if="editForm.avatar" :src="editForm.avatar" :alt="editForm.name" class="avatar-image" />
          <div v-else class="avatar-placeholder">
            <span class="avatar-initials">{{ getInitials(editForm.name) }}</span>
          </div>
        </div>
        <input 
          ref="avatarInput"
          type="file" 
          accept="image/*" 
          @change="handleAvatarUpload"
          style="display: none"
        />
        <button @click="$refs.avatarInput.click()" class="avatar-upload-btn">
          {{ editForm.avatar ? 'Change Avatar' : 'Add Avatar' }}
        </button>
        <button v-if="editForm.avatar" @click="removeAvatar" class="avatar-remove-btn">
          Remove
        </button>
      </div>
      
      <!-- Name -->
      <input 
        v-model="editForm.name" 
        placeholder="Character name"
        class="edit-input name-input"
      />
      
      <!-- Two Column Layout for Edit -->
      <div class="edit-columns">
        <!-- Left Column -->
        <div class="edit-column">
          <select v-model="editForm.race" class="edit-select">
            <option value="">Select Race</option>
            <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
          </select>
          
          <select v-model="editForm.alignment" class="edit-select">
            <option value="">Select Alignment</option>
            <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
          </select>
          
          <div class="background-field">
            <textarea 
              v-model="editForm.background" 
              placeholder="Character background (max 80 words)"
              class="edit-textarea"
              @input="updateBackgroundWordCount"
            ></textarea>
            <div class="word-counter" :class="{ 'over-limit': backgroundWordCount > 80 }">
              {{ backgroundWordCount }}/80 words
            </div>
          </div>
        </div>
        
        <!-- Right Column -->
        <div class="edit-column">
          <select v-model="editForm.size" class="edit-select">
            <option value="">Select Size</option>
            <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
          </select>
          
          <input 
            v-model="editForm.profession" 
            placeholder="Profession"
            class="edit-input"
          />
          
          <div class="communication-field">
            <textarea 
              v-model="editForm.communication_style" 
              placeholder="Communication style (max 30 words)"
              class="edit-textarea"
              @input="updateCommunicationWordCount"
            ></textarea>
            <div class="word-counter" :class="{ 'over-limit': communicationWordCount > 30 }">
              {{ communicationWordCount }}/30 words
            </div>
          </div>
        </div>
      </div>
      
      <!-- Tags Section -->
      <div class="tags-field">
        <div class="tags-input-container">
          <input 
            v-model="newTagInput"
            placeholder="Add tag"
            class="edit-input tag-input"
            @keyup.enter="addTag"
          />
          <button @click="addTag" class="add-tag-btn" type="button">Add</button>
        </div>
        <div class="tags-edit-display">
          <span 
            v-for="(tag, index) in editForm.tags" 
            :key="index" 
            class="tag-bubble editable"
          >
            {{ tag }}
            <button @click="removeTag(index)" class="remove-tag-btn" type="button">×</button>
          </span>
        </div>
      </div>
      
      <div class="edit-actions">
        <button @click="saveEdit" class="save-btn" :disabled="!isFormValid">Save</button>
        <button @click="cancelEdit" class="cancel-btn">Cancel</button>
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
.character-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e9ea;
  transition: all 0.3s ease;
  text-align: left;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.character-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

/* Avatar Section */
.avatar-section {
  display: flex;
  justify-content: center;
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

.character-name {
  margin: 0 0 24px 0;
  color: #1a1a1a;
  font-size: 1.5em;
  font-weight: 700;
  text-align: center;
  border-bottom: 3px solid #007bff;
  padding-bottom: 8px;
}

/* Field Layout */
.character-fields {
  flex: 1;
}

.field-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.field-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.character-field {
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.character-field:last-child {
  border-bottom: none;
}

.field-label {
  font-weight: 700;
  color: #2c3e50;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 6px;
  text-align: center;
}

.field-value {
  margin: 0;
  color: #34495e;
  line-height: 1.5;
  min-height: 20px;
  font-size: 0.95em;
  text-align: center;
}

.background-text, .communication-text {
  text-align: left;
  font-style: italic;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

/* Tags Section */
.tags-section {
  border-top: 2px solid #e9ecef;
  padding-top: 16px;
  margin-top: 16px;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 8px;
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

.no-tags {
  color: #6c757d;
  font-style: italic;
  font-size: 0.9em;
  padding: 4px 8px;
  background: #f1f3f4;
  border-radius: 12px;
}

/* Actions */
.character-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 2px solid #e9ecef;
  justify-content: center;
}

.edit-btn, .delete-btn, .save-btn, .cancel-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.2s ease;
  min-width: 80px;
}

.edit-btn {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.edit-btn:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.delete-btn {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
}

.delete-btn:hover {
  background: linear-gradient(135deg, #c82333, #a71e2a);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);
}

.save-btn {
  background: linear-gradient(135deg, #28a745, #218838);
  color: white;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
}

.save-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  color: white;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.3);
}

.cancel-btn:hover {
  background: linear-gradient(135deg, #5a6268, #495057);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108, 117, 125, 0.4);
}

/* Edit Form Styles */
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

.edit-input, .edit-textarea, .edit-select {
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
  transition: all 0.2s ease;
  background: #f8f9fa;
}

.edit-input:focus, .edit-textarea:focus, .edit-select:focus {
  outline: none;
  border-color: #007bff;
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.edit-textarea {
  min-height: 80px;
  resize: vertical;
  font-family: inherit;
}

.background-field, .communication-field {
  position: relative;
}

.word-counter {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 0.75em;
  color: #6c757d;
  background: rgba(255, 255, 255, 0.95);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  border: 1px solid #e9ecef;
}

.word-counter.over-limit {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
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

.edit-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: center;
}

@media (max-width: 768px) {
  .field-columns, .edit-columns {
    grid-template-columns: 1fr;
  }
}
</style>
