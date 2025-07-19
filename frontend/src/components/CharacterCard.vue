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

        <!-- Character Biases Section -->
        <div v-if="displayBiases && Object.keys(displayBiases).length > 0" class="shared-field shared-field-full-width">
          <div class="shared-field-label">Character Biases</div>
          <div class="shared-field-value">
            <div class="bias-display-grid">
              <div v-for="(preferences, category) in displayBiases" :key="category" class="bias-category-display">
                <div class="bias-category-title">{{ formatCategoryName(category) }}</div>
                <div class="bias-preferences-list">
                  <span 
                    v-for="(value, option) in preferences" 
                    :key="option"
                    class="bias-preference-item"
                    :class="getBiasClass(value)"
                  >
                    {{ option }}: {{ formatBiasValue(value) }}
                  </span>
                </div>
              </div>
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

      <!-- Character Biases Section -->
      <div class="bias-section">
        <h4 class="bias-section-title">Character Biases</h4>
        <p class="bias-section-description">Configure how this character feels about different player characteristics (±0.3 trust modifier each)</p>
        
        <!-- Race Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Race Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in editForm.biases.race_preferences"
            :key="`race-${index}`"
            :options="races"
            :used-options="editForm.biases.race_preferences.map(b => b.option)"
            :initial-option="bias.option"
            :initial-value="bias.value"
            placeholder="Select Race"
            @change="(option, val) => updateBiasPreference('race_preferences', index, option, val)"
            @remove="() => removeBiasPreference('race_preferences', index)"
          />
          <button 
            @click="addBiasPreference('race_preferences')" 
            class="bias-add-btn"
            type="button"
            v-if="editForm.biases.race_preferences.length < races.length"
          >
            + Add Race Preference
          </button>
        </div>

        <!-- Class Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Class Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in editForm.biases.class_preferences"
            :key="`class-${index}`"
            :options="classes"
            :used-options="editForm.biases.class_preferences.map(b => b.option)"
            :initial-option="bias.option"
            :initial-value="bias.value"
            placeholder="Select Class"
            @change="(option, val) => updateBiasPreference('class_preferences', index, option, val)"
            @remove="() => removeBiasPreference('class_preferences', index)"
          />
          <button 
            @click="addBiasPreference('class_preferences')" 
            class="bias-add-btn"
            type="button"
            v-if="editForm.biases.class_preferences.length < classes.length"
          >
            + Add Class Preference
          </button>
        </div>

        <!-- Gender Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Gender Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in editForm.biases.gender_preferences"
            :key="`gender-${index}`"
            :options="genders"
            :used-options="editForm.biases.gender_preferences.map(b => b.option)"
            :initial-option="bias.option"
            :initial-value="bias.value"
            placeholder="Select Gender"
            @change="(option, val) => updateBiasPreference('gender_preferences', index, option, val)"
            @remove="() => removeBiasPreference('gender_preferences', index)"
          />
          <button 
            @click="addBiasPreference('gender_preferences')" 
            class="bias-add-btn"
            type="button"
            v-if="editForm.biases.gender_preferences.length < genders.length"
          >
            + Add Gender Preference
          </button>
        </div>


        <!-- Size Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Size Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in editForm.biases.size_preferences"
            :key="`size-${index}`"
            :options="sizes"
            :used-options="editForm.biases.size_preferences.map(b => b.option)"
            :initial-option="bias.option"
            :initial-value="bias.value"
            placeholder="Select Size"
            @change="(option, val) => updateBiasPreference('size_preferences', index, option, val)"
            @remove="() => removeBiasPreference('size_preferences', index)"
          />
          <button 
            @click="addBiasPreference('size_preferences')" 
            class="bias-add-btn"
            type="button"
            v-if="editForm.biases.size_preferences.length < sizes.length"
          >
            + Add Size Preference
          </button>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { RACES, SIZES, ALIGNMENTS, CLASSES } from '../constants/gameData.js'
