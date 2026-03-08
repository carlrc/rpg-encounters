<template>
  <div class="shared-form">
    <!-- Name -->
    <input
      v-model="form.name"
      placeholder="Character name"
      class="shared-input shared-input-name"
    />

    <!-- Two Column Layout -->
    <div class="shared-field-columns">
      <!-- Left Column -->
      <div class="shared-field-column">
        <select v-model="form.race" class="shared-select">
          <option value="">Select Race</option>
          <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
        </select>

        <select v-model="form.alignment" class="shared-select">
          <option value="">Select Alignment</option>
          <option v-for="alignment in alignments" :key="alignment" :value="alignment">
            {{ alignment }}
          </option>
        </select>
      </div>

      <!-- Right Column -->
      <div class="shared-field-column">
        <select v-model="form.size" class="shared-select">
          <option value="">Select Size</option>
          <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
        </select>

        <select v-model="form.gender" class="shared-select">
          <option value="">Select Gender</option>
          <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
        </select>
      </div>
    </div>

    <!-- Profession Field (Full Width) -->
    <input v-model="form.profession" placeholder="Profession" class="shared-input" />

    <!-- Background Field (Full Width) -->
    <div class="shared-field shared-field-full-width">
      <label class="shared-field-label">Background</label>
      <BaseTextareaWithCharacterCounter
        v-model="form.background"
        :placeholder="`Character background (max ${gameData.validation_limits.character_background} characters)`"
        :max-characters="gameData.validation_limits.character_background"
      />
    </div>

    <!-- Communication Style Field (Full Width) -->
    <div class="shared-field shared-field-full-width">
      <label class="shared-field-label">Communication Style</label>
      <select
        v-model="form.communication_style_type"
        class="shared-select"
        @change="handleCommunicationStyleTypeChange"
      >
        <option value="">Select Communication Style</option>
        <option v-for="style in gameData.communication_styles" :key="style" :value="style">
          {{ style }}
        </option>
      </select>

      <!-- Custom Communication Style Textarea -->
      <div v-if="form.communication_style_type === 'Custom'" class="custom-communication-style">
        <BaseTextareaWithCharacterCounter
          v-model="form.communication_style"
          :placeholder="`Describe custom communication style (max ${gameData.validation_limits.character_communication} characters)`"
          :max-characters="gameData.validation_limits.character_communication"
        />
      </div>
    </div>

    <!-- Motivation Field (Full Width) -->
    <div class="shared-field shared-field-full-width">
      <label class="shared-field-label">Motivation</label>
      <BaseTextareaWithCharacterCounter
        v-model="form.motivation"
        :placeholder="`Character motivation (max ${gameData.validation_limits.character_motivation} characters)`"
        :max-characters="gameData.validation_limits.character_motivation"
      />
    </div>

    <!-- Voice Selection Field (Full Width) -->
    <VoiceSelector
      :current-voice-id="form.voice_id"
      :current-voice-name="form.voice_name"
      :current-provider="form.tts_provider"
      @select-voice="handleVoiceSelection"
      @select-provider="handleProviderSelection"
    />

    <!-- Character Biases Section -->
    <div class="shared-field shared-field-full-width">
      <div class="shared-field-label">Character Biases</div>
      <div class="shared-field-value">
        <p class="bias-section-description">
          Configure how this character feels about different player characteristics (±5 DC influence
          modifier each)
        </p>

        <!-- Race Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Race Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in form.biases.race_preferences"
            :key="`race-${index}`"
            :options="gameData.races"
            :used-options="form.biases.race_preferences.map((b) => b.option)"
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
            v-if="form.biases.race_preferences.length < gameData.races.length"
          >
            + Add Race Preference
          </button>
        </div>

        <!-- Class Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Class Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in form.biases.class_preferences"
            :key="`class-${index}`"
            :options="gameData.classes"
            :used-options="form.biases.class_preferences.map((b) => b.option)"
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
            v-if="form.biases.class_preferences.length < gameData.classes.length"
          >
            + Add Class Preference
          </button>
        </div>

        <!-- Gender Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Gender Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in form.biases.gender_preferences"
            :key="`gender-${index}`"
            :options="genders"
            :used-options="form.biases.gender_preferences.map((b) => b.option)"
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
            v-if="form.biases.gender_preferences.length < genders.length"
          >
            + Add Gender Preference
          </button>
        </div>

        <!-- Size Preferences -->
        <div class="bias-category">
          <label class="bias-category-label">Size Preferences</label>
          <BiasPreferenceRow
            v-for="(bias, index) in form.biases.size_preferences"
            :key="`size-${index}`"
            :options="gameData.sizes.character"
            :used-options="form.biases.size_preferences.map((b) => b.option)"
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
            v-if="form.biases.size_preferences.length < gameData.sizes.character.length"
          >
            + Add Size Preference
          </button>
        </div>
      </div>
    </div>

    <div class="shared-actions">
      <button @click="handleSave" class="shared-btn shared-btn-success" :disabled="!isFormValid">
        {{ isEditing ? 'Save' : 'Create' }}
      </button>
      <button @click="handleCancel" class="shared-btn shared-btn-secondary">Cancel</button>
    </div>
  </div>
