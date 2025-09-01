<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="character-content">
      <!-- Avatar Section -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img
            v-if="character.avatar"
            :src="character.avatar"
            :alt="character.name"
            class="shared-avatar-image"
          />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
        </div>
      </div>

      <!-- Name with Gender Emoji -->
      <h3 class="shared-title">{{ getGenderEmoji(character.gender) }} {{ character.name }}</h3>

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
              {{ (character.background || '').length }}/{{
                gameData.validation_limits.character_background
              }}
              characters
            </div>
          </div>
        </div>

        <!-- Communication Style Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Communication Style</div>
          <div class="shared-field-value">
            <div class="communication-style-display">
              <span class="communication-style-type">{{ character.communication_style_type }}</span>
              <div
                v-if="character.communication_style_type === 'Custom'"
                class="shared-text-display"
              >
                {{ character.communication_style }}
              </div>
            </div>
            <div
              v-if="character.communication_style_type === 'Custom'"
              class="character-limit-info"
            >
              {{ character.communication_style.length }}/{{
                gameData.validation_limits.character_communication
              }}
              characters
            </div>
          </div>
        </div>

        <!-- Motivation Section (Full Width) -->
        <div class="shared-field shared-field-full-width">
          <div class="shared-field-label">Motivation</div>
          <div class="shared-field-value">
            <div class="shared-text-display">{{ character.motivation }}</div>
            <div class="character-limit-info">
              {{ (character.motivation || '').length }}/{{
                gameData.validation_limits.character_motivation
              }}
              characters
            </div>
          </div>
        </div>

        <!-- Voice Section (Full Width) -->
        <div v-if="character.voice_id" class="shared-field shared-field-full-width">
          <div class="shared-field-label">Voice</div>
          <div class="shared-field-value">
            <div class="communication-style-display">
              <div class="voice-centered-container">
                <span class="communication-style-type">
                  {{ character.voice_name }}
                  <button
                    @click="playCharacterVoiceSample"
                    class="voice-preview-btn"
                    :disabled="previewLoading"
                    title="Play voice sample"
                  >
                    {{ previewLoading ? '⏳' : '▶️' }}
                  </button>
                </span>
              </div>
              <div class="preset-communication-style">ID: {{ character.voice_id }}</div>
            </div>
          </div>
        </div>

        <!-- Character Biases Section -->
        <div
          v-if="displayBiases && Object.keys(displayBiases).length > 0"
          class="shared-field shared-field-full-width"
        >
          <div class="shared-field-label">Character Biases</div>
          <div class="shared-field-value">
            <TraitsDisplay
              :traits="displayBiases"
              :category-names="biasesCategoryNames"
              :value-classifier="getBiasClass"
            />
          </div>
        </div>
      </div>

      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deleteCharacter" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else class="shared-form">
      <!-- Avatar Display (Read-only) -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img
            v-if="character.avatar"
            :src="character.avatar"
            :alt="character.name"
            class="shared-avatar-image"
          />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
        </div>
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
            <option v-for="alignment in alignments" :key="alignment" :value="alignment">
              {{ alignment }}
            </option>
          </select>
        </div>

        <!-- Right Column -->
        <div class="shared-field-column">
          <select v-model="editForm.size" class="shared-select">
            <option value="">Select Size</option>
            <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
          </select>

          <select v-model="editForm.gender" class="shared-select">
            <option value="">Select Gender</option>
            <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
          </select>
        </div>
      </div>

      <!-- Profession Field (Full Width) -->
      <input v-model="editForm.profession" placeholder="Profession" class="shared-input" />

      <!-- Background Field (Full Width) -->
      <div class="shared-field shared-field-full-width">
        <label class="shared-field-label">Background</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.background"
          :placeholder="`Character background (max ${gameData.validation_limits.character_background} characters)`"
          :max-characters="gameData.validation_limits.character_background"
        />
      </div>

      <!-- Communication Style Field (Full Width) -->
      <div class="shared-field shared-field-full-width">
        <label class="shared-field-label">Communication Style</label>
        <select
          v-model="editForm.communication_style_type"
          class="shared-select"
          @change="handleCommunicationStyleTypeChange"
        >
          <option value="">Select Communication Style</option>
          <option v-for="style in gameData.communication_styles" :key="style" :value="style">
            {{ style }}
          </option>
        </select>

        <!-- Custom Communication Style Textarea -->
        <div
          v-if="editForm.communication_style_type === 'Custom'"
          class="custom-communication-style"
        >
          <BaseTextareaWithCharacterCounter
            v-model="editForm.communication_style"
            :placeholder="`Describe custom communication style (max ${gameData.validation_limits.character_communication} characters)`"
            :max-characters="gameData.validation_limits.character_communication"
          />
        </div>
      </div>

      <!-- Motivation Field (Full Width) -->
      <div class="shared-field shared-field-full-width">
        <label class="shared-field-label">Motivation</label>
        <BaseTextareaWithCharacterCounter
          v-model="editForm.motivation"
          :placeholder="`Character motivation (max ${gameData.validation_limits.character_motivation} characters)`"
          :max-characters="gameData.validation_limits.character_motivation"
        />
      </div>

      <!-- Voice Selection Field (Full Width) -->
      <VoiceSelector
        :current-voice-id="editForm.voice_id"
        :current-voice-name="editForm.voice_name"
        @select-voice="handleVoiceSelection"
      />

      <!-- Character Biases Section -->
      <div class="shared-field shared-field-full-width">
        <div class="shared-field-label">Character Biases</div>
        <div class="shared-field-value">
          <p class="bias-section-description">
            Configure how this character feels about different player characteristics (±5 DC
            influence modifier each)
          </p>

          <!-- Race Preferences -->
          <div class="bias-category">
            <label class="bias-category-label">Race Preferences</label>
            <BiasPreferenceRow
              v-for="(bias, index) in editForm.biases.race_preferences"
              :key="`race-${index}`"
              :options="gameData.races"
              :used-options="editForm.biases.race_preferences.map((b) => b.option)"
              :initial-option="bias.option"
              :initial-value="bias.value"
              placeholder="Select Race"
              @change="(option, val) => handleRaceBiasChange(index, option, val)"
              @remove="() => handleRaceBiasRemove(index)"
            />
            <button
              @click="addBiasPreference('race_preferences')"
              class="shared-add-btn"
              type="button"
              v-if="editForm.biases.race_preferences.length < gameData.races.length"
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
              :options="gameData.classes"
              :used-options="editForm.biases.class_preferences.map((b) => b.option)"
              :initial-option="bias.option"
              :initial-value="bias.value"
              placeholder="Select Class"
              @change="(option, val) => handleClassBiasChange(index, option, val)"
              @remove="() => handleClassBiasRemove(index)"
            />
            <button
              @click="addBiasPreference('class_preferences')"
              class="shared-add-btn"
              type="button"
              v-if="editForm.biases.class_preferences.length < gameData.classes.length"
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
              :used-options="editForm.biases.gender_preferences.map((b) => b.option)"
              :initial-option="bias.option"
              :initial-value="bias.value"
              placeholder="Select Gender"
              @change="(option, val) => handleGenderBiasChange(index, option, val)"
              @remove="() => handleGenderBiasRemove(index)"
            />
            <button
              @click="addBiasPreference('gender_preferences')"
              class="shared-add-btn"
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
              :options="gameData.sizes.character"
              :used-options="editForm.biases.size_preferences.map((b) => b.option)"
              :initial-option="bias.option"
              :initial-value="bias.value"
              placeholder="Select Size"
              @change="(option, val) => handleSizeBiasChange(index, option, val)"
              @remove="() => handleSizeBiasRemove(index)"
            />
            <button
              @click="addBiasPreference('size_preferences')"
              class="shared-add-btn"
              type="button"
              v-if="editForm.biases.size_preferences.length < gameData.sizes.character.length"
            >
              + Add Size Preference
            </button>
          </div>
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

