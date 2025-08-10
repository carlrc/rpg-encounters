<template>
  <SplitViewLayout
    :items="characters"
    :selected-item-id="selectedCharacterId"
    list-title="Characters"
    create-button-text=""
    empty-message="No characters available"
    @select-item="selectCharacter"
    @create-item="() => {}"
  >
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading characters...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedCharacter"
        icon="🎭"
        title="No Character Selected"
        message="Select a character from the list to start an encounter."
      />

      <div v-else class="encounter-interface">
        <div class="character-header">
          <div class="character-avatar">
            <img
              v-if="selectedCharacter.avatar"
              :src="selectedCharacter.avatar"
              :alt="selectedCharacter.name"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              <span class="avatar-initials">{{ getInitials(selectedCharacter.name) }}</span>
            </div>
          </div>
          <div class="character-info">
            <h2>{{ selectedCharacter.name }}</h2>
            <p v-if="selectedCharacter.race">{{ selectedCharacter.race }}</p>
          </div>
        </div>

        <div class="encounter-controls">
          <div class="player-selection">
            <label for="player-select">Speaking Player:</label>
            <select
              id="player-select"
              v-model="selectedPlayerId"
              class="shared-select"
              :disabled="isRecording || isProcessing"
            >
              <option value="">Select a player</option>
              <option v-for="player in players" :key="player.id" :value="player.id">
                {{ player.name }}
              </option>
            </select>
          </div>

          <button
            @click="toggleRecording"
            :class="['speak-button', { recording: isRecording, processing: isProcessing }]"
            :disabled="!selectedPlayerId || isProcessing"
          >
            {{ buttonText }}
          </button>

          <div :class="['status', { recording: isRecording, processing: isProcessing }]">
            {{ statusText }}
          </div>
        </div>
      </div>
    </template>
  </SplitViewLayout>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import { getInitials } from '../utils/avatarUtils.js'
  import apiService from '../services/api.js'

  export default {
    name: 'EncountersPage',
    components: {
      SplitViewLayout,
      EmptyState,
    },
    setup() {
      const characters = ref([])
      const players = ref([])
      const loading = ref(true)
      const error = ref(null)
      const selectedCharacterId = ref(null)
      const selectedPlayerId = ref('')
      const isRecording = ref(false)
      const isProcessing = ref(false)
      const websocket = ref(null)
      const mediaRecorder = ref(null)
      const audioContext = ref(null)
      const audioChunks = ref([])

      const selectedCharacter = computed(() => {
        return characters.value.find((c) => c.id === selectedCharacterId.value) || null
      })

      const buttonText = computed(() => {
        if (isProcessing.value) return 'Processing...'
        return isRecording.value ? 'Stop' : 'Speak'
      })

      const statusText = computed(() => {
        if (isProcessing.value) return 'Processing your message...'
        if (isRecording.value) return 'Listening... Click Stop when done'
        if (!selectedPlayerId.value) return 'Select a player to begin'
        return 'Click Speak to start conversation'
      })

      const loadCharacters = async () => {
        try {
          characters.value = await apiService.getCharacters()
        } catch (err) {
          error.value = 'Failed to load characters'
          console.error('Error loading characters:', err)
        }
      }

      const loadPlayers = async () => {
        try {
          players.value = await apiService.getPlayers()
        } catch (err) {
          error.value = 'Failed to load players'
          console.error('Error loading players:', err)
        }
      }

      const loadData = async () => {
        loading.value = true
        error.value = null

        try {
          await Promise.all([loadCharacters(), loadPlayers()])
        } catch (err) {
          error.value = 'Failed to load data'
        } finally {
          loading.value = false
        }
      }

      const selectCharacter = (characterId) => {
        selectedCharacterId.value = characterId
        // Reset states when switching characters
        if (isRecording.value) {
          stopRecording()
        }
        selectedPlayerId.value = ''
      }

      const connectWebSocket = () => {
        if (!selectedPlayerId.value || !selectedCharacterId.value) return

        const wsUrl = `ws://localhost:8000/conversation/${selectedPlayerId.value}/${selectedCharacterId.value}`
        websocket.value = new WebSocket(wsUrl)

        websocket.value.onopen = () => {
          console.log('WebSocket connected')
        }

        websocket.value.onmessage = (event) => {
          if (event.data instanceof Blob) {
            // Received binary audio chunk
            console.log('Received audio chunk:', event.data.size, 'bytes')
            processAudioChunk(event.data)
          } else if (typeof event.data === 'string') {
            // Received text message
            if (event.data === 'AUDIO_COMPLETE') {
              console.log('Audio streaming complete')
              playAccumulatedAudio()
              isProcessing.value = false
              // Close WebSocket after receiving completion signal
              if (websocket.value) {
                websocket.value.close()
                websocket.value = null
              }
            } else {
              console.log('Received text message:', event.data)
            }
          }
        }

        websocket.value.onerror = (error) => {
          console.error('WebSocket error:', error)
          isProcessing.value = false
        }

        websocket.value.onclose = () => {
          console.log('WebSocket disconnected')
        }
      }

      const processAudioChunk = (audioBlob) => {
        // Simply collect audio chunks
        audioChunks.value.push(audioBlob)
        console.log('Collected audio chunk:', audioBlob.size, 'bytes')
      }

      const playAccumulatedAudio = () => {
        if (audioChunks.value.length === 0) {
          console.log('No audio chunks to play')
          return
        }

        try {
          // Combine all chunks into single blob
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/mpeg' })
          console.log('Playing combined audio:', audioBlob.size, 'bytes')

          // Create object URL and play with Audio element
          const audioUrl = URL.createObjectURL(audioBlob)
          const audio = new Audio(audioUrl)

          audio.onended = () => {
            URL.revokeObjectURL(audioUrl)
            console.log('Audio playback completed')
          }

          audio.onerror = (error) => {
            console.error('Audio playback error:', error)
            URL.revokeObjectURL(audioUrl)
          }

          audio.play().catch((error) => {
            console.error('Failed to play audio:', error)
            URL.revokeObjectURL(audioUrl)
          })
        } catch (error) {
          console.error('Error creating audio blob:', error)
        }

        // Clear chunks for next response
        audioChunks.value = []
      }

      const startRecording = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
              sampleRate: 16000,
              channelCount: 1,
              echoCancellation: true,
              noiseSuppression: true,
            },
          })

          // Set up media recorder to send audio chunks
          mediaRecorder.value = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus',
          })

          mediaRecorder.value.ondataavailable = (event) => {
            if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
              // Send raw binary audio data directly
              websocket.value.send(event.data)
            }
          }

          // Send audio chunks every 250ms for real-time processing
          mediaRecorder.value.start(250)
          isRecording.value = true
        } catch (error) {
          console.error('Error starting recording:', error)
          alert('Could not access microphone. Please check permissions.')
        }
      }

      const stopRecording = () => {
        if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
          mediaRecorder.value.stream.getTracks().forEach((track) => track.stop())
        }

        if (audioContext.value) {
          audioContext.value.close()
        }

        isRecording.value = false
        isProcessing.value = true

        // Let the backend close it after streaming is complete
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.send('END')
        }
      }

      const toggleRecording = () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          // Connect WebSocket before starting recording
          if (!websocket.value) {
            connectWebSocket()
          }
          startRecording()
        }
      }

      onMounted(() => {
        loadData()
      })

      onUnmounted(() => {
        if (websocket.value) {
          websocket.value.close()
        }
        if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
        }
        if (audioContext.value) {
          audioContext.value.close()
        }
        // Clear any remaining audio chunks
        audioChunks.value = []
      })

      return {
        characters,
        players,
        loading,
        error,
        selectedCharacterId,
        selectedPlayerId,
        selectedCharacter,
        isRecording,
        isProcessing,
        buttonText,
        statusText,
        getInitials,
        selectCharacter,
        toggleRecording,
      }
    },
  }
