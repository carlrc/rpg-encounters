<template>
  <div class="player-encounter-page">
    <audio ref="streamAudio" playsinline style="display: none"></audio>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading encounter...</p>
    </div>

    <!-- No Encounter State -->
    <div v-else-if="!encounter" class="empty-state">
      <div class="empty-content">
        <h2>No Active Encounter</h2>
        <p>You are not currently assigned to any encounters.</p>
      </div>
    </div>

    <!-- Encounter View -->
    <div v-else class="encounter-view">
      <!-- Header -->
      <div class="encounter-header">
        <h1 class="encounter-title">{{ encounter.name }}</h1>
        <div v-if="encounter.description" class="encounter-description">
          {{ encounter.description }}
        </div>
      </div>

      <!-- Characters Grid -->
      <div class="characters-section">
        <h2 class="section-title">Characters</h2>
        <div class="characters-grid">
          <div
            v-for="character in encounter.characters"
            :key="character.id"
            class="character-tile"
            @click="openCharacterInteraction(character)"
            :class="{ active: selectedCharacter?.id === character.id }"
          >
            <div class="character-avatar">
              <img
                v-if="character.avatar"
                :src="character.avatar"
                :alt="character.name"
                class="avatar-image"
              />
              <div v-else class="avatar-placeholder">
                <span class="avatar-initials">{{ getInitials(character.name) }}</span>
              </div>
            </div>
            <div class="character-info">
              <div class="character-name">{{ character.name }}</div>
              <div class="character-details">
                <span class="character-race">{{ character.race }}</span>
                <span class="character-profession">{{ character.profession }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Character Interaction Panel -->
      <div v-if="selectedCharacter" class="interaction-panel">
        <div class="panel-header">
          <h3>Talking with {{ selectedCharacter.name }}</h3>
          <button @click="closeCharacterInteraction" class="close-btn">&times;</button>
        </div>

        <!-- Score Display -->
        <div v-if="shouldShowScore" class="score-display">
          <span class="score-label">{{ scoreLabel }}</span>
          <span class="score-value">{{ displayScore }}</span>
        </div>

        <!-- Controls -->
        <div class="interaction-controls">
          <!-- Challenge Mode Toggle -->
          <div class="mode-controls">
            <button
              @click="toggleChallengeMode"
              :class="['mode-btn', { active: isChallengeMode }]"
              :disabled="isRecording || isProcessing"
            >
              {{ isChallengeMode ? 'Conversation' : 'Challenge' }}
            </button>
          </div>

          <!-- Skill Selection (Challenge Mode Only) -->
          <div v-if="isChallengeMode" class="skill-selection">
            <select
              v-model="selectedSkill"
              class="skill-select"
              :disabled="isRecording || isProcessing"
            >
              <option value="">Select a skill</option>
              <option v-for="skill in skills" :key="skill" :value="skill">
                {{ skill }}
              </option>
            </select>
          </div>

          <!-- Main Action Button -->
          <div class="main-controls">
            <button
              @click="toggleRecording"
              :class="['speak-button', { recording: isRecording, processing: isProcessing }]"
              :disabled="isProcessing || (isChallengeMode && !selectedSkill)"
            >
              {{ buttonText }}
            </button>
          </div>

          <!-- Status Text -->
          <div :class="['status-text', { recording: isRecording, processing: isProcessing }]">
            {{ statusText }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { getInitials } from '../utils/avatarUtils.js'
  import { getPlayerEncounter } from '../services/api.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useWorldStore } from '../stores/world.js'
  import { useNotification } from '../composables/useNotification.js'
  import WebSocketStreamPlayer from '../composables/audio/WebSocketStreamPlayer.js'

  // Constants
  const WEBSOCKET_BASE_URL = import.meta.env.VITE_WEBSOCKET_URL
  const AUDIO_SAMPLE_RATE = 16000
  const AUDIO_CHANNEL_COUNT = 1
  const MEDIA_RECORDER_TIMESLICE = 250

  export default {
    name: 'PlayerEncounterView',
    setup() {
      const route = useRoute()
      const router = useRouter()
      const gameDataStore = useGameDataStore()
      const worldStore = useWorldStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const { showError } = useNotification()

      // Data
      const loading = ref(true)
      const encounter = ref(null)
      const selectedCharacter = ref(null)
      const streamAudio = ref(null)

      // Interaction state
      const isRecording = ref(false)
      const isProcessing = ref(false)
      const websocket = ref(null)
      const mediaRecorder = ref(null)
      const isChallengeMode = ref(false)
      const selectedSkill = ref('')
      const diceRoll = ref(null)
      const influenceScore = ref(null)

      // Local WebSocket progressive audio player
      let streamPlayer = null

      // Computed properties
      const playerId = computed(() => route.params.playerId)
      const skills = computed(() => gameData.value?.skills || [])

      const buttonText = computed(() => {
        if (isProcessing.value) return 'Processing...'
        return isRecording.value ? 'Stop' : 'Speak'
      })

      const statusText = computed(() => {
        if (isProcessing.value) return 'Processing your message...'
        if (isRecording.value) return 'Listening... Tap Stop when done'
        if (isChallengeMode.value && !selectedSkill.value) return 'Select a skill for challenge'
        if (isChallengeMode.value) return 'Tap Speak to start challenge'
        return 'Tap Speak to start conversation'
      })

      const scoreLabel = computed(() => {
        return isChallengeMode.value ? 'D20 Roll:' : 'Influence:'
      })

      const displayScore = computed(() => {
        if (isChallengeMode.value) {
          return influenceScore.value !== null ? influenceScore.value : 0
        }
        return influenceScore.value
      })

      const shouldShowScore = computed(() => {
        return influenceScore.value !== null || isChallengeMode.value
      })

      // Methods
      const loadEncounter = async () => {
        try {
          loading.value = true
          const encounterData = await getPlayerEncounter(playerId.value)
          encounter.value = encounterData

          // TODO: This is already done when they authenticate and exists in session
          // Set world ID in world store if it's not already set
          if (encounterData && encounterData.world_id && !worldStore.currentWorldId) {
            worldStore.setCurrentWorldId(encounterData.world_id)
          }
        } catch (error) {
          // TODO: This should be a serialized error such as the other encounter pages using the npm package
          console.error('Error loading encounter:', error)
          // TODO: remove this
          if (error.message?.includes('404')) {
            encounter.value = null // No encounter assigned
          } else {
            showError('Failed to load encounter')
          }
        } finally {
          loading.value = false
        }
      }

      const openCharacterInteraction = (character) => {
        selectedCharacter.value = character
        // Reset state
        isChallengeMode.value = false
        selectedSkill.value = ''
        influenceScore.value = null
        diceRoll.value = null
      }

      const closeCharacterInteraction = () => {
        // Clean up any active recording/websocket
        if (isRecording.value) {
          stopRecording()
        }
        closeWebSocket()
        selectedCharacter.value = null
      }

      const toggleChallengeMode = () => {
        isChallengeMode.value = !isChallengeMode.value
        selectedSkill.value = ''
        influenceScore.value = null
        diceRoll.value = null
      }

      const toggleRecording = () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          startRecording()
        }
      }

      const startRecording = async () => {
        if (!selectedCharacter.value) return

        try {
          // TODO: Is this exactly what is on the other encounter page? Dont introduce new features
          const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
              sampleRate: AUDIO_SAMPLE_RATE,
              channelCount: AUDIO_CHANNEL_COUNT,
              echoCancellation: true,
              noiseSuppression: true,
            },
          })

          const options = { mimeType: 'audio/webm;codecs=opus' }
          mediaRecorder.value = new MediaRecorder(stream, options)

          // Start WebSocket connection before recording
          await startWebSocketConnection()

          // TODO: Is this the same as the encounter page? I dont' think so
          mediaRecorder.value.ondataavailable = (event) => {
            if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
              websocket.value.send(event.data)
            }
          }

          mediaRecorder.value.start(MEDIA_RECORDER_TIMESLICE)
          isRecording.value = true
        } catch (error) {
          console.error('Error starting recording:', error)
          showError('Failed to access microphone. Please check permissions.')
        }
      }

      const stopRecording = () => {
        if (mediaRecorder.value && isRecording.value) {
          mediaRecorder.value.stop()
          mediaRecorder.value.stream.getTracks().forEach((track) => track.stop())
          isRecording.value = false
          isProcessing.value = true
        }
      }

      const startWebSocketConnection = async () => {
        if (!selectedCharacter.value || !encounter.value) return

        // Initialize stream player
        if (!streamPlayer) {
          streamPlayer = new WebSocketStreamPlayer({ audioEl: streamAudio.value })
        }

        const worldId = encounter.value.world_id
        let wsUrl

        if (isChallengeMode.value) {
          if (!selectedSkill.value) return
          // Generate random D20 roll for challenge
          diceRoll.value = Math.floor(Math.random() * 20) + 1
          wsUrl = `${WEBSOCKET_BASE_URL}/api/encounters/${encounter.value.id}/challenge/${playerId.value}/${selectedCharacter.value.id}?skill=${selectedSkill.value}&d20_roll=${diceRoll.value}&world_id=${worldId}&player_init=true`
        } else {
          wsUrl = `${WEBSOCKET_BASE_URL}/api/encounters/${encounter.value.id}/conversation/${playerId.value}/${selectedCharacter.value.id}?world_id=${worldId}&player_init=true`
        }

        websocket.value = new WebSocket(wsUrl)

        websocket.value.onopen = () => {
          console.log('WebSocket connection opened')
        }

        websocket.value.onmessage = async (event) => {
          try {
            if (typeof event.data === 'string') {
              const message = JSON.parse(event.data)

              if (message.type === 'conversation_data' && !isChallengeMode.value) {
                // For conversation mode, we don't show influence to players
                // but we might receive it - just ignore it
              } else if (message.type === 'challenge_data' && isChallengeMode.value) {
                // For challenge mode, show only the D20 roll result
                if (message.d20_roll !== undefined) {
                  influenceScore.value = message.d20_roll
                }
              } else if (message.type === 'end') {
                // End of stream
                await streamPlayer.end()
                isProcessing.value = false
              }
            } else {
              // Audio chunk
              await streamPlayer.append(event.data)
            }
          } catch (error) {
            console.error('Error processing WebSocket message:', error)
          }
        }

        websocket.value.onerror = (error) => {
          console.error('WebSocket error:', error)
          showError('Connection error occurred')
          isProcessing.value = false
        }

        websocket.value.onclose = () => {
          console.log('WebSocket connection closed')
          isProcessing.value = false
        }
      }

      const closeWebSocket = () => {
        if (websocket.value) {
          websocket.value.close()
          websocket.value = null
        }
        if (streamPlayer) {
          streamPlayer.stop()
          streamPlayer = null
        }
      }

      // Lifecycle
      onMounted(async () => {
        // Initialize game data if needed
        if (!gameData.value || !gameData.value.skills) {
          await gameDataStore.load()
        }
        await loadEncounter()
      })

      onUnmounted(() => {
        closeCharacterInteraction()
      })

      // Watch for route changes
      watch(
        () => route.params.playerId,
        () => {
          closeCharacterInteraction()
          loadEncounter()
        }
      )

      return {
        loading,
        encounter,
        selectedCharacter,
        streamAudio,
        isRecording,
        isProcessing,
        isChallengeMode,
        selectedSkill,
        skills,
        buttonText,
        statusText,
        scoreLabel,
        displayScore,
        shouldShowScore,
        getInitials,
        openCharacterInteraction,
        closeCharacterInteraction,
        toggleChallengeMode,
        toggleRecording,
      }
    },
  }
