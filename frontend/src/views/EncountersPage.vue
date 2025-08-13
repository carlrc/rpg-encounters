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

          <div class="control-buttons">
            <button
              @click="toggleRecording"
              :class="['speak-button', { recording: isRecording, processing: isProcessing }]"
              :disabled="!selectedPlayerId || isProcessing || (isChallengeMode && !selectedSkill)"
            >
              {{ buttonText }}
            </button>

            <button
              @click="toggleChallengeMode"
              :class="['challenge-button', { active: isChallengeMode }]"
              :disabled="isRecording || isProcessing"
            >
              Challenge
            </button>
          </div>

          <div v-if="isChallengeMode" class="skill-selection">
            <label for="skill-select">Skill:</label>
            <select
              id="skill-select"
              v-model="selectedSkill"
              class="shared-select"
              :disabled="isRecording || isProcessing"
            >
              <option value="">Select a skill</option>
              <option v-for="skill in skills" :key="skill" :value="skill">
                {{ skill }}
              </option>
            </select>
          </div>

          <div v-if="showDiceRoll && diceRoll !== null" class="dice-result">
            <div class="dice-number">{{ diceRoll }}</div>
            <div class="dice-label">D20 Roll</div>
          </div>

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
  import { useGameData } from '../composables/useGameData.js'

  export default {
    name: 'EncountersPage',
    components: {
      SplitViewLayout,
      EmptyState,
    },
    setup() {
      const { gameData, loadGameData } = useGameData()
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

      // Challenge mode state
      const isChallengeMode = ref(false)
      const selectedSkill = ref('')
      const diceRoll = ref(null)
      const showDiceRoll = ref(false)

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
        if (isChallengeMode.value && !selectedSkill.value)
          return 'Select a skill for challenge mode'
        if (isChallengeMode.value) return 'Click Speak to start challenge'
        return 'Click Speak to start conversation'
      })

      const loadCharacters = async () => {
        try {
          characters.value = await apiService.getCharacters()
        } catch (err) {
          error.value = 'Failed to load characters'
          console.error('Character loading failed')
        }
      }

      const loadPlayers = async () => {
        try {
          players.value = await apiService.getPlayers()
        } catch (err) {
          error.value = 'Failed to load players'
          console.error('Player loading failed')
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

      // Helper function to reset challenge state (DRY principle)
      const resetChallengeState = () => {
        selectedSkill.value = ''
        diceRoll.value = null
        showDiceRoll.value = false
      }

      const selectCharacter = (characterId) => {
        selectedCharacterId.value = characterId
        // Reset states when switching characters
        if (isRecording.value) {
          stopRecording()
        }
        selectedPlayerId.value = ''
        // Reset challenge mode state
        isChallengeMode.value = false
        resetChallengeState()
      }

      const toggleChallengeMode = () => {
        if (isRecording.value || isProcessing.value) return

        isChallengeMode.value = !isChallengeMode.value
        // Reset challenge-specific state when toggling
        resetChallengeState()
      }

      // Helper function to close WebSocket safely
      const closeWebSocket = () => {
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.close()
        }
        websocket.value = null
      }

      const connectWebSocket = () => {
        if (!selectedPlayerId.value || !selectedCharacterId.value) return

        // Validate challenge mode requirements
        if (isChallengeMode.value && (!selectedSkill.value || diceRoll.value === null)) {
          return
        }

        // Build WebSocket URL based on mode
        const wsUrl = isChallengeMode.value
          ? `ws://localhost:8000/challenge/${selectedPlayerId.value}/${selectedCharacterId.value}?skill=${selectedSkill.value}&d20_roll=${diceRoll.value}`
          : `ws://localhost:8000/conversation/${selectedPlayerId.value}/${selectedCharacterId.value}`

        try {
          websocket.value = new WebSocket(wsUrl)

          websocket.value.onopen = () => {
            // WebSocket connected
          }

          websocket.value.onmessage = (event) => {
            if (event.data instanceof Blob) {
              processAudioChunk(event.data)
            } else if (typeof event.data === 'string') {
              if (event.data === 'AUDIO_COMPLETE') {
                playAccumulatedAudio()
                isProcessing.value = false
                closeWebSocket()
              }
            }
          }

          websocket.value.onerror = (error) => {
            console.error('WebSocket connection error')
            isProcessing.value = false
            closeWebSocket()
          }

          websocket.value.onclose = () => {
            websocket.value = null
          }
        } catch (error) {
          console.error('WebSocket creation failed')
          isProcessing.value = false
        }
      }

      const processAudioChunk = (audioBlob) => {
        audioChunks.value.push(audioBlob)
      }

      const playAccumulatedAudio = () => {
        if (audioChunks.value.length === 0) {
          return
        }

        try {
          // Combine all chunks into single blob
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/mpeg' })

          // Create object URL and play with Audio element
          const audioUrl = URL.createObjectURL(audioBlob)
          const audio = new Audio(audioUrl)

          audio.onended = () => {
            URL.revokeObjectURL(audioUrl)
          }

          audio.onerror = () => {
            console.error('Audio playback error')
            URL.revokeObjectURL(audioUrl)
          }

          audio.play().catch(() => {
            console.error('Audio play failed')
            URL.revokeObjectURL(audioUrl)
          })
        } catch (error) {
          console.error('Audio processing error')
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
          console.error('Microphone access failed')
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

        // Show dice roll when stopping recording in challenge mode
        if (isChallengeMode.value) {
          showDiceRoll.value = true
        }

        // Let the backend close it after streaming is complete
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.send('END')
        }
      }

      // Helper function to prepare challenge mode
      const prepareChallengeMode = () => {
        // Generate new dice roll for each attempt
        diceRoll.value = Math.floor(Math.random() * 20) + 1
        showDiceRoll.value = false // Keep hidden until recording stops

        // Close existing WebSocket to ensure fresh connection with new dice roll
        closeWebSocket()
      }

      const toggleRecording = () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          // Prepare challenge mode if active
          if (isChallengeMode.value) {
            prepareChallengeMode()
          }

          // Ensure WebSocket connection exists
          if (!websocket.value) {
            connectWebSocket()
          }

          // Start recording if WebSocket is ready
          if (websocket.value) {
            startRecording()
          }
        }
      }

      onMounted(async () => {
        await loadGameData()
        loadData()
      })

      onUnmounted(() => {
        // Clean up WebSocket connection
        closeWebSocket()

        // Clean up media recorder
        if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
        }

        // Clean up audio context
        if (audioContext.value) {
          audioContext.value.close()
        }

        // Clear any remaining audio chunks
        audioChunks.value = []
      })

      return {
        gameData,
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
        // Challenge mode properties
        skills: computed(() => gameData.value.skills),
        isChallengeMode,
        selectedSkill,
        diceRoll,
        showDiceRoll,
        toggleChallengeMode,
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

  .control-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
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
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .challenge-button {
    padding: 12px 24px;
    font-size: 1em;
    font-weight: 600;
    border: 2px solid #6c757d;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
    background: white;
    color: #6c757d;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .challenge-button:hover:not(:disabled) {
    border-color: #007bff;
    color: #007bff;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
  }

  .challenge-button.active {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-color: #007bff;
  }

  .challenge-button.active:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
    border-color: #004085;
  }

  .challenge-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
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

  .skill-selection {
    margin-bottom: 20px;
  }

  .skill-selection label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .dice-result {
    margin-bottom: 20px;
    text-align: center;
  }

  .dice-number {
    font-size: 3em;
    font-weight: bold;
    color: #007bff;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 5px;
  }

  .dice-label {
    font-size: 1em;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
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