</script>

<style scoped>
  .encounter-interface {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .character-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
  }

  .character-avatar {
    flex-shrink: 0;
  }

  .avatar-image {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #007bff;
  }

  .avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #0056b3);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid #004085;
  }

  .avatar-initials {
    color: white;
    font-size: 24px;
    font-weight: bold;
  }

  .character-info h2 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 1.8em;
    font-weight: 700;
  }

  .character-info p {
    margin: 0;
    color: #6c757d;
    font-size: 1.1em;
    font-style: italic;
  }

  .encounter-controls {
    text-align: center;
  }

  .player-selection {
    margin-bottom: 30px;
  }

  .player-selection label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .speak-button {
    padding: 16px 32px;
    font-size: 1.2em;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 140px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .speak-button:not(:disabled) {
    background: linear-gradient(135deg, #28a745, #218838);
    color: white;
  }

  .speak-button:not(:disabled):hover {
    background: linear-gradient(135deg, #218838, #1e7e34);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(40, 167, 69, 0.3);
  }

  .speak-button.recording {
    background: linear-gradient(135deg, #dc3545, #c82333) !important;
  }

  .speak-button.recording:hover {
    background: linear-gradient(135deg, #c82333, #bd2130) !important;
  }

  .speak-button.processing {
    background: linear-gradient(135deg, #ffc107, #e0a800) !important;
    cursor: not-allowed;
  }

  .speak-button:disabled {
    background: #6c757d;
    color: #fff;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }

  .status {
    font-size: 1.1em;
    font-weight: 500;
    color: #6c757d;
    min-height: 24px;
    transition: color 0.3s ease;
  }

  .status.recording {
    color: #dc3545;
    font-weight: 600;
  }

  .status.processing {
    color: #ffc107;
    font-weight: 600;
  }
</style>
