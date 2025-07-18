<template>
  <div class="shared-card nugget-card">
    <div v-if="!isEditing" class="nugget-display">
      <!-- Character Name -->
      <h2 class="shared-title">{{ getCharacterName(nugget.character_id) }}</h2>
      
      <!-- Trust Level Circles -->
      <div class="circle-row">
        <div 
          v-for="level in 3" 
          :key="level"
          class="secret-circle"
          :class="{ 
            'unlocked': isLevelUnlocked(level), 
            'locked': !isLevelUnlocked(level),
            'current': nugget.layer === level
          }"
        >
          <div class="tooltip">
            Level {{ level }}: {{ getLevelDescription(level) }}
            <div v-if="nugget.layer === level" class="tooltip-content">
              {{ nugget.content }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="label">Trust Level Secrets</div>
      
      <!-- Nugget Details -->
      <div class="shared-field">
        <div class="shared-field-label">Trust Level</div>
        <div class="shared-field-value">
          <span class="trust-level-badge" :class="`level-${nugget.layer}`">
            Level {{ nugget.layer }}: {{ getLevelName(nugget.layer) }}
          </span>
        </div>
      </div>
      
      <!-- Nugget Content -->
      <div class="shared-field shared-field-full-width">
        <div class="shared-field-label">Secret Content</div>
        <div class="shared-field-value">
          <div class="shared-text-display">{{ nugget.content }}</div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="confirmDelete" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>
    
    <div v-else class="nugget-edit">
      <!-- Edit Form -->
      <div class="shared-form">
        <!-- Character Selection -->
        <div class="character-field">
          <label class="shared-field-label">Character</label>
          <select v-model="editForm.character_id" class="shared-select">
            <option value="">Select character...</option>
            <option 
              v-for="character in characters" 
              :key="character.id" 
              :value="character.id"
            >
              {{ character.name }}
            </option>
          </select>
        </div>
        
        <!-- Trust Level Selection -->
        <div class="trust-level-field">
          <label class="shared-field-label">Trust Level</label>
          <div class="trust-level-options">
            <label 
              v-for="level in 3" 
              :key="level"
              class="trust-level-option"
              :class="{ active: editForm.layer === level }"
            >
              <input 
                type="radio" 
                :value="level" 
                v-model="editForm.layer"
              />
              <div class="trust-level-info">
                <div class="trust-level-name">Level {{ level }}: {{ getLevelName(level) }}</div>
                <div class="trust-level-desc">{{ getLevelDescription(level) }}</div>
              </div>
            </label>
          </div>
        </div>
        
        <!-- Content -->
        <div class="content-field">
          <label class="shared-field-label">Secret Content</label>
          <BaseTextareaWithCharacterCounter
            v-model="editForm.content"
            placeholder="Enter the secret content for this trust level..."
            :max-characters="500"
          />
        </div>
        
        <!-- Actions -->
        <div class="shared-actions">
          <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">Save</button>
          <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'

export default {
  name: 'NuggetCard',
  components: {
    BaseTextareaWithCharacterCounter
  },
  props: {
    nugget: {
      type: Object,
      required: true
    },
    characters: {
      type: Array,
      default: () => []
    },
    currentTrustLevel: {
      type: Number,
      default: 0
    }
  },
  emits: ['update', 'delete'],
  setup(props, { emit }) {
    const isEditing = ref(false)
    const editForm = reactive({
      character_id: 0,
      layer: 1,
      content: ''
    })
    
    const isFormValid = computed(() => {
      return editForm.character_id && 
             editForm.layer && 
             editForm.content.trim() && 
             editForm.content.length <= 500
    })
    
    const getCharacterName = (characterId) => {
      const character = props.characters.find(c => c.id === characterId)
      return character ? character.name : `Character ${characterId}`
    }
    
    const getLevelName = (level) => {
      const names = {
        1: 'Public',
        2: 'Privileged', 
        3: 'Exclusive'
      }
      return names[level] || 'Unknown'
    }
    
    const getLevelDescription = (level) => {
      const descriptions = {
        1: 'Always accessible',
        2: 'High trust required',
        3: 'Maximum trust required'
      }
      return descriptions[level] || 'Unknown level'
    }
    
    const isLevelUnlocked = (level) => {
      // For display purposes, show if this level would be accessible
      // This is a simplified version - in a real app you'd calculate based on actual trust
      const thresholds = { 1: 0.0, 2: 0.55, 3: 0.8 }
      return props.currentTrustLevel >= thresholds[level]
    }
    
    const startEdit = () => {
      Object.assign(editForm, {
        character_id: props.nugget.character_id,
        layer: props.nugget.layer,
        content: props.nugget.content
      })
      isEditing.value = true
    }
    
    const cancelEdit = () => {
      isEditing.value = false
    }
    
    const saveEdit = () => {
      if (isFormValid.value) {
        emit('update', props.nugget.id, {
          character_id: editForm.character_id,
          layer: editForm.layer,
          content: editForm.content.trim()
        })
        isEditing.value = false
      }
    }
    
    const confirmDelete = () => {
      const characterName = getCharacterName(props.nugget.character_id)
      const levelName = getLevelName(props.nugget.layer)
      if (confirm(`Are you sure you want to delete the ${levelName} secret for ${characterName}?`)) {
        emit('delete', props.nugget.id)
      }
    }
    
    return {
      isEditing,
      editForm,
      isFormValid,
      getCharacterName,
      getLevelName,
      getLevelDescription,
      isLevelUnlocked,
      startEdit,
      cancelEdit,
      saveEdit,
      confirmDelete
    }
  }
}
</script>

<style scoped>
.nugget-card {
  background-color: #2a2a2a;
  color: #f1f1f1;
}

.circle-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 2rem 0;
}

.secret-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #444;
  position: relative;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.secret-circle.locked::before {
  content: "🔒";
}

.secret-circle.unlocked::before {
  content: "🧠";
}

.secret-circle.current {
  background: #007bff;
  box-shadow: 0 0 12px rgba(0, 123, 255, 0.5);
}

.secret-circle:hover .tooltip {
  opacity: 1;
  transform: translateY(-10px);
}

.tooltip {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: #222;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  white-space: nowrap;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
  font-size: 0.85rem;
  color: #ddd;
  z-index: 10;
  min-width: 200px;
  text-align: center;
}

.tooltip-content {
  margin-top: 0.5rem;
  font-style: italic;
  white-space: normal;
  max-width: 250px;
}

.label {
  text-align: center;
  font-size: 1rem;
  color: #aaa;
  margin-top: -1rem;
  margin-bottom: 2rem;
}

.trust-level-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.trust-level-badge.level-1 {
  background: #28a745;
  color: white;
}

.trust-level-badge.level-2 {
  background: #ffc107;
  color: #212529;
}

.trust-level-badge.level-3 {
  background: #dc3545;
  color: white;
}

.character-field,
.trust-level-field,
.content-field {
  margin-bottom: 1.5rem;
}

.trust-level-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trust-level-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.trust-level-option:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.trust-level-option.active {
  border-color: #007bff;
  background: #e3f2fd;
}

.trust-level-option input[type="radio"] {
  margin: 0;
}

.trust-level-info {
  flex: 1;
}

.trust-level-name {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.trust-level-desc {
  font-size: 0.875rem;
  color: #6c757d;
}

.trust-level-option.active .trust-level-name {
  color: #007bff;
}
</style>
