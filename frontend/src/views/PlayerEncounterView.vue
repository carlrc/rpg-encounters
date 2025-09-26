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
      </div>
    </div>

    <!-- Encounter View -->
    <div v-else class="encounter-view" :class="{ 'has-interaction-panel': selectedCharacter }">
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
              :class="['challenge-button', { active: isChallengeMode }]"
              :disabled="isRecording || isProcessing"
            >
              Challenge
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
              :class="['shared-speak-button', { recording: isRecording, processing: isProcessing }]"
              :disabled="isProcessing || (isChallengeMode && !selectedSkill)"
            >
              {{ buttonText }}
            </button>
          </div>

          <!-- Status Text -->
          <div
            :class="['shared-status-text', { recording: isRecording, processing: isProcessing }]"
          >
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
  import { serializeError } from 'serialize-error'
  import { getInitials } from '../utils/avatarUtils.js'
  import { getPlayerEncounter } from '../services/api.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useWorldStore } from '../stores/world.js'
  import { useNotification } from '../composables/useNotification.js'
  import WebSocketStreamPlayer from '../composables/audio/WebSocketStreamPlayer.js'
  import { useWebSocketAudioHandler } from '../composables/audio/useWebSocketAudioHandler.js'

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
      const isChallengeMode = ref(false)
      const selectedSkill = ref('')
      const diceRoll = ref(null)
      const influenceScore = ref(null)

      // Local WebSocket progressive audio player
      let streamPlayer = null

      // WebSocket Audio Handler
      const {
        isRecording,
        isProcessing,
        checkMicrophoneAccess,
        startRecording,
        stopRecording,
        connectWebSocket,
        closeWebSocket,
        cleanup: cleanupAudioHandler,
      } = useWebSocketAudioHandler({
        audioElementRef: streamAudio,
        worldId: worldStore.currentWorldId,
        onConversationData: (json) => {
          // Handle conversation data for players
          if (isChallengeMode.value && json.influence !== undefined) {
            // For challenge mode, show the total roll (d20 + modifiers)
            influenceScore.value = json.influence
          }
          // For conversation mode, players don't see influence scores
        },
      })

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
          // TODO: function is being called in lifecycle hook after logout
          if (error.message?.includes('401') || error.message?.includes('404')) {
            encounter.value = null // No encounter assigned
          } else {
            console.error('Error loading encounter:', JSON.stringify(serializeError(error)))
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

      const closeCharacterInteraction = async () => {
        // Clean up any active recording/websocket
        if (isRecording.value) {
          stopRecording()
        }
        await cleanupAudioHandler(streamPlayer)
        selectedCharacter.value = null
      }

      const toggleChallengeMode = () => {
        isChallengeMode.value = !isChallengeMode.value
        selectedSkill.value = ''
        influenceScore.value = null
        diceRoll.value = null
      }

      const processAudioChunk = async (audioBlob) => {
        await streamPlayer.append(audioBlob)
      }

      const toggleRecording = async () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          if (!selectedCharacter.value) return

          if (isChallengeMode.value) {
            // Generate random D20 roll for challenge
            diceRoll.value = Math.floor(Math.random() * 20) + 1
          }

          streamPlayer = new WebSocketStreamPlayer({
            audioEl: streamAudio.value || undefined,
          })
          void streamPlayer.prepare({ fromUserGesture: true })

          // Check microphone access before opening WebSocket
          const microphoneAvailable = await checkMicrophoneAccess()
          if (!microphoneAvailable) {
            return
          }

          connectWebSocket({
            encounterId: encounter.value.id,
            selectedPlayerId: playerId.value,
            characterId: selectedCharacter.value.id,
            isChallengeMode: isChallengeMode.value,
            selectedSkill: selectedSkill.value,
            diceRoll: diceRoll.value,
            streamPlayer,
            processAudioChunk,
            playerInitiated: true,
          })

          startRecording()
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

      onUnmounted(async () => {
        await closeCharacterInteraction()
      })

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

  .encounter-view.has-interaction-panel {
    padding-bottom: 400px; /* Add padding when interaction panel is open */
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
    /* Add fallback solid background to ensure opacity */
    background-color: #ffffff;
    border-top: 1px solid var(--border-default);
    padding: var(--spacing-lg);
    padding-bottom: calc(var(--spacing-lg) + env(safe-area-inset-bottom));
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
    max-height: 70vh;
    overflow-y: auto;
    z-index: 1000;
    -webkit-overflow-scrolling: touch;
    /* Allow both horizontal and vertical touch scrolling */
    touch-action: auto;
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

  .challenge-button {
    padding: 12px 24px;
    font-size: 1em;
    font-weight: 600;
    border: 2px solid var(--gray-500);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 120px;
    background: white;
    color: var(--gray-500);
    box-shadow: var(--shadow-voice-hover);
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
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

  /* Tablet optimizations */
  @media (min-width: 768px) and (max-width: 1023px) {
    .interaction-panel {
      background-color: rgba(255, 255, 255, 0.98); /* Better opacity for tablets */
      backdrop-filter: blur(10px);
    }

    .encounter-view.has-interaction-panel {
      padding-bottom: 450px; /* More padding for larger tablet screen */
    }
  }

  /* Mobile Responsiveness */
  @media (max-width: 767px) {
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

    .encounter-view.has-interaction-panel {
      padding-bottom: 320px; /* Reduce padding on mobile */
    }

    .shared-speak-button {
      padding: var(--spacing-md) var(--spacing-lg);
      min-width: 100px;
      min-height: 56px;
    }
  }
</style>
