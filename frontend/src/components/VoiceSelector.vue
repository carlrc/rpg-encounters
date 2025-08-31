<template>
  <div class="shared-field shared-field-full-width">
    <div class="shared-field-label">🎤 Character Voice</div>

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

    <!-- Voice Search -->
    <div class="voice-search">
      <input
        v-model="searchTerm"
        @keyup.enter="handleEnterSearch"
        placeholder="Search voices (press Enter to search)..."
        class="shared-input voice-search-input"
        :disabled="loading"
      />
    </div>

    <!-- Search Results Container -->
    <div v-if="searchTerm" class="voice-results-container">
      <div v-if="loading && voices.length === 0" class="shared-loading">Searching voices...</div>

      <div v-else-if="error" class="shared-error">
        {{ error }}
        <button
          @click="retrySearch"
          class="shared-btn shared-btn-secondary"
          style="margin-left: 8px; padding: 4px 8px; font-size: 0.8rem"
        >
          Retry
        </button>
      </div>

      <div v-else-if="voices.length === 0" class="voice-empty">
        No voices found for "{{ searchTerm }}"
      </div>

      <div v-else class="voice-results">
        <div class="voice-results-header">
          <span class="results-count"
            >{{ voices.length }} voice{{ voices.length !== 1 ? 's' : '' }}</span
          >
        </div>

        <div class="voice-list">
          <div
            v-for="voice in voices"
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
            >
              {{ voice.voice_id === currentVoiceId ? '✓' : '+' }}
            </button>

            <div class="voice-info">
              <span class="voice-name">{{ voice.name }}</span>
              <span v-if="voice.description" class="voice-description">{{
                voice.description
              }}</span>
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

        <div v-if="hasMore" class="voice-pagination">
          <button
            @click="loadMore"
            class="shared-btn shared-btn-primary"
            :disabled="loading"
            style="padding: 6px 12px; font-size: 0.9rem"
          >
            {{ loading ? 'Loading...' : 'Load More' }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="voice-prompt">Type to search for voices...</div>
  </div>
</template>

<script>
  import { ref, onMounted, onUnmounted } from 'vue'
  import { useAudioPlayer } from '../composables/useAudioPlayer.js'
  import apiService from '../services/api.js'

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
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['select-voice'],
    setup(props, { emit }) {
      // Audio player composable
      const {
        playStreamingResponse,
        isLoading: audioLoading,
        playingAudioId,
        error: audioError,
      } = useAudioPlayer()

      // Voice search state
      const voices = ref([])
      const searchTerm = ref('')
      const loading = ref(false)
      const error = ref(null)
      const hasMore = ref(false)
      const nextPageToken = ref(null)
      const searchTimeout = ref(null)

      // Computed for audio state
      const playingVoiceId = ref(null)

      // Handle Enter key search
      const handleEnterSearch = () => {
        if (searchTerm.value.trim()) {
          searchVoices(true) // true = reset results
        } else {
          resetSearch()
        }
      }

      // Search for voices
      const searchVoices = async (reset = false) => {
        if (!searchTerm.value.trim()) return

        try {
          loading.value = true
          error.value = null

          const pageToken = reset ? null : nextPageToken.value
          if (reset) {
            voices.value = []
          }

          const response = await apiService.searchVoices(searchTerm.value.trim(), pageToken)

          if (reset) {
            voices.value = response.voices || []
          } else {
            voices.value.push(...(response.voices || []))
          }

          hasMore.value = response.has_more || false
          nextPageToken.value = response.next_page_token || null
        } catch (err) {
          error.value = 'Failed to search voices. Please try again.'
          console.error('Voice search failed:', err)
        } finally {
          loading.value = false
        }
      }

      // Load more voices (pagination)
      const loadMore = () => {
        if (hasMore.value && !loading.value) {
          searchVoices(false) // false = append results
        }
      }

      // Reset search results
      const resetSearch = () => {
        voices.value = []
        hasMore.value = false
        nextPageToken.value = null
        error.value = null
      }

      // Retry search after error
      const retrySearch = () => {
        if (searchTerm.value.trim()) {
          searchVoices(true)
        }
      }

      // Select a voice
      const selectVoice = (voice) => {
        if (props.disabled) return
        emit('select-voice', voice)
      }

      // Play current voice sample
      const playCurrentVoiceSample = async () => {
        if (!props.currentVoiceId || audioLoading.value) return
        await playSample(props.currentVoiceId)
      }

      // Play voice sample
      const playSample = async (voiceId) => {
        if (audioLoading.value) return

        try {
          playingVoiceId.value = voiceId

          // Get voice sample from API service
          const response = await apiService.getVoiceSample(voiceId)
          await playStreamingResponse(response, voiceId)
        } catch (err) {
          error.value = 'Failed to play voice sample'
          console.error('Voice sample playback failed:', err)
        } finally {
          playingVoiceId.value = null
        }
      }

      // Cleanup timeout on unmount
      onUnmounted(() => {
        if (searchTimeout.value) {
          clearTimeout(searchTimeout.value)
        }
      })

      return {
        // State
        voices,
        searchTerm,
        loading,
        error,
        hasMore,
        audioLoading,
        playingVoiceId,

        // Methods
        handleEnterSearch,
        loadMore,
        retrySearch,
        selectVoice,
        playSample,
        playCurrentVoiceSample,
      }
    },
  }
</script>

<style scoped>
  /* Voice search field - centered */
  .voice-search {
    margin-bottom: 16px;
    display: flex;
    justify-content: center;
  }

  .voice-search-input {
    max-width: 300px;
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
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    background: white;
  }

  /* Status messages */
  .voice-empty,
  .voice-prompt {
    text-align: center;
    font-style: italic;
    padding: 20px;
    font-size: 0.9rem;
    color: #6c757d;
  }

  /* Results header */
  .voice-results-header {
    padding: 8px 12px;
    border-bottom: 1px solid #dee2e6;
    background: #f8f9fa;
  }

  .results-count {
    font-size: 0.9rem;
    font-weight: 500;
  }

  /* Voice list */
  .voice-list {
    padding: 8px;
  }

  .voice-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    margin-bottom: 8px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .voice-item.selected {
    background: #e3f2fd;
    border-color: #007bff;
  }

  .voice-item:hover {
    border-color: #adb5bd;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  /* Voice selection button */
  .voice-add-btn {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border: none;
    border-radius: 50%;
    background: #007bff;
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .voice-add-btn:hover {
    background: #0056b3;
    transform: scale(1.1);
  }

  .voice-add-btn.selected {
    background: #28a745;
  }

  .voice-add-btn.selected:hover {
    background: #218838;
  }

  /* Voice info */
  .voice-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .voice-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: #2c3e50;
  }

  .voice-description {
    font-size: 0.8rem;
    font-style: italic;
    color: #6c757d;
  }

  /* Shared voice preview button - matches CharacterCard */
  .voice-preview-btn {
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    transition: transform 0.2s ease;
    padding: 4px;
  }

  .voice-preview-btn:hover:not(:disabled) {
    transform: scale(1.1);
  }

  .voice-preview-btn:disabled {
    cursor: not-allowed;
    transform: none;
    opacity: 0.6;
  }

  /* Pagination */
  .voice-pagination {
    display: flex;
    justify-content: center;
    padding: 12px;
    background: #f8f9fa;
    border-top: 1px solid #dee2e6;
  }
</style>
