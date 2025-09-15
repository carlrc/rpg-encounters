<template>
  <div class="shared-field shared-field-full-width">
    <div class="shared-field-label character-voice-title">🎤 Character Voice</div>

    <!-- Current Voice Display -->
    <div v-if="currentVoiceId && currentVoiceName" class="shared-field-value">
      <div class="communication-style-display">
        <div class="voice-name-container">
          <span class="communication-style-type">{{ currentVoiceName }}</span>
          <button
            @click="playCurrentVoiceSample"
            class="voice-preview-btn"
            :disabled="audioLoading && playingVoiceId === currentVoiceId"
            title="Play current voice sample"
          >
            {{ audioLoading && playingVoiceId === currentVoiceId ? '⏳' : '▶️' }}
          </button>
        </div>
        <div class="preset-communication-style">ID: {{ currentVoiceId }}</div>
      </div>
    </div>

    <!-- Manual Voice Input Section -->
    <div class="voice-manual-input">
      <div class="manual-input-header">
        <label class="manual-input-label">Manual Voice ID Entry</label>
      </div>
      <div class="manual-input-controls">
        <input
          v-model="manualVoiceId"
          placeholder="Voice ID"
          class="shared-input manual-voice-input"
          :disabled="disabled"
        />
        <button
          @click="previewManualVoice"
          class="voice-preview-btn manual-preview-btn"
          :disabled="
            !manualVoiceId.trim() || (audioLoading && playingVoiceId === manualVoiceId.trim())
          "
          title="Preview this voice"
        >
          {{ audioLoading && playingVoiceId === manualVoiceId.trim() ? '⏳' : '▶️' }}
        </button>
        <button
          @click="setManualVoice"
          class="shared-btn shared-btn-primary manual-set-btn"
          :disabled="!manualVoiceId.trim() || disabled"
        >
          Set Voice
        </button>
      </div>
      <div v-if="manualVoiceError" class="voice-error">
        {{ manualVoiceError }}
      </div>
    </div>

    <!-- Voice Browser Section -->
    <div class="voice-browser">
      <div class="browser-header">
        <label class="browser-label">Browse Available Voices</label>
      </div>

      <!-- Provider Selection -->
      <div v-if="!initialLoading" class="voice-search">
        <select
          v-model="selectedProvider"
          class="shared-select voice-provider-select"
          @change="handleProviderChange"
          :disabled="disabled"
        >
          <option
            v-for="provider in gameData?.tts_providers || []"
            :key="provider"
            :value="provider"
          >
            {{ formatProviderName(provider) }}
          </option>
        </select>
      </div>

      <!-- Voice Search -->
      <div v-if="!initialLoading && selectedProvider" class="voice-search">
        <input
          v-model="searchTerm"
          placeholder="🔍 Filter voices..."
          class="shared-input voice-search-input"
        />
      </div>

      <!-- Voice List -->
      <div v-if="initialLoading" class="shared-loading">Loading voices...</div>

      <div v-else-if="loadError" class="shared-error">
        {{ loadError }}
        <button
          @click="loadAllVoices"
          class="shared-btn shared-btn-secondary"
          style="margin-left: 8px; padding: 4px 8px; font-size: 0.8rem"
        >
          Retry
        </button>
      </div>

      <div v-else-if="filteredVoices.length === 0" class="voice-empty">
        <div v-if="searchTerm.trim()">No voices found for "{{ searchTerm }}"</div>
        <div v-else>No voices available for {{ formatProviderName(selectedProvider) }}.</div>
      </div>

      <div v-else class="voice-results-container">
        <div class="voice-results-header">
          <span class="results-count">
            {{ filteredVoices.length }} voice{{ filteredVoices.length !== 1 ? 's' : '' }}
            <span v-if="searchTerm.trim()">for "{{ searchTerm }}"</span>
          </span>
        </div>

        <div class="voice-list">
          <div
            v-for="voice in filteredVoices"
            :key="voice.voice_id"
            class="voice-item"
            :class="{ selected: voice.voice_id === currentVoiceId }"
          >
            <button
              @click="selectVoice(voice)"
              class="voice-add-btn"
              :class="{ selected: voice.voice_id === currentVoiceId }"
              :title="
                voice.voice_id === currentVoiceId ? 'Currently selected' : 'Select this voice'
              "
              :disabled="disabled"
            >
              {{ voice.voice_id === currentVoiceId ? '✓' : '+' }}
            </button>

            <div class="voice-info">
              <span class="voice-name">{{ voice.name }}</span>
              <div class="voice-details">
                <span v-if="voice.description" class="voice-description">{{
                  voice.description
                }}</span>
                <div class="voice-labels">
                  <span class="voice-category">{{ voice.category }}</span>
                  <span v-if="voice.labels?.gender" class="voice-label">{{
                    voice.labels.gender
                  }}</span>
                  <span v-if="voice.labels?.accent" class="voice-label">{{
                    voice.labels.accent
                  }}</span>
                  <span v-if="voice.labels?.age" class="voice-label">{{ voice.labels.age }}</span>
                  <span v-if="voice.labels?.language" class="voice-label">{{
                    voice.labels.language
                  }}</span>
                  <span v-if="voice.labels?.descriptive" class="voice-label">{{
                    voice.labels.descriptive
                  }}</span>
                </div>
                <span class="voice-id">ID: {{ voice.voice_id }}</span>
              </div>
            </div>

            <button
              @click="playSample(voice.voice_id)"
              class="voice-preview-btn"
              :disabled="audioLoading && playingVoiceId === voice.voice_id"
              :title="
                audioLoading && playingVoiceId === voice.voice_id ? 'Loading...' : 'Play sample'
              "
            >
              {{ audioLoading && playingVoiceId === voice.voice_id ? '⏳' : '▶️' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useAudioPlayer } from '../composables/useAudioPlayer.js'
  import { searchVoices, getVoiceSample } from '../services/api.js'

  export default {
    name: 'VoiceSelector',
    props: {
      currentVoiceId: {
        type: String,
        default: null,
      },
      currentVoiceName: {
        type: String,
        default: null,
      },
      currentProvider: {
        type: String,
        default: null,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['select-voice', 'select-provider'],
    setup(props, { emit }) {
      // Game data store
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      // Audio player composable
      const {
        playSampleResponse,
        isLoading: audioLoading,
        playingAudioId,
        error: audioError,
        stop,
      } = useAudioPlayer()

      // State management
      const allVoices = ref([])
      const initialLoading = ref(true)
      const loadError = ref(null)
      const playingVoiceId = ref(null)

      // Manual input state
      const manualVoiceId = ref('')
      const manualVoiceError = ref(null)

      // Search state
      const searchTerm = ref('')

      // Provider state
      const selectedProvider = ref(props.currentProvider || '')

      // Computed properties
      const filteredVoices = computed(() => {
        if (!searchTerm.value.trim()) {
          return allVoices.value
        }

        const search = searchTerm.value.trim().toLowerCase()
        return allVoices.value.filter((voice) => {
          // Search in name and description
          const nameMatch = voice.name.toLowerCase().includes(search)
          const descriptionMatch =
            voice.description && voice.description.toLowerCase().includes(search)

          // Search in category
          const categoryMatch = voice.category && voice.category.toLowerCase().includes(search)

          // Search in labels
          let labelsMatch = false
          if (voice.labels) {
            const labels = voice.labels
            labelsMatch =
              (labels.gender && labels.gender.toLowerCase().includes(search)) ||
              (labels.accent && labels.accent.toLowerCase().includes(search)) ||
              (labels.descriptive && labels.descriptive.toLowerCase().includes(search)) ||
              (labels.age && labels.age.toLowerCase().includes(search)) ||
              (labels.language && labels.language.toLowerCase().includes(search))
          }

          return nameMatch || descriptionMatch || categoryMatch || labelsMatch
        })
      })

      // Methods
      const loadAllVoices = async () => {
        if (!selectedProvider.value) {
          allVoices.value = []
          initialLoading.value = false
          return
        }

        try {
          initialLoading.value = true
          loadError.value = null

          const response = await searchVoices('en', selectedProvider.value)
          allVoices.value = response.voices || []
        } catch (err) {
          loadError.value = 'Failed to load voices. Please try again.'
          console.error('Failed to load voices:', err)
        } finally {
          initialLoading.value = false
        }
      }

      const handleProviderChange = () => {
        emit('select-provider', selectedProvider.value)
        loadAllVoices()
      }

      const formatProviderName = (provider) => {
        return provider === 'elevanlabs'
          ? 'ElevenLabs'
          : provider === 'google'
            ? 'Google'
            : provider
      }

      // Voice selection and preview methods
      const selectVoice = (voice) => {
        if (props.disabled) return
        emit('select-voice', voice)
      }

      const setManualVoice = () => {
        if (!manualVoiceId.value.trim() || props.disabled) return

        const voiceId = manualVoiceId.value.trim()
        manualVoiceError.value = null

        // Create a voice object for manual input
        const manualVoice = {
          voice_id: voiceId,
          name: `Manual Voice (${voiceId})`,
          description: 'Manually entered voice ID',
          category: 'manual',
        }

        emit('select-voice', manualVoice)
        manualVoiceId.value = '' // Clear the input after selection
      }

      const previewManualVoice = async () => {
        if (!manualVoiceId.value.trim()) return
        await playSample(manualVoiceId.value.trim())
      }

      const playCurrentVoiceSample = async () => {
        if (!props.currentVoiceId || audioLoading.value) return
        await playSample(props.currentVoiceId)
      }

      const playSample = async (voiceId) => {
        if (audioLoading.value || !selectedProvider.value) return

        try {
          playingVoiceId.value = voiceId
          manualVoiceError.value = null

          // Stop any current audio before playing new sample
          await stop()

          const response = await getVoiceSample(voiceId, selectedProvider.value)
          await playSampleResponse(response, voiceId)
        } catch (err) {
          if (voiceId === manualVoiceId.value.trim()) {
            manualVoiceError.value = 'Invalid voice ID or failed to play sample'
          }
          console.error('Voice sample playback failed:', err)
        } finally {
          playingVoiceId.value = null
        }
      }

      // Lifecycle
      onMounted(async () => {
        await gameDataStore.load()
        selectedProvider.value = props.currentProvider
        loadAllVoices()
      })

      onUnmounted(async () => {
        try {
          await stop()
        } catch {}
      })

      return {
        // State
        allVoices,
        initialLoading,
        loadError,
        audioLoading,
        playingVoiceId,
        manualVoiceId,
        manualVoiceError,
        searchTerm,
        selectedProvider,
        gameData,

        // Computed
        filteredVoices,

        // Methods
        loadAllVoices,
        selectVoice,
        setManualVoice,
        previewManualVoice,
        playSample,
        playCurrentVoiceSample,
        handleProviderChange,
        formatProviderName,
      }
    },
  }
</script>

<style scoped>
  /* Character Voice Title */
  .character-voice-title {
    text-align: center !important;
    display: block;
    width: 100%;
  }

  /* Center the current voice display */
  .shared-field-value .communication-style-display {
    align-items: center;
  }

  .shared-field-value .voice-name-container {
    justify-content: center !important;
  }

  /* Manual Input Section */
  .voice-manual-input {
    margin: 16px 0;
    padding: 16px;
    border: 2px dashed var(--gray-200);
    border-radius: 8px;
    background: var(--gray-50);
  }

  .manual-input-header {
    margin-bottom: 12px;
  }

  .manual-input-label {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--gray-600);
  }

  .manual-input-controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .manual-voice-input {
    flex: 1;
    font-family: monospace;
    font-size: 0.85rem;
  }

  .manual-preview-btn,
  .manual-set-btn {
    flex-shrink: 0;
  }

  .manual-set-btn {
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .voice-error {
    margin-top: 8px;
    color: var(--danger-color);
    font-size: 0.8rem;
    font-style: italic;
  }

  /* Voice Browser Section */
  .voice-browser {
    margin-top: 16px;
  }

  .browser-header {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 12px;
  }

  .browser-label {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--gray-600);
    text-align: center;
  }

  /* Voice Search */
  .voice-search {
    margin-bottom: 16px;
    display: flex;
    justify-content: center;
  }

  .voice-search-input {
    max-width: 400px;
  }

  /* Current voice display - reuse CharacterCard shared styles */
  .voice-name-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  /* Scrollable results container */
  .voice-results-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid var(--gray-200);
    border-radius: 6px;
    background: white;
  }

  /* Results header */
  .voice-results-header {
    padding: 8px 12px;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
  }

  .results-count {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--gray-600);
  }

  /* Status messages */
  .voice-empty {
    text-align: center;
    font-style: italic;
    padding: 40px 20px;
    font-size: 0.9rem;
    color: var(--gray-500);
  }

  /* Voice list */
  .voice-list {
    padding: 8px;
  }

  .voice-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    margin-bottom: 8px;
    background: white;
    border: 1px solid var(--gray-200);
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .voice-item.selected {
    background: var(--color-voice-selected-bg);
    border-color: var(--color-voice-selected);
  }

  .voice-item:hover {
    border-color: var(--gray-400);
    transform: translateY(-1px);
    box-shadow: var(--shadow-voice-hover);
  }

  /* Voice selection button */
  .voice-add-btn {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 50%;
    background: var(--color-voice-add-btn);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .voice-add-btn:hover:not(:disabled) {
    background: var(--color-voice-add-btn-hover);
    transform: scale(1.1);
  }

  .voice-add-btn.selected {
    background: var(--success-color);
  }

  .voice-add-btn.selected:hover {
    background: var(--success-dark);
  }

  .voice-add-btn:disabled {
    background: var(--gray-500);
    cursor: not-allowed;
    transform: none;
  }

  /* Voice info */
  .voice-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .voice-name {
    font-weight: 600;
    font-size: 1rem;
    color: var(--gray-800);
  }

  .voice-details {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .voice-description {
    font-size: 0.85rem;
    color: var(--gray-600);
  }

  .voice-labels {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 2px 0;
  }

  .voice-category,
  .voice-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-transform: capitalize;
    font-weight: 500;
    padding: 2px 6px;
    background: var(--gray-50);
    border-radius: 3px;
    border: 1px solid var(--gray-100);
  }

  .voice-id {
    font-size: 0.7rem;
    color: var(--gray-400);
    font-family: monospace;
  }

  /* Voice preview button */
  .voice-preview-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    transition: transform 0.2s ease;
    padding: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .voice-preview-btn:hover:not(:disabled) {
    background: var(--gray-50);
    transform: scale(1.1);
  }

  .voice-preview-btn:disabled {
    cursor: not-allowed;
    transform: none;
    opacity: 0.6;
  }

  /* Communication style display styles */
  .communication-style-display {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .communication-style-type {
    font-weight: 600;
    color: var(--primary-color);
    font-size: 0.9rem;
    padding: 4px 8px;
    background-color: var(--gray-50);
    border-radius: 4px;
    display: block;
    width: fit-content;
    margin: 0 auto;
    text-align: center;
  }

  .preset-communication-style {
    font-style: italic;
    color: var(--gray-500);
    font-size: 0.8rem;
    text-align: center;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .manual-input-controls {
      flex-direction: column;
      gap: 8px;
    }

    .manual-voice-input {
      width: 100%;
    }

    .voice-search-input {
      max-width: 100%;
    }

    .voice-results-container {
      max-height: 300px;
    }
  }
</style>
