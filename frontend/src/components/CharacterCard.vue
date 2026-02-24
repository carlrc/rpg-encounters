<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="character-content">
      <AvatarDisplay :name="character.name" :avatar="character.avatar" />

      <h3 class="shared-title">{{ getGenderEmoji(character.gender) }} {{ character.name }}</h3>

      <div class="character-fields">
        <div class="shared-field-columns">
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

    <div v-else>
      <AvatarDisplay :name="character.name" :avatar="character.avatar" />
      <CharacterForm
        :initial-data="character"
        :is-editing="true"
        @save="saveEdit"
        @cancel="cancelEdit"
      />
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted, onUnmounted, watch, watchEffect } from 'vue'
  import { storeToRefs } from 'pinia'
  import { serializeError } from 'serialize-error'
  import { useDropdownOptions } from '../composables/useDropdownOptions'
  import { useGameDataStore } from '../stores/gameData'
  import HttpAudioPlayer from '../composables/audio/HttpAudioPlayer'
  import CharacterForm from './CharacterForm.vue'
  import AvatarDisplay from './base/AvatarDisplay.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'
  import { getVoiceSample } from '../services/api'

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
  const httpPlayer = new HttpAudioPlayer()
  const previewLoading = ref(false)
  const isEditing = ref(false)

  const { getGenderEmoji } = useDropdownOptions()

  const cleanupFunctions = []

  const originalAIFields = ref({
    background: '',
    motivation: '',
    communication_style: '',
    communication_style_type: '',
  })

  const startEdit = () => {
    originalAIFields.value = {
      background: props.character.background || '',
      motivation: props.character.motivation || '',
      communication_style: props.character.communication_style || '',
      communication_style_type: props.character.communication_style_type || 'Custom',
    }

    isEditing.value = true
  }

  const cancelEdit = () => {
    isEditing.value = false
  }

  const saveEdit = (formData) => {
    const updateData = {
      name: (formData.name || '').trim(),
      race: formData.race,
      size: formData.size,
      alignment: formData.alignment,
      gender: formData.gender,
      profession: (formData.profession || '').trim(),
      voice_id: formData.voice_id,
      voice_name: formData.voice_name,
      tts_provider: formData.tts_provider,
      race_preferences: formData.race_preferences || {},
      class_preferences: formData.class_preferences || {},
      gender_preferences: formData.gender_preferences || {},
      size_preferences: formData.size_preferences || {},
      appearance_keywords: [],
      storytelling_keywords: [],
    }

    const currentBackground = (formData.background || '').trim()
    const currentMotivation = (formData.motivation || '').trim()
    const currentCommStyle = (formData.communication_style || '').trim()
    const currentCommStyleType = formData.communication_style_type

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

  const playCharacterVoiceSample = async () => {
    if (previewLoading.value) return

    try {
      previewLoading.value = true
      await httpPlayer.stop()

      const response = await getVoiceSample(props.character.voice_id, props.character.tts_provider)
      await httpPlayer.playResponse(response)
    } catch (err) {
      console.error('Failed to play character voice sample:', JSON.stringify(serializeError(err)))
    } finally {
      previewLoading.value = false
    }
  }

  const deleteCharacter = () => {
    if (confirm(`Are you sure you want to delete ${props.character.name}?`)) {
      emit('delete', props.character.id)
    }
  }

  const displayBiases = ref({})

  const loadDisplayBiases = () => {
    const character = props.character
    const biases = {}

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

  onMounted(() => {
    loadDisplayBiases()
  })

  const stopCharacterIdWatcher = watchEffect(() => {
    if (props.character.id) {
      loadDisplayBiases()
    }
  })

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

  cleanupFunctions.push(stopCharacterIdWatcher, stopBiasWatcher)

  onUnmounted(() => {
    cleanupFunctions.forEach((cleanup) => cleanup())
  })

  onUnmounted(async () => {
    try {
      await httpPlayer.stop()
    } catch {}
  })
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