</template>

<script>
  import { reactive, computed, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useFormValidation } from '../utils/useFormValidation'
  import { useDropdownOptions } from '../composables/useDropdownOptions'
  import { sanitizeDisplayName } from '../utils/nameUtils'
  import { useGameDataStore } from '../stores/gameData'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import BiasPreferenceRow from './BiasPreferenceRow.vue'
  import VoiceSelector from './VoiceSelector.vue'

  export default {
    name: 'CharacterForm',
    components: {
      BaseTextareaWithCharacterCounter,
      BiasPreferenceRow,
      VoiceSelector,
    },
    props: {
      initialData: {
        type: Object,
        default: () => ({}),
      },
      isEditing: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['save', 'cancel'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const { genders } = useDropdownOptions()

      // Initialize form with either initial data or empty values
      const form = reactive({
        name: props.initialData.name || '',
        race: props.initialData.race || '',
        size: props.initialData.size || '',
        alignment: props.initialData.alignment || '',
        gender: props.initialData.gender || '',
        profession: props.initialData.profession || '',
        background: props.initialData.background || '',
        communication_style: props.initialData.communication_style || '',
        communication_style_type: props.initialData.communication_style_type || 'Custom',
        motivation: props.initialData.motivation || '',
        voice_id: props.initialData.voice_id,
        voice_name: props.initialData.voice_name,
        tts_provider: props.initialData.tts_provider,
        biases: {
          race_preferences: Object.entries(props.initialData.race_preferences || {}).map(
            ([option, value]) => ({ option, value })
          ),
          class_preferences: Object.entries(props.initialData.class_preferences || {}).map(
            ([option, value]) => ({ option, value })
          ),
          gender_preferences: Object.entries(props.initialData.gender_preferences || {}).map(
            ([option, value]) => ({ option, value })
          ),
          size_preferences: Object.entries(props.initialData.size_preferences || {}).map(
            ([option, value]) => ({ option, value })
          ),
        },
      })

      const { isFormValid } = useFormValidation(form, 'CHARACTER')

      // Bias management methods
      const addBiasPreference = (category) => {
        form.biases[category].push({ option: '', value: 0 })
      }

      const updateBiasPreference = (category, index, option, value) => {
        if (form.biases[category][index]) {
          form.biases[category][index].option = option
          form.biases[category][index].value = value
        }
      }

      const removeBiasPreference = (category, index) => {
        form.biases[category].splice(index, 1)
      }

      // Specific handler methods
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

      // Communication style handling
      const handleCommunicationStyleTypeChange = () => {
        if (form.communication_style_type !== 'Custom') {
          form.communication_style = ''
        }
      }

      // Voice selection
      const handleVoiceSelection = (voice) => {
        form.voice_id = voice.voice_id
        form.voice_name = voice.name
      }

      // Provider selection
      const handleProviderSelection = (provider) => {
        form.tts_provider = provider
      }

      // Convert biases from array to object format for API
      const convertBiasesToObject = (arr) => {
        const obj = {}
        arr.forEach(({ option, value }) => {
          if (option) {
            obj[option] = value
          }
        })
        return obj
      }

      // Form actions
      const handleSave = () => {
        if (isFormValid.value) {
          const formData = {
            ...form,
            name: sanitizeDisplayName(form.name),
            race_preferences: convertBiasesToObject(form.biases.race_preferences),
            class_preferences: convertBiasesToObject(form.biases.class_preferences),
            gender_preferences: convertBiasesToObject(form.biases.gender_preferences),
            size_preferences: convertBiasesToObject(form.biases.size_preferences),
          }
          // Remove the biases object since we've converted it to individual preference fields
          delete formData.biases
          emit('save', formData)
        }
      }

      const handleCancel = () => {
        emit('cancel')
      }

      return {
        form,
        gameData,
        races: computed(() => gameData.value?.races || []),
        classes: computed(() => gameData.value?.classes || []),
        genders,
        sizes: computed(() => gameData.value?.sizes?.character || []),
        alignments: computed(() => gameData.value?.alignments || []),
        isFormValid,
        addBiasPreference,
        handleRaceBiasChange,
        handleRaceBiasRemove,
        handleClassBiasChange,
        handleClassBiasRemove,
        handleGenderBiasChange,
        handleGenderBiasRemove,
        handleSizeBiasChange,
        handleSizeBiasRemove,
        handleCommunicationStyleTypeChange,
        handleVoiceSelection,
        handleProviderSelection,
        handleSave,
        handleCancel,
      }
    },
  }
</script>

<style scoped>
  .custom-communication-style {
    margin-top: 12px;
  }

  /* Bias Section Styles */
  .bias-section-description {
    margin: 0 0 1.5rem 0;
    font-size: 0.875rem;
    color: var(--gray-500);
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
    color: var(--gray-600);
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
  }
</style>
