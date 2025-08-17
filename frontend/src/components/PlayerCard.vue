<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="player-content">
      <!-- Avatar Section -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img
            v-if="player.avatar"
            :src="player.avatar"
            :alt="player.name"
            class="shared-avatar-image"
          />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(player.name) }}</span>
          </div>
        </div>
      </div>

      <!-- Name with Gender Emoji -->
      <h3 class="shared-title">{{ getGenderEmoji(player.gender) }} {{ player.name }}</h3>

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
              {{ (player.appearance || '').length }}/{{
                gameData.validation_limits.player_appearance
              }}
              characters
            </div>
          </div>
        </div>

        <!-- Player Abilities & Skills Section -->
        <div
          v-if="displayAbilitiesSkills && Object.keys(displayAbilitiesSkills).length > 0"
          class="shared-field shared-field-full-width"
        >
          <div class="shared-field-label">Abilities & Skills</div>
          <div class="shared-field-value">
            <TraitsDisplay
              :traits="displayAbilitiesSkills"
              :category-names="abilitiesSkillsCategoryNames"
              :value-classifier="getValueClass"
            />
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
            <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">
              {{ playerClass }}
            </option>
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
            <option v-for="alignment in alignments" :key="alignment" :value="alignment">
              {{ alignment }}
            </option>
          </select>
        </div>
      </div>

      <!-- Gender Field (Full Width) -->
      <select v-model="editForm.gender" class="shared-select">
        <option value="">Select Gender</option>
        <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
      </select>

      <!-- Appearance Field (Full Width) -->
      <div class="appearance-field">
        <label class="shared-field-label">Appearance</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.appearance"
          :placeholder="`Player appearance (max ${gameData.validation_limits.player_appearance} characters)`"
          :max-characters="gameData.validation_limits.player_appearance"
        />
      </div>

      <!-- Abilities Section -->
      <div class="abilities-skills-section">
        <h4 class="section-title">Abilities</h4>
        <div class="threshold-slider">
          <label class="threshold-label">Charisma: {{ editForm.abilities.Charisma || 0 }}</label>
          <input
            type="range"
            v-model.number="editForm.abilities.Charisma"
            min="0"
            max="30"
            step="1"
            class="slider"
          />
        </div>
      </div>

      <!-- Skills Section -->
      <div class="abilities-skills-section">
        <h4 class="section-title">Skills</h4>
        <div class="threshold-slider">
          <label class="threshold-label">Deception: {{ editForm.skills.Deception || 0 }}</label>
          <input
            type="range"
            v-model.number="editForm.skills.Deception"
            min="-5"
            max="25"
            step="1"
            class="slider"
          />
        </div>
        <div class="threshold-slider">
          <label class="threshold-label"
            >Intimidation: {{ editForm.skills.Intimidation || 0 }}</label
          >
          <input
            type="range"
            v-model.number="editForm.skills.Intimidation"
            min="-5"
            max="25"
            step="1"
            class="slider"
          />
        </div>
        <div class="threshold-slider">
          <label class="threshold-label">Performance: {{ editForm.skills.Performance || 0 }}</label>
          <input
            type="range"
            v-model.number="editForm.skills.Performance"
            min="-5"
            max="25"
            step="1"
            class="slider"
          />
        </div>
        <div class="threshold-slider">
          <label class="threshold-label">Persuasion: {{ editForm.skills.Persuasion || 0 }}</label>
          <input
            type="range"
            v-model.number="editForm.skills.Persuasion"
            min="-5"
            max="25"
            step="1"
            class="slider"
          />
        </div>
      </div>

      <div class="shared-actions">
        <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">
          Save
        </button>
        <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameData } from '../composables/useGameData.js'
  import { getInitials } from '../utils/avatarUtils.js'
  import AvatarUpload from './base/AvatarUpload.vue'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'

  export default {
    name: 'PlayerCard',
    components: {
      AvatarUpload,
      BaseTextareaWithCharacterCounter,
      TraitsDisplay,
    },
    props: {
      player: {
        type: Object,
        required: true,
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const { gameData } = useGameData()
      const isEditing = ref(false)

      // Abilities & Skills display functionality
      const displayAbilitiesSkills = ref({})

      const editForm = reactive({
        name: '',
        avatar: null,
        appearance: '',
        race: '',
        class_name: '',
        size: '',
        alignment: '',
        gender: '',
        abilities: {},
        skills: {},
      })

      const { isFormValid } = useFormValidation(editForm, 'PLAYER')

      const { genders, getGenderEmoji } = useDropdownOptions()

      const startEdit = () => {
        editForm.name = props.player.name || ''
        editForm.avatar = props.player.avatar || null
        editForm.appearance = props.player.appearance || ''
        editForm.race = props.player.race || ''
        editForm.class_name = props.player.class_name || ''
        editForm.size = props.player.size || ''
        editForm.alignment = props.player.alignment || ''
        editForm.gender = props.player.gender || ''
        // Initialize abilities with defaults
        editForm.abilities = {
          Charisma: props.player.abilities?.Charisma || 0,
        }
        // Initialize skills with defaults
        editForm.skills = {
          Deception: props.player.skills?.Deception || 0,
          Intimidation: props.player.skills?.Intimidation || 0,
          Performance: props.player.skills?.Performance || 0,
          Persuasion: props.player.skills?.Persuasion || 0,
        }
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
            alignment: editForm.alignment,
            gender: editForm.gender,
            abilities: editForm.abilities,
            skills: editForm.skills,
          })
          isEditing.value = false
        }
      }

      const deletePlayer = () => {
        if (confirm(`Are you sure you want to delete ${props.player.name}?`)) {
          emit('delete', props.player.id)
        }
      }

      const loadDisplayAbilitiesSkills = () => {
        const player = props.player
        const abilitiesSkills = {}

        // Add abilities if they exist
        if (player.abilities && Object.keys(player.abilities).length > 0) {
          abilitiesSkills.abilities = player.abilities
        }

        // Add skills if they exist
        if (player.skills && Object.keys(player.skills).length > 0) {
          abilitiesSkills.skills = player.skills
        }

        displayAbilitiesSkills.value = abilitiesSkills
      }

      const abilitiesSkillsCategoryNames = {
        abilities: 'Abilities',
        skills: 'Skills',
      }

      const getValueClass = (value, category) => {
        // For abilities and skills: green is positive, red is negative
        // These values are already modifiers, so use standard positive/negative logic
        if (value > 0) return 'bias-positive' // Green for positive values
        if (value < 0) return 'bias-negative' // Red for negative values
        return 'bias-neutral' // Gray for neutral (0) values
      }

      // Load display data when component mounts and when player changes
      onMounted(() => {
        loadDisplayAbilitiesSkills()
      })

      // Watch for player prop changes and reload abilities/skills
      watch(
        () => props.player.id,
        () => {
          loadDisplayAbilitiesSkills()
        }
      )

      // Watch for changes in player abilities and skills properties
      watch(
        () => [props.player.abilities, props.player.skills],
        () => {
          loadDisplayAbilitiesSkills()
        },
        { deep: true }
      )

      return {
        gameData,
        isEditing,
        editForm,
        races: computed(() => gameData.value.races),
        classes: computed(() => gameData.value.classes),
        genders,
        sizes: computed(() => gameData.value.sizes.player),
        alignments: computed(() => gameData.value.alignments),
        isFormValid,
        getInitials,
        getGenderEmoji,
        startEdit,
        cancelEdit,
        saveEdit,
        deletePlayer,
        displayAbilitiesSkills,
        abilitiesSkillsCategoryNames,
        getValueClass,
      }
    },
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

  .abilities-skills-section {
    margin-bottom: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .section-title {
    margin: 0 0 var(--spacing-lg) 0;
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    text-align: center;
  }

  /* TraitsDisplay component handles the display styling */

  .threshold-slider {
    margin-bottom: var(--spacing-lg);
  }

  .threshold-slider:last-child {
    margin-bottom: 0;
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-base);
    text-align: center;
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--border-default);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
    border: none;
  }

  /* Responsive styles handled by TraitsDisplay component */
</style>
