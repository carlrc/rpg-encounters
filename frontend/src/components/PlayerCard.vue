<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="player-content">
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
            
            <div class="shared-field">
              <label class="shared-field-label">Appearance</label>
              <p class="shared-field-value shared-text-italic">{{ player.appearance }}</p>
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
        
        <!-- Tags Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <label class="shared-field-label">Tags</label>
          <div class="shared-tags-display">
            <span 
              v-for="tag in player.tags" 
              :key="tag" 
              class="shared-tag-bubble"
            >
              {{ tag }}
            </span>
            <span v-if="!player.tags || player.tags.length === 0" class="shared-no-tags">
              No tags assigned
            </span>
          </div>
        </div>
      </div>
      
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deletePlayer" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>
    
    <div v-else class="shared-form">
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
          
          <div class="shared-word-counter-field">
            <textarea 
              v-model="editForm.appearance" 
              placeholder="Player appearance (max 40 words)"
              class="shared-textarea"
              @input="updateWordCount"
            ></textarea>
            <div class="shared-word-counter" :class="{ 'over-limit': wordCount > 40 }">
              {{ wordCount }}/40 words
            </div>
          </div>
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
/* PlayerCard now uses shared styles - minimal custom styles needed */
.player-fields {
  flex: 1;
}
</style>
