<template>
  <div class="player-card">
    <div v-if="!isEditing" class="player-content">
      <h3 class="player-name">{{ player.name }}</h3>
      
      <div class="player-field">
        <label class="field-label">Appearance</label>
        <p class="field-value">{{ player.appearance }}</p>
      </div>
      
      <div class="player-field">
        <label class="field-label">Race</label>
        <p class="field-value">{{ player.race }}</p>
      </div>
      
      <div class="player-field">
        <label class="field-label">Class</label>
        <p class="field-value">{{ player.class_name }}</p>
      </div>
      
      <div class="player-field">
        <label class="field-label">Size</label>
        <p class="field-value">{{ player.size }}</p>
      </div>
      
      <div class="player-field">
        <label class="field-label">Alignment</label>
        <p class="field-value">{{ player.alignment }}</p>
      </div>
      
      <div class="player-field">
        <label class="field-label">Tags</label>
        <div class="tags-display">
          <span 
            v-for="tag in player.tags" 
            :key="tag" 
            class="tag-bubble"
          >
            {{ tag }}
          </span>
          <span v-if="!player.tags || player.tags.length === 0" class="no-tags">
            No tags assigned
          </span>
        </div>
      </div>
      
      <div class="player-actions">
        <button @click="startEdit" class="edit-btn">Edit</button>
        <button @click="deletePlayer" class="delete-btn">Delete</button>
      </div>
    </div>
    
    <div v-else class="player-edit-form">
      <input 
        v-model="editForm.name" 
        placeholder="Player name"
        class="edit-input"
      />
      
      <div class="appearance-field">
        <textarea 
          v-model="editForm.appearance" 
          placeholder="Player appearance"
          class="edit-textarea"
          @input="updateWordCount"
        ></textarea>
        <div class="word-counter" :class="{ 'over-limit': wordCount > 40 }">
          {{ wordCount }}/40 words
        </div>
      </div>
      
      <select v-model="editForm.race" class="edit-select">
        <option value="">Select Race</option>
        <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
      </select>
      
      <select v-model="editForm.class_name" class="edit-select">
        <option value="">Select Class</option>
        <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">{{ playerClass }}</option>
      </select>
      
      <select v-model="editForm.size" class="edit-select">
        <option value="">Select Size</option>
        <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
      </select>
      
      <select v-model="editForm.alignment" class="edit-select">
        <option value="">Select Alignment</option>
        <option v-for="alignment in alignments" :key="alignment" :value="alignment">{{ alignment }}</option>
      </select>
      
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
  name: 'PlayerCard',
  props: {
    player: {
      type: Object,
      required: true
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    const newTagInput = ref('')
    const wordCount = ref(0)
    
    const editForm = reactive({
      name: '',
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: '',
      tags: []
    })

    const races = [
      'Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
      'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'
    ]

    const classes = [
      'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 
      'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 
      'Warlock', 'Wizard'
    ]

    const sizes = [
      'Small', 'Medium'
    ]

    const alignments = [
      'Lawful Good', 'Neutral Good', 'Chaotic Good',
      'Lawful Neutral', 'True Neutral', 'Chaotic Neutral',
      'Lawful Evil', 'Neutral Evil', 'Chaotic Evil'
    ]

    const isFormValid = computed(() => {
      return editForm.name.trim() && 
             editForm.appearance.trim() && 
             editForm.race && 
             editForm.class_name &&
             editForm.size &&
             editForm.alignment &&
             wordCount.value <= 40
    })

    const updateWordCount = () => {
      wordCount.value = editForm.appearance.trim() ? editForm.appearance.trim().split(/\s+/).length : 0
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

    const startEdit = () => {
      editForm.name = props.player.name || ''
      editForm.appearance = props.player.appearance || ''
      editForm.race = props.player.race || ''
      editForm.class_name = props.player.class_name || ''
      editForm.size = props.player.size || ''
      editForm.alignment = props.player.alignment || ''
      editForm.tags = [...(props.player.tags || [])]
      updateWordCount()
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
      newTagInput.value = ''
      wordCount.value = 0
    }

    const saveEdit = () => {
      if (isFormValid.value) {
        emit('update', props.player.id, {
          name: editForm.name.trim(),
          appearance: editForm.appearance.trim(),
          race: editForm.race,
          class_name: editForm.class_name,
          size: editForm.size,
          alignment: editForm.alignment,
          tags: editForm.tags
        })
        isEditing.value = false
        newTagInput.value = ''
        wordCount.value = 0
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
      newTagInput,
      wordCount,
      races,
      classes,
      sizes,
      alignments,
      isFormValid,
      updateWordCount,
      addTag,
      removeTag,
      startEdit,
      cancelEdit,
      saveEdit,
      deletePlayer
    }
  }
}
</script>

<style scoped>
.player-card {
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

.player-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.player-name {
  height: 68px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  margin: 0 0 20px 0;
  color: #1a1a1a;
  font-size: 1.5em;
  font-weight: 700;
  border-bottom: 3px solid #007bff;
  padding-bottom: 8px;
  text-align: center;
  box-sizing: border-box;
}

.player-field {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.player-field:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.field-label {
  font-weight: 700;
  color: #2c3e50;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 8px;
  text-align: center;
}

.field-value {
  margin: 0;
  color: #34495e;
  line-height: 1.6;
  min-height: 22px;
  font-size: 1.05em;
  font-weight: 400;
  text-align: center;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-start;
  margin-top: 4px;
  justify-content: center;
}

.tag-bubble {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  transition: all 0.2s ease;
}

.tag-bubble:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.tag-bubble.editable {
  background: linear-gradient(135deg, #6c757d, #5a6268);
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 8px;
}

.remove-tag-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 1.1em;
  cursor: pointer;
  padding: 2px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-tag-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.no-tags {
  color: #6c757d;
  font-style: italic;
  font-size: 0.9em;
  padding: 4px 8px;
  background: #f1f3f4;
  border-radius: 12px;
}

.player-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
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

.edit-btn:active {
  transform: translateY(0);
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

.delete-btn:active {
  transform: translateY(0);
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

.save-btn:active:not(:disabled) {
  transform: translateY(0);
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

.cancel-btn:active {
  transform: translateY(0);
}

.player-edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  min-height: 90px;
  resize: vertical;
  font-family: inherit;
}

.appearance-field {
  position: relative;
}

.word-counter {
  position: absolute;
  bottom: 10px;
  right: 10px;
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

.add-tag-btn:active {
  transform: translateY(0);
}

.tags-edit-display {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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
</style>
