<template>
  <div v-if="isOpen" class="encounter-popup-overlay" @click="closePopup">
    <div class="encounter-popup" @click.stop>
      <audio ref="streamAudio" playsinline style="display: none"></audio>
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

        <!-- Challenge/Conversation preview display -->
        <div class="conversation-stats" v-if="shouldShowScore || displayRevealsData.length > 0">
          <div class="influence-display" v-if="shouldShowScore">
            <span class="stat-label">{{ scoreLabel }}</span>
            <span class="stat-value">{{ displayScore }}</span>
          </div>

          <div class="reveals-section" v-if="displayRevealsData.length > 0">
            <h4 class="reveals-title">Reveals {{ isPreviewMode ? '(Preview)' : '' }}</h4>
            <div class="reveals-list">
              <div
                v-for="reveal in displayRevealsData"
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
          <div class="selection-row">
            <div class="player-selection">
              <select
                id="player-select"
                v-model="selectedPlayerId"
                class="shared-select"
                :disabled="isRecording || isProcessing || players.length === 0"
              >
                <option v-if="players.length === 0" value="" disabled>No players assigned</option>
                <option v-else value="">Select a player</option>
                <option v-for="player in players" :key="player.id" :value="player.id">
                  {{ player.rl_name }}
                </option>
              </select>
            </div>

            <div v-if="isChallengeMode" class="skill-selection">
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
          </div>

          <div class="control-buttons">
            <button
              @click="toggleRecording"
              :class="['shared-speak-button', { recording: isRecording, processing: isProcessing }]"
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
  import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { getInitials } from '../utils/avatarUtils.js'
  import { useGameDataStore } from '../stores/gameData.js'
  import { useConversationDataStore } from '../stores/conversationData.js'
  import { useWorldStore } from '../stores/world.js'
  import WebSocketStreamPlayer from '../composables/audio/WebSocketStreamPlayer.js'
  import { useWebSocketAudioHandler } from '../composables/audio/useWebSocketAudioHandler.js'
  import { serializeError } from 'serialize-error'

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
      initialPlayerId: {
        type: [String, Number],
        default: null,
      },
      assignedPlayers: {
        type: Array,
        default: () => [],
      },
    },
    emits: ['close'],
    setup(props, { emit }) {
      const gameDataStore = useGameDataStore()
      const conversationDataStore = useConversationDataStore()
      const worldStore = useWorldStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const router = useRouter()
      const route = useRoute()

      // Local WebSocket progressive audio player (explicit control)
      let streamPlayer = null

      const players = computed(() => props.assignedPlayers || [])
      const streamAudio = ref(null)

      // Encounter state
      const selectedPlayerId = ref('')

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
          // Update local state from websocket data
          influenceScore.value = json.influence ?? null
          revealsData.value = Array.isArray(json.reveals) ? json.reveals : []

          // Handle caching in component - only cache conversation data, not challenge data
          if (selectedPlayerId.value && props.character?.id && !isChallengeMode.value) {
            const cacheKey = `${props.encounterId}-${selectedPlayerId.value}-${props.character.id}`
            conversationDataStore.cache[cacheKey] = {
              influence: json.influence ?? null,
              reveals: json.reveals || [],
              rawReveals: json.raw_reveals || json.reveals || [],
            }
          }
        },
      })

      // Conversation data state
      const influenceScore = ref(null)
      const revealsData = ref([])

      // Challenge mode state
      const isChallengeMode = ref(false)
      const selectedSkill = ref('')
      const diceRoll = ref(null)

      // Raw reveal data from backend (for challenge mode calculations)
      const rawRevealsData = ref([])

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
          return 'Select a Charisma skill for an ability check'
        if (isChallengeMode.value) return 'Click Speak to start challenge'
        return 'Click Speak to start conversation'
      })

      const skills = computed(() => gameData.value?.skills || [])

      // Unified score display computed properties
      const scoreLabel = computed(() => {
        return isChallengeMode.value ? 'D20 Roll:' : 'Influence:'
      })

      const displayScore = computed(() => {
        if (isChallengeMode.value) {
          // Show WebSocket result if available, otherwise show 0 as preview for challenge
          return influenceScore.value !== null ? influenceScore.value : 0
        }
        return influenceScore.value
      })

      const shouldShowScore = computed(() => {
        return influenceScore.value !== null || isChallengeMode.value
      })

      // Challenge mode preview functionality
      const calculateRevealProgress = (reveal, influenceScore) => {
        let unlockedLayers = 0

        // Check each threshold (mimic backend logic)
        if (influenceScore >= reveal.standard_threshold) {
          unlockedLayers += 1
        }
        if (influenceScore >= reveal.privileged_threshold) {
          unlockedLayers += 1
        }
        if (influenceScore >= reveal.exclusive_threshold) {
          unlockedLayers += 1
        }

        // Count total layers (only count non-null/non-empty content)
        let totalLayers = 0
        if (reveal.level_1_content) totalLayers += 1
        if (reveal.level_2_content) totalLayers += 1
        if (reveal.level_3_content) totalLayers += 1

        return {
          id: reveal.id,
          title: reveal.title,
          progress: `${unlockedLayers}/${totalLayers}`,
          unlocked_layers: unlockedLayers,
          total_layers: totalLayers,
        }
      }

      const challengePreviewReveals = computed(() => {
        if (
          !isChallengeMode.value ||
          isRecording.value ||
          isProcessing.value ||
          rawRevealsData.value.length === 0
        ) {
          return []
        }

        // Calculate preview with d20 roll of 0 (no influence)
        return rawRevealsData.value.map((reveal) => calculateRevealProgress(reveal, 0))
      })

      const displayRevealsData = computed(() => {
        if (isChallengeMode.value) {
          // Show WebSocket results if available, otherwise show challenge preview
          return revealsData.value.length > 0 ? revealsData.value : challengePreviewReveals.value
        }
        return revealsData.value
      })

      const isPreviewMode = computed(() => {
        return (
          isChallengeMode.value &&
          revealsData.value.length === 0 &&
          challengePreviewReveals.value.length > 0
        )
      })

      // Encounter functions (simplified from EncountersPage.vue)
      const closePopup = () => {
        // Clean up any active recording/websocket
        if (isRecording.value) {
          stopRecording()
        }
        closeWebSocket()

        // Stop any playing audio
        if (streamPlayer) {
          streamPlayer.stop()
          streamPlayer = null
        }

        // Reset state
        selectedPlayerId.value = ''
        isChallengeMode.value = false
        selectedSkill.value = ''
        diceRoll.value = null

        emit('close')
      }

      const resetChallengeState = () => {
        selectedSkill.value = ''
        diceRoll.value = null
      }

      const toggleChallengeMode = () => {
        if (isRecording.value || isProcessing.value) return

        isChallengeMode.value = !isChallengeMode.value
        resetChallengeState()
      }

      const processAudioChunk = async (audioBlob) => {
        try {
          await streamPlayer.append(audioBlob)
        } catch (error) {
          console.error('Failed to append audio chunk:', JSON.stringify(serializeError(error)))
        }
      }

      const prepareChallengeMode = () => {
        diceRoll.value = Math.floor(Math.random() * 20) + 1
        closeWebSocket()
      }

      const toggleRecording = async () => {
        if (isRecording.value) {
          stopRecording()
        } else {
          if (isChallengeMode.value) {
            prepareChallengeMode()
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
            encounterId: props.encounterId,
            selectedPlayerId: selectedPlayerId.value,
            characterId: props.character?.id,
            isChallengeMode: isChallengeMode.value,
            selectedSkill: selectedSkill.value,
            diceRoll: diceRoll.value,
            streamPlayer,
            processAudioChunk,
            playerInitiated: false,
          })

          startRecording()
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

        const data = await conversationDataStore.getData(
          props.encounterId,
          selectedPlayerId.value,
          props.character.id
        )

        influenceScore.value = data.influence
        revealsData.value = data.reveals

        // Store raw reveals for challenge mode calculations
        rawRevealsData.value = data.rawReveals
      }

      // Reset state when switching modes
      const resetModeState = () => {
        if (isChallengeMode.value) {
          // Switching to challenge mode - clear WebSocket results but keep raw data
          influenceScore.value = null
          revealsData.value = []
        } else {
          // Switching back to conversation mode - use cached data for smooth transition
          if (selectedPlayerId.value) {
            const cached = conversationDataStore.getCached(
              props.encounterId,
              selectedPlayerId.value,
              props.character.id
            )
            if (cached) {
              // Restore from cache immediately for smooth transition
              influenceScore.value = cached.influence
              revealsData.value = cached.reveals
              rawRevealsData.value = cached.rawReveals
            } else {
              // Fetch if not cached yet
              fetchConversationData()
            }
          }
        }
      }

      // Watch for challenge mode changes
      watch(
        () => isChallengeMode.value,
        () => {
          resetModeState()
        }
      )

      // Automatically reset conversation data when character changes
      watch(
        () => props.character?.id,
        (_, oldCharacterId) => {
          influenceScore.value = null
          revealsData.value = []
          rawRevealsData.value = []
          // Clear cache for old character when character changes
          if (oldCharacterId) {
            conversationDataStore.clearCharacterCache(oldCharacterId)
          }
        }
      )

      watch(
        () => props.assignedPlayers,
        (newPlayers) => {
          const playersList = newPlayers || []

          if (selectedPlayerId.value) {
            const selectedId = String(selectedPlayerId.value)
            if (!playersList.some((player) => String(player.id) === selectedId)) {
              selectedPlayerId.value = ''
            }
            return
          }

          if (props.initialPlayerId) {
            const initialId = String(props.initialPlayerId)
            if (playersList.some((player) => String(player.id) === initialId)) {
              selectedPlayerId.value = props.initialPlayerId
            }
          }
        }
      )

      // Fetch conversation data when player selection changes (only in conversation mode)
      watch(
        () => selectedPlayerId.value,
        () => {
          if (selectedPlayerId.value && !isChallengeMode.value) {
            fetchConversationData()
          } else if (selectedPlayerId.value && isChallengeMode.value) {
            // In challenge mode, clear any existing data to show default state
            influenceScore.value = null
            revealsData.value = []
          }

          // Update URL with new playerId when player selection changes
          if (props.isOpen) {
            router.replace({
              query: {
                ...route.query,
                playerId: selectedPlayerId.value || undefined,
              },
            })
          }
        }
      )

      onMounted(async () => {
        await gameDataStore.load()

        if (props.initialPlayerId) {
          selectedPlayerId.value = props.initialPlayerId
        }
      })

      onUnmounted(async () => {
        closeWebSocket()

        // If recording, stop via composable API to avoid out-of-scope refs
        if (isRecording.value) {
          stopRecording()
        }

        // Stop any playing audio when component unmounts
        if (streamPlayer) {
          await streamPlayer.stop()
          streamPlayer = null
        }

        // Wipe the audio element to avoid stale state on mobile
        if (streamAudio.value) {
          try {
            streamAudio.value.pause()
            streamAudio.value.removeAttribute('src')
            streamAudio.value.load()
          } catch (error) {
            console.warn(
              'Unmounted encounter popup audio element cleanup failed',
              JSON.stringify(serializeError(error))
            )
          }
        }
      })

      // Also reset audio/websocket when navigating away to avoid mobile Safari quirks
      onBeforeRouteLeave(async () => {
        if (isRecording.value) {
          stopRecording()
        }
        closeWebSocket()
        if (streamPlayer) {
          await streamPlayer.stop()
          streamPlayer = null
        }
        if (streamAudio.value) {
          try {
            streamAudio.value.pause()
            streamAudio.value.removeAttribute('src')
            streamAudio.value.load()
          } catch (error) {
            console.warn(
              'Encounter popup audio element cleanup failed (route-leave)',
              JSON.stringify(serializeError(error))
            )
          }
        }
      })

      return {
        players,
        selectedPlayerId,
        isRecording,
        isProcessing,
        buttonText,
        statusText,
        skills,
        isChallengeMode,
        selectedSkill,
        diceRoll,
        scoreLabel,
        displayScore,
        shouldShowScore,
        displayRevealsData,
        isPreviewMode,
        closePopup,
        toggleRecording,
        toggleChallengeMode,
        navigateToCharacter,
        getInitials,
        influenceScore,
        revealsData,
        rawRevealsData,
        getProgressClass,
        navigateToReveal,
        fetchConversationData,
        streamAudio,
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

  .selection-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
  }

  .player-selection {
    width: 150px;
  }

  .skill-selection {
    width: 120px;
  }

  .control-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
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
