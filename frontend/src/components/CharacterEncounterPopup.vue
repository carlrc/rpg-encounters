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
            <h2 class="character-name-link" @click="navigateToCharacter">{{ character?.name }}</h2>
            <div class="character-details">
              <span class="character-race">{{ character?.race }}</span>
              <span class="character-profession">{{ character?.profession }}</span>
            </div>
          </div>
        </div>

        <!-- Conversation stats display -->
        <div class="conversation-stats" v-if="influenceScore !== null || revealsData.length > 0">
          <div class="influence-display" v-if="influenceScore !== null">
            <span class="stat-label">Influence:</span>
            <span class="stat-value">{{ influenceScore }}</span>
          </div>

          <div class="reveals-section" v-if="revealsData.length > 0">
            <h4 class="reveals-title">Reveals</h4>
            <div class="reveals-list">
              <div
                v-for="reveal in revealsData"
                :key="reveal.id"
                class="reveal-item reveal-clickable"
                @click="navigateToReveal(reveal)"
              >
                <span class="reveal-title">{{ reveal.title }}</span>
                <span class="reveal-progress" :class="getProgressClass(reveal)">
                  {{ reveal.progress }}
                </span>
              </div>
            </div>
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
                {{ player.rl_name }}
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
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { getInitials } from '../utils/avatarUtils.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useAudioPlayer } from '../composables/useAudioPlayer.js'
  import { getPlayers, getConversationData } from '../services/api.js'

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
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const router = useRouter()

      // Use the standardized audio player composable
      const {
        playWebSocketAudio,
        stopAudio,
        isLoading: audioLoading,
        error: audioError,
      } = useAudioPlayer()

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
      const audioChunks = ref([])

      // NEW: Conversation data state
      const influenceScore = ref(null)
      const revealsData = ref([])

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
          players.value = await getPlayers()
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

        // Stop any playing audio
        stopAudio()

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

      const isConversationData = (v) =>
        v && v.type === 'conversation_data' && 'influence' in v && 'reveals' in v

      const CONTROL = {
        AUDIO_COMPLETE: () => {
          // Use the standardized audio player for WebSocket chunks
          playWebSocketAudio(audioChunks.value, `encounter-${props.encounterId}`)
          audioChunks.value = [] // Clear chunks after playing
          isProcessing.value = false
          closeWebSocket()
        },
      }

      const handleWSMessage = (data) => {
        // Binary audio chunks
        if (data instanceof Blob) {
          processAudioChunk(data)
          return
        }

        // Text frames: fast path for control tokens
        if (typeof data === 'string') {
          const control = CONTROL[data]
          if (control) {
            control()
            return
          }

          // Assume its JSON
          const json = JSON.parse(data)
          if (isConversationData(json)) {
            influenceScore.value = json.influence ?? null
            revealsData.value = Array.isArray(json.reveals) ? json.reveals : []
            return
          }
        }
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

          // Set binary type explicitly for better performance
          websocket.value.binaryType = 'blob'

          websocket.value.onopen = () => {
            // WebSocket connected
          }

          websocket.value.onmessage = (event) => handleWSMessage(event.data)

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

      const navigateToCharacter = () => {
        if (props.character?.id) {
          router.push({
            path: '/characters',
            query: { id: props.character.id },
          })
        }
      }

      const navigateToReveal = (reveal) => {
        router.push({
          path: '/reveals',
          query: { id: reveal.id },
        })
      }

      const getProgressClass = (reveal) => {
        const { unlocked_layers, total_layers } = reveal
        if (unlocked_layers === 0) return 'progress-locked'
        if (unlocked_layers === total_layers) return 'progress-complete'
        return 'progress-partial'
      }

      const fetchConversationData = async () => {
        if (!selectedPlayerId.value) {
          return
        }

        const data = await getConversationData(
          props.encounterId,
          selectedPlayerId.value,
          props.character.id
        )

        influenceScore.value = data.influence
        revealsData.value = data.reveals
      }

      // Automatically reset conversation data when character changes
      watch(
        () => props.character?.id,
        () => {
          influenceScore.value = null
          revealsData.value = []
        }
      )

      // Fetch conversation data when player selection changes
      watch(
        () => selectedPlayerId.value,
        () => {
          if (selectedPlayerId.value) {
            fetchConversationData()
          }
        }
      )

      onMounted(async () => {
        await gameDataStore.load()
        loadData()
      })

      onUnmounted(() => {
        closeWebSocket()

        if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
          mediaRecorder.value.stop()
        }

        // Stop any playing audio when component unmounts
        stopAudio()

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
        navigateToCharacter,
        getInitials,
        influenceScore,
        revealsData,
        getProgressClass,
        navigateToReveal,
        fetchConversationData,
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
    box-shadow: var(--shadow-card-hover);
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
    border-bottom: 1px solid var(--gray-100);
    flex-shrink: 0;
  }

  .popup-header h3 {
    margin: 0;
    color: var(--gray-800);
    font-size: 1.5em;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--gray-500);
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
    background: var(--gray-50);
    color: var(--danger-color);
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
    background: var(--gray-50);
    border-radius: 12px;
    border: 1px solid var(--gray-100);
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
    border: 3px solid var(--primary-color);
  }

  .avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid var(--primary-darker);
  }

  .avatar-initials {
    color: white;
    font-size: 24px;
    font-weight: bold;
  }

  .character-info h2 {
    margin: 0 0 8px 0;
    color: var(--gray-800);
    font-size: 1.8em;
    font-weight: 700;
  }

  .character-name-link {
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .character-name-link:hover {
    color: var(--primary-color);
    text-decoration: underline;
  }

  .character-details {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .character-race,
  .character-profession {
    color: var(--gray-500);
    font-size: 1.1em;
    font-style: italic;
  }

  .character-profession {
    font-weight: 600;
  }

  .character-race::after {
    content: '•';
    margin-left: 8px;
    color: var(--gray-200);
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
    color: var(--gray-600);
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
    box-shadow: var(--shadow-voice-hover);
  }

  .challenge-button {
    padding: 12px 24px;
    font-size: 1em;
    font-weight: 600;
    border: 2px solid var(--gray-500);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
    background: white;
    color: var(--gray-500);
    box-shadow: var(--shadow-voice-hover);
  }

  .challenge-button:hover:not(:disabled) {
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-1px);
    box-shadow: var(--shadow-reveal-hover);
  }

  .challenge-button.active {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    border-color: var(--primary-color);
  }

  .challenge-button.active:hover {
    background: linear-gradient(135deg, var(--primary-dark), var(--primary-darker));
    border-color: var(--primary-darker);
  }

  .challenge-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .speak-button:not(:disabled) {
    background: linear-gradient(135deg, var(--success-color), var(--success-dark));
    color: white;
  }

  .speak-button:not(:disabled):hover {
    background: linear-gradient(135deg, var(--success-dark), var(--success-darker));
    transform: translateY(-2px);
    box-shadow: var(--shadow-success-hover);
  }

  .speak-button.recording {
    background: linear-gradient(135deg, var(--danger-color), var(--danger-dark)) !important;
  }

  .speak-button.recording:hover {
    background: linear-gradient(135deg, var(--danger-dark), var(--danger-darker)) !important;
  }

  .speak-button.processing {
    background: linear-gradient(135deg, var(--warning-color), var(--warning-dark)) !important;
    cursor: not-allowed;
  }

  .speak-button:disabled {
    background: var(--gray-500);
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
    color: var(--gray-600);
    font-size: 1.1em;
  }

  .dice-result {
    margin: 15px auto;
    text-align: center;
    /* Enhanced container styling for better visibility */
    min-width: 150px;
    min-height: 100px;
    padding: 15px 20px;
    background: var(--gray-50);
    border-radius: 12px;
    border: 2px solid var(--gray-100);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-voice-hover);
  }

  .dice-number {
    font-size: 3.5em;
    font-weight: bold;
    color: var(--primary-color);
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
    line-height: 1;
  }

  .dice-label {
    font-size: 1.1em;
    color: var(--gray-500);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .status {
    font-size: 1.1em;
    font-weight: 500;
    color: var(--gray-500);
    min-height: 24px;
    transition: color 0.3s ease;
  }

  .status.recording {
    color: var(--danger-color);
    font-weight: 600;
  }

  .status.processing {
    color: var(--warning-color);
    font-weight: 600;
  }

  /* Conversation stats container */
  .conversation-stats {
    margin: 20px 0;
    padding: 15px;
    background: var(--gray-50);
    border-radius: 8px;
    border: 1px solid var(--gray-100);
  }

  /* Influence display */
  .influence-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    font-size: 1.2em;
  }

  .stat-label {
    font-weight: 600;
    color: var(--gray-600);
  }

  .stat-value {
    font-weight: bold;
    color: var(--primary-color);
    font-size: 1.3em;
  }

  /* Reveals section */
  .reveals-section {
    margin-top: 20px;
  }

  .reveals-title {
    margin: 0 0 10px 0;
    font-size: 1.1em;
    color: var(--gray-600);
    font-weight: 600;
  }

  .reveals-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .reveal-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: white;
    border-radius: 6px;
    border: 1px solid var(--gray-200);
    transition: all 0.2s ease;
  }

  .reveal-clickable {
    cursor: pointer;
  }

  .reveal-clickable:hover {
    background: var(--gray-50);
    border-color: var(--primary-color);
    transform: translateY(-1px);
    box-shadow: var(--shadow-reveal-hover);
  }

  .reveal-title {
    color: var(--gray-800);
    flex: 1;
  }

  .reveal-progress {
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.9em;
  }

  .progress-locked {
    background: var(--color-reveal-locked);
    color: var(--color-reveal-locked-text);
  }

  .progress-partial {
    background: var(--color-reveal-partial);
    color: var(--color-reveal-partial-text);
  }

  .progress-complete {
    background: var(--color-reveal-complete);
    color: var(--color-reveal-complete-text);
  }
</style>