<script setup>
  import { ref, reactive, computed, onMounted, onUnmounted, watch, watchEffect } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useAudioPlayer } from '../composables/useAudioPlayer.js'
  import { getInitials } from '../utils/avatarUtils.js'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import BiasPreferenceRow from './BiasPreferenceRow.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'
  import VoiceSelector from './VoiceSelector.vue'
  import { getVoiceSample } from '../services/api.js'

  const props = defineProps({
    character: {
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
  })

  const emit = defineEmits(['update', 'delete'])

  const gameDataStore = useGameDataStore()
  const { data: gameData } = storeToRefs(gameDataStore)
  const { playStreamingResponse, isLoading: previewLoading } = useAudioPlayer()
  const isEditing = ref(false)

  const editForm = reactive({
    name: '',
    race: '',
    size: '',
    alignment: '',
    gender: '',
    profession: '',
    background: '',
    communication_style: '',
    communication_style_type: 'Custom',
    motivation: '',
    voice_id: '',
    voice_name: '',
    biases: {
      race_preferences: [],
      class_preferences: [],
      gender_preferences: [],
      size_preferences: [],
    },
  })

  const { isFormValid } = useFormValidation(editForm, 'CHARACTER')

  const { genders, getGenderEmoji } = useDropdownOptions()

  // Store cleanup functions for proper memory management
  const cleanupFunctions = []

  // Store original AI-triggering field values to detect changes
  const originalAIFields = ref({
    background: '',
    motivation: '',
    communication_style: '',
    communication_style_type: '',
  })

  // Computed properties
  const races = computed(() => gameData.value.races)
  const classes = computed(() => gameData.value.classes)
  const sizes = computed(() => gameData.value.sizes.character)
  const alignments = computed(() => gameData.value.alignments)

  const loadInfluenceProfile = () => {
    // Influence profiles are now part of the character model
    const character = props.character
    editForm.biases = {
      race_preferences: Object.entries(character.race_preferences || {}).map(([option, value]) => ({
        option,
        value,
      })),
      class_preferences: Object.entries(character.class_preferences || {}).map(
        ([option, value]) => ({ option, value })
      ),
      gender_preferences: Object.entries(character.gender_preferences || {}).map(
        ([option, value]) => ({ option, value })
      ),
      size_preferences: Object.entries(character.size_preferences || {}).map(([option, value]) => ({
        option,
        value,
      })),
    }
  }

  const startEdit = async () => {
    editForm.name = props.character.name || ''
    editForm.race = props.character.race || ''
    editForm.size = props.character.size || ''
    editForm.alignment = props.character.alignment || ''
    editForm.gender = props.character.gender || ''
    editForm.profession = props.character.profession || ''
    editForm.background = props.character.background || ''
    editForm.communication_style = props.character.communication_style || ''
    editForm.communication_style_type = props.character.communication_style_type || 'Custom'

    // If no communication_style_type is set but there's communication_style content,
    // it's likely an existing custom style
    if (!props.character.communication_style_type && props.character.communication_style) {
      editForm.communication_style_type = 'Custom'
    }
    editForm.motivation = props.character.motivation || ''
    editForm.voice_id = props.character.voice_id || ''
    editForm.voice_name = props.character.voice_name || ''

    // Store original AI-triggering field values for change detection
    originalAIFields.value = {
      background: props.character.background || '',
      motivation: props.character.motivation || '',
      communication_style: props.character.communication_style || '',
      communication_style_type: props.character.communication_style_type || 'Custom',
    }

    // Load existing influence profile
    await loadInfluenceProfile()

    isEditing.value = true
  }

  const cancelEdit = () => {
    isEditing.value = false
  }

  const convertBiasesToObject = (arr) => {
    const obj = {}
    arr.forEach(({ option, value }) => {
      if (option) {
        // Only include items with valid options
        obj[option] = value
      }
    })
    return obj
  }

  const saveEdit = async () => {
    if (isFormValid.value) {
      // Always send non-AI-triggering fields
      const updateData = {
        name: editForm.name.trim(),
        race: editForm.race,
        size: editForm.size,
        alignment: editForm.alignment,
        gender: editForm.gender,
        profession: editForm.profession.trim(),
        voice_id: editForm.voice_id || '',
        voice_name: editForm.voice_name || '',
        // Include bias profile fields
        race_preferences: convertBiasesToObject(editForm.biases.race_preferences),
        class_preferences: convertBiasesToObject(editForm.biases.class_preferences),
        gender_preferences: convertBiasesToObject(editForm.biases.gender_preferences),
        size_preferences: convertBiasesToObject(editForm.biases.size_preferences),
        appearance_keywords: [],
        storytelling_keywords: [],
      }

      // Only include AI-triggering fields if they've changed
      const currentBackground = editForm.background.trim()
      const currentMotivation = editForm.motivation.trim()
      const currentCommStyle = (editForm.communication_style || '').trim()
      const currentCommStyleType = editForm.communication_style_type

      if (currentBackground !== originalAIFields.value.background) {
        updateData.background = currentBackground
      }

      if (currentMotivation !== originalAIFields.value.motivation) {
        updateData.motivation = currentMotivation
      }

      if (currentCommStyle !== originalAIFields.value.communication_style) {
        updateData.communication_style = currentCommStyle
      }

      if (currentCommStyleType !== originalAIFields.value.communication_style_type) {
        updateData.communication_style_type = currentCommStyleType
      }

      emit('update', props.character.id, updateData)

      isEditing.value = false
    }
  }

  const addBiasPreference = (category) => {
    // Add a new empty preference object to the array
    editForm.biases[category].push({ option: '', value: 0 })
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

  // Specific handler methods to avoid inline arrow functions
  const handleRaceBiasChange = (index, option, value) => {
    updateBiasPreference('race_preferences', index, option, value)
  }

  const handleRaceBiasRemove = (index) => {
    removeBiasPreference('race_preferences', index)
  }

  const handleClassBiasChange = (index, option, value) => {
    updateBiasPreference('class_preferences', index, option, value)
  }

  const handleClassBiasRemove = (index) => {
    removeBiasPreference('class_preferences', index)
  }

  const handleGenderBiasChange = (index, option, value) => {
    updateBiasPreference('gender_preferences', index, option, value)
  }

  const handleGenderBiasRemove = (index) => {
    removeBiasPreference('gender_preferences', index)
  }

  const handleSizeBiasChange = (index, option, value) => {
    updateBiasPreference('size_preferences', index, option, value)
  }

  const handleSizeBiasRemove = (index) => {
    removeBiasPreference('size_preferences', index)
  }

  // Watch for communication style type changes
  const handleCommunicationStyleTypeChange = () => {
    // Clear communication_style when switching away from Custom
    if (editForm.communication_style_type !== 'Custom') {
      editForm.communication_style = ''
    }
  }

  // Handle voice selection
  const handleVoiceSelection = (voice) => {
    editForm.voice_id = voice.voice_id
    editForm.voice_name = voice.name
  }

  // Voice preview method
  const playCharacterVoiceSample = async () => {
    if (!props.character.voice_id || previewLoading.value) return

    try {
      const response = await getVoiceSample(props.character.voice_id)
      await playStreamingResponse(response, `character-${props.character.id}`)
    } catch (err) {
      console.error('Failed to play character voice sample:', err)
    }
  }

  const deleteCharacter = () => {
    if (confirm(`Are you sure you want to delete ${props.character.name}?`)) {
      emit('delete', props.character.id)
    }
  }

  // Bias display functionality
  const displayBiases = ref({})

  const loadDisplayBiases = () => {
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

  const biasesCategoryNames = {
    race_preferences: 'Race',
    class_preferences: 'Class',
    gender_preferences: 'Gender',
    alignment_preferences: 'Alignment',
    size_preferences: 'Size',
  }

  const getBiasClass = (value) => {
    if (value > 0) return 'bias-positive'
    if (value < 0) return 'bias-negative'
    return 'bias-neutral'
  }

  // Load display biases when component mounts and when character changes
  onMounted(() => {
    loadDisplayBiases()
  })

  // Use watchEffect for automatic cleanup and better performance
  const stopCharacterIdWatcher = watchEffect(() => {
    if (props.character.id) {
      loadDisplayBiases()
    }
  })

  // Watch for changes in character bias properties with cleanup
  const stopBiasWatcher = watch(
    () => [
      props.character.race_preferences,
      props.character.class_preferences,
      props.character.gender_preferences,
      props.character.size_preferences,
    ],
    () => {
      loadDisplayBiases()
    },
    { deep: true }
  )

  // Add watchers to cleanup functions
  cleanupFunctions.push(stopCharacterIdWatcher, stopBiasWatcher)

  // Clean up on unmount to prevent memory leaks
  onUnmounted(() => {
    cleanupFunctions.forEach((cleanup) => cleanup())
  })

  // Watch communication style type changes to clear custom input
  watch(() => editForm.communication_style_type, handleCommunicationStyleTypeChange)
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .character-fields {
    flex: 1;
  }

  .custom-communication-style {
    margin-top: var(--spacing-md);
  }

  .communication-style-display {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .communication-style-type {
    font-weight: var(--font-weight-semibold);
    color: var(--primary-color);
    font-size: var(--font-size-base);
    padding: var(--spacing-xs) var(--spacing-sm);
    background-color: var(--bg-light);
    border-radius: var(--radius-sm);
    display: block;
    width: fit-content;
    margin: 0 auto;
    text-align: center;
  }

  .preset-communication-style {
    font-style: italic;
    color: var(--text-muted);
    font-size: var(--font-size-base);
    margin-top: var(--spacing-xs);
  }

  /* Voice display - component-specific functionality only */
  .voice-centered-container {
    display: flex;
    justify-content: center;
  }

  .voice-preview-btn {
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    transition: transform var(--transition-fast);
    margin-left: var(--spacing-sm);
    padding: var(--spacing-xs);
  }

  .voice-preview-btn:hover:not(:disabled) {
    transform: scale(1.1);
  }

  .voice-preview-btn:disabled {
    cursor: not-allowed;
    transform: none;
    opacity: 0.6;
  }
</style>
