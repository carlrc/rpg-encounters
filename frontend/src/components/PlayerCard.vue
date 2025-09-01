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

      <!-- Player Names Section -->
      <div class="player-title-section">
        <h3 class="real-name">{{ player.rl_name }}</h3>
        <h4 class="character-name">{{ getGenderEmoji(player.gender) }} {{ player.name }}</h4>
      </div>

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
          <div class="shared-field-label">Ability & Skill Modifiers</div>
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
      <!-- Avatar Display (Read-only) -->
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

      <!-- Real Name -->
      <input
        v-model="editForm.rl_name"
        placeholder="Real-life player name"
        class="shared-input shared-input-name"
      />

      <!-- Character Name -->
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

      <!-- Ability Modifiers Section -->
      <div class="abilities-skills-section">
        <h4 class="section-title">Ability Modifiers</h4>
        <div class="threshold-slider">
          <label class="threshold-label">Charisma: {{ editForm.abilities.Charisma || 0 }}</label>
          <input
            type="range"
            v-model.number="editForm.abilities.Charisma"
            min="-5"
            max="10"
            step="1"
            class="slider"
          />
        </div>
      </div>

      <!-- Skill Modifiers Section -->
      <div class="abilities-skills-section">
        <h4 class="section-title">Skill Modifiers</h4>
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
  import { ref, reactive, computed, onMounted, onUnmounted, watch, watchEffect } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { getInitials } from '../utils/avatarUtils.js'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'

  export default {
    name: 'PlayerCard',
    components: {
      BaseTextareaWithCharacterCounter,
      TraitsDisplay,
    },
    props: {
      player: {
        type: Object,
        required: true,
        validator: (value) => {
          return (
            value &&
            typeof value.id !== 'undefined' &&
            typeof value.name === 'string' &&
            value.name.length > 0
          )
        },
      },
    },
    emits: ['update', 'delete'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const isEditing = ref(false)

      // Abilities & Skills display functionality
      const displayAbilitiesSkills = ref({})

      const editForm = reactive({
        name: '',
        rl_name: '',
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

      // Store cleanup functions for proper memory management
      const cleanupFunctions = []

      const startEdit = () => {
        editForm.name = props.player.name || ''
        editForm.rl_name = props.player.rl_name || ''
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
            rl_name: editForm.rl_name.trim(),
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
        abilities: 'Ability Modifiers',
        skills: 'Skill Modifiers',
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

      // Use watchEffect for automatic cleanup and better performance
      const stopPlayerIdWatcher = watchEffect(() => {
        if (props.player.id) {
          loadDisplayAbilitiesSkills()
        }
      })

      // Watch for changes in player abilities and skills properties with cleanup
      const stopAbilitiesSkillsWatcher = watch(
        () => [props.player.abilities, props.player.skills],
        () => {
          loadDisplayAbilitiesSkills()
        },
        { deep: true }
      )

      // Add watchers to cleanup functions
      cleanupFunctions.push(stopPlayerIdWatcher, stopAbilitiesSkillsWatcher)

      // Clean up on unmount to prevent memory leaks
      onUnmounted(() => {
        cleanupFunctions.forEach((cleanup) => cleanup())
      })

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
  /* Component-specific styles only - shared styles handled globally */
  .player-fields {
    flex: 1;
  }

  .appearance-field {
    margin-bottom: var(--spacing-lg);
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

  /* Player title section - custom layout for dual names */
  .player-title-section {
    margin: 0 0 var(--spacing-xxl) 0;
    text-align: center;
    border-bottom: 3px solid var(--primary-color);
    padding-bottom: var(--spacing-sm);
  }

  .real-name {
    margin: 0 0 var(--spacing-xs) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xxl);
    font-weight: var(--font-weight-bold);
  }

  .character-name {
    margin: 0;
    color: var(--text-muted);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    font-style: italic;
  }
</style>
