<template>
  <div v-if="isOpen" class="encounter-popup-overlay" @click="closePopup">
    <div class="encounter-popup" @click.stop>
      <div class="popup-header">
        <h3>Encounter with {{ character?.name }}</h3>
        <button class="close-button" @click="closePopup">&times;</button>
      </div>

      <!-- Direct reuse of encounter interface from EncountersPage.vue -->
      <div class="encounter-interface">
        <div class="character-header">
          <div class="character-avatar">
            <img
              v-if="character?.avatar"
              :src="character.avatar"
              :alt="character.name"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              <span class="avatar-initials">{{ getInitials(character?.name || '') }}</span>
            </div>
          </div>
          <div class="character-info">
            <h2>{{ character?.name }}</h2>
            <p v-if="character?.race">{{ character.race }}</p>
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
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { getInitials } from '../utils/avatarUtils.js'
  import { useGameData } from '../composables/useGameData.js'
  import apiService from '../services/api.js'

  // Constants to replace magic numbers
  const WEBSOCKET_BASE_URL = 'ws://localhost:8000'
  const AUDIO_SAMPLE_RATE = 16000
  const AUDIO_CHANNEL_COUNT = 1
  const MEDIA_RECORDER_TIMESLICE = 250

  export default {
    name: 'CharacterEncounterPopup',
    props: {
      character: {
        type: Object,
        default: null,
      },
      isOpen: {
        type: Boolean,
        default: false,
      },
      encounterId: {
        type: Number,
        required: true,
      },
    },
    emits: ['close'],
    setup(props, { emit }) {
      const { gameData, loadGameData } = useGameData()

      // Use existing data from API (same as EncountersPage.vue)
      const players = ref([])
      const loading = ref(true)
      const error = ref(null)

      // Encounter state (copied from EncountersPage.vue)
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

      // Computed properties (copied from EncountersPage.vue)
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

      const skills = computed(() => gameData.value?.skills || [])

      // Load data functions (same as EncountersPage.vue)
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
          await Promise.all([loadPlayers()])
        } catch (err) {
          error.value = 'Failed to load data'
        } finally {
          loading.value = false
        }
      }

      // Encounter functions (simplified from EncountersPage.vue)
      const closePopup = () => {
        // Clean up any active recording/websocket
        if (isRecording.value) {
          stopRecording()
        }
        closeWebSocket()

        // Reset state
        selectedPlayerId.value = ''
        isChallengeMode.value = false
        selectedSkill.value = ''
        diceRoll.value = null
        showDiceRoll.value = false

        emit('close')
      }

      const resetChallengeState = () => {
        selectedSkill.value = ''
        diceRoll.value = null
        showDiceRoll.value = false
      }

      const toggleChallengeMode = () => {
        if (isRecording.value || isProcessing.value) return

        isChallengeMode.value = !isChallengeMode.value
        resetChallengeState()
      }

      const closeWebSocket = () => {
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.close()
        }
        websocket.value = null
      }

      const connectWebSocket = () => {
        if (!selectedPlayerId.value || !props.character?.id) return

        if (isChallengeMode.value && (!selectedSkill.value || diceRoll.value === null)) {
          return
        }

        const wsUrl = isChallengeMode.value
          ? `${WEBSOCKET_BASE_URL}/api/encounters/${props.encounterId}/challenge/${selectedPlayerId.value}/${props.character.id}?skill=${selectedSkill.value}&d20_roll=${diceRoll.value}`
          : `${WEBSOCKET_BASE_URL}/api/encounters/${props.encounterId}/conversation/${selectedPlayerId.value}/${props.character.id}`

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
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/mpeg' })
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

        audioChunks.value = []
      }

      const startRecording = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
              sampleRate: AUDIO_SAMPLE_RATE,
              channelCount: AUDIO_CHANNEL_COUNT,
              echoCancellation: true,
              noiseSuppression: true,
            },
          })

          mediaRecorder.value = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus',
          })

          mediaRecorder.value.ondataavailable = (event) => {
            if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
              websocket.value.send(event.data)
            }
          }

          mediaRecorder.value.start(MEDIA_RECORDER_TIMESLICE)
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

        if (isChallengeMode.value) {
          showDiceRoll.value = true
        }

        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.send('END')
        }
      }

      const prepareChallengeMode = () => {
        diceRoll.value = Math.floor(Math.random() * 20) + 1
        showDiceRoll.value = false
        closeWebSocket()
      }

      const toggleRecording = () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          if (isChallengeMode.value) {
            prepareChallengeMode()
          }

          if (!websocket.value) {
            connectWebSocket()
          }

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
        closeWebSocket()

        if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
        }

        if (audioContext.value) {
          audioContext.value.close()
        }

        audioChunks.value = []
      })

      return {
        players,
        loading,
        error,
        selectedPlayerId,
        isRecording,
        isProcessing,
        buttonText,
        statusText,
        skills,
        isChallengeMode,
        selectedSkill,
        diceRoll,
        showDiceRoll,
        closePopup,
        toggleRecording,
        toggleChallengeMode,
        getInitials,
      }
    },
  }
</script>

<style scoped>
  /* Popup overlay and container */
  .encounter-popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .encounter-popup {
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #e9ecef;
    flex-shrink: 0;
  }

  .popup-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5em;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6c757d;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background: #f8f9fa;
    color: #dc3545;
  }

  /* Import all encounter styles from EncountersPage.vue */
  .encounter-interface {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .character-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 1px solid #e9ecef;
    flex-shrink: 0;
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
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .player-selection {
    margin-bottom: 20px;
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
    margin-bottom: 15px;
  }

  .skill-selection label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .dice-result {
    margin: 15px auto;
    text-align: center;
    /* Enhanced container styling for better visibility */
    min-width: 150px;
    min-height: 100px;
    padding: 15px 20px;
    background: #f8f9fa;
    border-radius: 12px;
    border: 2px solid #e9ecef;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .dice-number {
    font-size: 3.5em;
    font-weight: bold;
    color: #007bff;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
    line-height: 1;
  }

  .dice-label {
    font-size: 1.1em;
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