import { CHARACTER_LIMITS } from '../constants/validation.js'
import { useFormValidation } from '../utils/useFormValidation.js'
import { getInitials } from '../utils/avatarUtils.js'
import AvatarUpload from './base/AvatarUpload.vue'
import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
import BiasPreferenceRow from './BiasPreferenceRow.vue'
import apiService from '../services/api.js'

export default {
  name: 'CharacterCard',
  components: {
    AvatarUpload,
    BaseTextareaWithCharacterCounter,
    BiasPreferenceRow
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
      motivation: '',
      biases: {
        race_preferences: [],
        class_preferences: [],
        gender_preferences: [],
        size_preferences: []
      }
    })

    const { isFormValid } = useFormValidation(editForm, 'CHARACTER')

    // Gender options (not in gameData.js)
    const genders = ['male', 'female', 'nonbinary']

    const loadTrustProfile = () => {
      // Trust profiles are now part of the character model
      const character = props.character
      editForm.biases = {
        race_preferences: Object.entries(character.race_preferences || {}).map(([option, value]) => ({ option, value })),
        class_preferences: Object.entries(character.class_preferences || {}).map(([option, value]) => ({ option, value })),
        gender_preferences: Object.entries(character.gender_preferences || {}).map(([option, value]) => ({ option, value })),
        size_preferences: Object.entries(character.size_preferences || {}).map(([option, value]) => ({ option, value }))
      }
    }

    const startEdit = async () => {
      editForm.name = props.character.name || ''
      editForm.avatar = props.character.avatar || null
      editForm.race = props.character.race || ''
      editForm.size = props.character.size || ''
      editForm.alignment = props.character.alignment || ''
      editForm.profession = props.character.profession || ''
      editForm.background = props.character.background || ''
      editForm.communication_style = props.character.communication_style || ''
      editForm.motivation = props.character.motivation || ''
      
      // Load existing trust profile
      await loadTrustProfile()
      
      isEditing.value = true
    }

    const cancelEdit = () => {
      isEditing.value = false
    }

    const convertBiasesToObject = (arr) => {
      const obj = {}
      arr.forEach(({ option, value }) => {
        if (option) { // Only include items with valid options
          obj[option] = value
        }
      })
      return obj
    }

    const saveEdit = async () => {
      if (isFormValid.value) {
        // Save character data including trust profile fields
        emit('update', props.character.id, {
          name: editForm.name.trim(),
          avatar: editForm.avatar,
          race: editForm.race,
          size: editForm.size,
          alignment: editForm.alignment,
          profession: editForm.profession.trim(),
          background: editForm.background.trim(),
          communication_style: editForm.communication_style.trim(),
          motivation: editForm.motivation.trim(),
          // Include trust profile fields
          race_preferences: convertBiasesToObject(editForm.biases.race_preferences),
          class_preferences: convertBiasesToObject(editForm.biases.class_preferences),
          gender_preferences: convertBiasesToObject(editForm.biases.gender_preferences),
          size_preferences: convertBiasesToObject(editForm.biases.size_preferences),
          appearance_keywords: [],
          storytelling_keywords: []
        })
        
        // Refresh display biases to show the updated biases
        loadDisplayBiases()
        
        isEditing.value = false
      }
    }

    const addBiasPreference = (category) => {
      // Add a new empty preference object to the array
      editForm.biases[category].push({ option: '', value: 0.0 })
    }

    const updateBiasPreference = (category, index, option, value) => {
      if (editForm.biases[category][index]) {
        editForm.biases[category][index].option = option
        editForm.biases[category][index].value = value
      }
    }

    const removeBiasPreference = (category, index) => {
      editForm.biases[category].splice(index, 1)
    }

    const deleteCharacter = () => {
      if (confirm(`Are you sure you want to delete ${props.character.name}?`)) {
        emit('delete', props.character.id)
      }
    }

    // Bias display functionality
    const displayBiases = ref({})

    const loadDisplayBiases = () => {
      // Trust profiles are now part of the character model
      const character = props.character
      const biases = {}
      
      // Only include categories that have preferences
      if (character.race_preferences && Object.keys(character.race_preferences).length > 0) {
        biases.race_preferences = character.race_preferences
      }
      if (character.class_preferences && Object.keys(character.class_preferences).length > 0) {
        biases.class_preferences = character.class_preferences
      }
      if (character.gender_preferences && Object.keys(character.gender_preferences).length > 0) {
        biases.gender_preferences = character.gender_preferences
      }
      if (character.size_preferences && Object.keys(character.size_preferences).length > 0) {
        biases.size_preferences = character.size_preferences
      }
      
      displayBiases.value = biases
    }

    const formatCategoryName = (category) => {
      const names = {
        race_preferences: 'Race',
        class_preferences: 'Class',
        gender_preferences: 'Gender',
        alignment_preferences: 'Alignment',
        size_preferences: 'Size'
      }
      return names[category] || category
    }

    const formatBiasValue = (value) => {
      const sign = value >= 0 ? '+' : ''
      return `${sign}${value.toFixed(1)}`
    }

    const getBiasClass = (value) => {
      if (value > 0) return 'bias-positive'
      if (value < 0) return 'bias-negative'
      return 'bias-neutral'
    }

    // Computed properties for two-column layout
    const leftColumnBiases = computed(() => {
      const entries = Object.entries(displayBiases.value)
      const leftEntries = {}
      entries.forEach(([category, preferences], index) => {
        if (index % 2 === 0) {
          leftEntries[category] = preferences
        }
      })
      return leftEntries
    })

    const rightColumnBiases = computed(() => {
      const entries = Object.entries(displayBiases.value)
      const rightEntries = {}
      entries.forEach(([category, preferences], index) => {
        if (index % 2 === 1) {
          rightEntries[category] = preferences
        }
      })
      return rightEntries
    })

    // Load display biases when component mounts and when character changes
    onMounted(() => {
      loadDisplayBiases()
    })

    // Watch for character prop changes and reload biases
    watch(() => props.character.id, () => {
      loadDisplayBiases()
    })

    return {
      isEditing,
      editForm,
      races: RACES,
      classes: CLASSES,
      genders,
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
      addBiasPreference,
      updateBiasPreference,
      removeBiasPreference,
      deleteCharacter,
      displayBiases,
      leftColumnBiases,
      rightColumnBiases,
      formatCategoryName,
      formatBiasValue,
      getBiasClass
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

/* Bias Section Styles */
.bias-section {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.bias-section-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #495057;
}

.bias-section-description {
  margin: 0 0 1.5rem 0;
  font-size: 0.875rem;
  color: #6c757d;
  line-height: 1.4;
}

.bias-category {
  margin-bottom: 1.5rem;
}

.bias-category:last-child {
  margin-bottom: 0;
}

.bias-category-label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.bias-add-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-top: 0.5rem;
}

.bias-add-btn:hover {
  background: #0056b3;
}

.bias-add-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Bias Display Styles */
.bias-display-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.bias-category-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 80px;
  box-sizing: border-box;
  overflow: hidden;
}

.bias-category-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.bias-preferences-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  justify-content: center;
  width: 100%;
  max-width: 100%;
}

.bias-preference-item {
  display: inline-block;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  box-sizing: border-box;
}

/* Responsive design for bias grid */
@media (max-width: 768px) {
  .bias-display-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .bias-category-display {
    padding: 0.5rem;
    min-height: 60px;
  }
  
  .bias-preference-item {
    font-size: 0.7rem;
    padding: 0.15rem 0.3rem;
  }
}

.bias-preference-item.bias-positive {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.bias-preference-item.bias-negative {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.bias-preference-item.bias-neutral {
  background-color: #e2e3e5;
  border-color: #d6d8db;
  color: #383d41;
}
</style>