</script>

<style scoped>
  .player-encounter-page {
    min-height: 100vh;
    background: var(--bg-primary);
    padding: var(--spacing-md);
    padding-bottom: calc(var(--spacing-md) + env(safe-area-inset-bottom));
  }

  /* Loading and Empty States */
  .loading-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-default);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--spacing-lg);
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .empty-content h2 {
    margin: 0 0 var(--spacing-md) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xl);
  }

  .empty-content p {
    margin: 0;
    color: var(--text-muted);
  }

  /* Encounter View */
  .encounter-view {
    max-width: 800px;
    margin: 0 auto;
  }

  .encounter-header {
    text-align: center;
    margin-bottom: var(--spacing-xl);
    padding: var(--spacing-lg);
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-lg);
  }

  .encounter-title {
    margin: 0 0 var(--spacing-md) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xxl);
    font-weight: var(--font-weight-bold);
  }

  .encounter-description {
    color: var(--text-muted);
    font-style: italic;
  }

  /* Characters Section */
  .characters-section {
    margin-bottom: var(--spacing-xl);
  }

  .section-title {
    margin: 0 0 var(--spacing-lg) 0;
    color: var(--text-primary);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    text-align: center;
  }

  .characters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-md);
  }

  .character-tile {
    display: flex;
    align-items: center;
    padding: var(--spacing-lg);
    background: var(--bg-secondary);
    border: 2px solid var(--border-default);
    border-radius: var(--border-radius-lg);
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: 88px; /* Ensure touch-friendly size */
  }

  .character-tile:hover,
  .character-tile.active {
    border-color: var(--primary-color);
    background: var(--primary-alpha-05);
  }

  .character-avatar {
    flex-shrink: 0;
    margin-right: var(--spacing-md);
  }

  .avatar-image,
  .avatar-placeholder {
    width: 56px;
    height: 56px;
    border-radius: 50%;
  }

  .avatar-image {
    object-fit: cover;
    border: 2px solid var(--border-default);
  }

  .avatar-placeholder {
    background: var(--primary-alpha-10);
    border: 2px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .avatar-initials {
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
    font-size: var(--font-size-lg);
  }

  .character-info {
    flex: 1;
    min-width: 0;
  }

  .character-name {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
  }

  .character-details {
    display: flex;
    gap: var(--spacing-sm);
    font-size: var(--font-size-sm);
    color: var(--text-muted);
  }

  .character-race::after {
    content: ' •';
    margin-left: var(--spacing-xs);
  }

  /* Interaction Panel */
  .interaction-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-default);
    padding: var(--spacing-lg);
    padding-bottom: calc(var(--spacing-lg) + env(safe-area-inset-bottom));
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
    max-height: 70vh;
    overflow-y: auto;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-lg);
  }

  .panel-header h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: var(--text-muted);
    cursor: pointer;
    padding: var(--spacing-xs);
    min-width: 44px;
    min-height: 44px;
  }

  /* Score Display */
  .score-display {
    text-align: center;
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    background: var(--primary-alpha-05);
    border-radius: var(--border-radius-md);
  }

  .score-label {
    font-weight: var(--font-weight-semibold);
    color: var(--text-muted);
    margin-right: var(--spacing-sm);
  }

  .score-value {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--text-primary);
  }

  /* Controls */
  .interaction-controls {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .mode-controls {
    display: flex;
    justify-content: center;
  }

  .mode-btn {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: 2px solid var(--border-default);
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-radius: var(--border-radius-md);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    min-height: 44px;
    transition: all 0.2s ease;
  }

  .mode-btn:hover,
  .mode-btn.active {
    border-color: var(--primary-color);
    background: var(--primary-alpha-10);
  }

  .skill-selection {
    display: flex;
    justify-content: center;
  }

  .skill-select {
    min-width: 200px;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-md);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: var(--font-size-base);
    min-height: 44px;
  }

  .main-controls {
    display: flex;
    justify-content: center;
  }

  .speak-button {
    padding: var(--spacing-lg) var(--spacing-xxl);
    border: 3px solid var(--primary-color);
    background: var(--primary-color);
    color: white;
    border-radius: 50px;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    min-width: 120px;
    min-height: 64px;
    transition: all 0.2s ease;
  }

  .speak-button:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
  }

  .speak-button.recording {
    background: var(--danger-color);
    border-color: var(--danger-color);
    animation: pulse 1.5s ease-in-out infinite;
  }

  .speak-button.processing {
    background: var(--warning-color);
    border-color: var(--warning-color);
    cursor: not-allowed;
  }

  .speak-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 var(--danger-color);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(220, 20, 60, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(220, 20, 60, 0);
    }
  }

  .status-text {
    text-align: center;
    color: var(--text-muted);
    font-size: var(--font-size-sm);
    font-style: italic;
  }

  .status-text.recording {
    color: var(--danger-color);
    font-weight: var(--font-weight-medium);
  }

  .status-text.processing {
    color: var(--warning-color);
    font-weight: var(--font-weight-medium);
  }

  /* Mobile Responsiveness */
  @media (max-width: 480px) {
    .player-encounter-page {
      padding: var(--spacing-sm);
    }

    .characters-grid {
      grid-template-columns: 1fr;
    }

    .character-tile {
      padding: var(--spacing-md);
    }

    .interaction-panel {
      padding: var(--spacing-md);
    }

    .speak-button {
      padding: var(--spacing-md) var(--spacing-lg);
      min-width: 100px;
      min-height: 56px;
    }
  }
</style>
