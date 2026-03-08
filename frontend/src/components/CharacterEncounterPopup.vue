<template>
  <SharedEncounterPopup
    :is-open="isOpen"
    :title="`Encounter with ${character?.name}`"
    close-aria-label="Close encounter popup"
    @close="closePopup"
  >
    <template #pre-header>
      <audio ref="streamAudio" playsinline style="display: none"></audio>
    </template>

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
        <button
          v-if="showResetHistory"
          class="reset-history-button"
          :disabled="isRecording || isProcessing"
          aria-label="Reset history"
          @click="resetConversationHistory"
        >
          🔄
        </button>
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
        <div class="shared-encounter-controls-grid">
          <div class="player-selection shared-encounter-controls-cell">
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

          <div
            :class="[
              'skill-selection',
              'shared-encounter-controls-cell',
              { 'shared-encounter-skill-placeholder-cell': !isChallengeMode },
            ]"
          >
            <select
              v-if="isChallengeMode"
              id="skill-select"
              v-model="selectedSkill"
              class="shared-select shared-encounter-skill-select"
              :disabled="isRecording || isProcessing"
            >
              <option value="">Select a skill</option>
              <option v-for="skill in skills" :key="skill" :value="skill">
                {{ skill }}
              </option>
            </select>
            <div v-else class="shared-encounter-controls-placeholder" aria-hidden="true"></div>
          </div>

          <div class="shared-encounter-controls-cell">
            <button
              @click="toggleRecording"
              :class="['shared-speak-button', { recording: isRecording, processing: isProcessing }]"
              :disabled="!selectedPlayerId || isProcessing || (isChallengeMode && !selectedSkill)"
            >
              {{ buttonText }}
            </button>
          </div>

          <div class="shared-encounter-controls-cell">
            <button
              @click="toggleChallengeMode"
              :class="['shared-encounter-challenge-button', { active: isChallengeMode }]"
              :disabled="isRecording || isProcessing"
            >
              Challenge
            </button>
          </div>
        </div>

        <div :class="['shared-status-text', { recording: isRecording, processing: isProcessing }]">
          {{ statusText }}
        </div>
      </div>
    </div>
  </SharedEncounterPopup>

  <BillingErrorPopup :is-open="showBillingErrorPopup" @close="closeBillingErrorPopup" />
  <BillingErrorPopup
    :is-open="showModerationPopup"
    :title="moderationPopupTitle"
    :message="moderationPopupMessage"
    @close="closeModerationPopup"
  />
</template>

<script>
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { getInitials } from '../utils/avatarUtils'
  import { getEncounterStatusText } from '../utils/encounterStatusText'
  import { useGameDataStore } from '../stores/gameData'
  import { useConversationDataStore } from '../stores/conversationData'
  import { useWorldStore } from '../stores/world'
  import { useNotification } from '../composables/useNotification'
  import { useWebSocketAudioHandler } from '../composables/audio/useWebSocketAudioHandler'
  import { deleteConversationHistory } from '../services/api'
  import SharedEncounterPopup from './base/SharedEncounterPopup.vue'
  import BillingErrorPopup from './ui/BillingErrorPopup.vue'

  export default {
    name: 'CharacterEncounterPopup',
    components: {
      SharedEncounterPopup,
      BillingErrorPopup,
    },
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
      const { showError } = useNotification()
      const { data: gameData } = storeToRefs(gameDataStore)
      const router = useRouter()
      const route = useRoute()

      const players = computed(() => props.assignedPlayers || [])
      const streamAudio = ref(null)
      const showBillingErrorPopup = ref(false)
      const showModerationPopup = ref(false)
      const moderationPopupTitle = ref('Moderation Warning')
      const moderationPopupMessage = ref('Your message was blocked.')

      // Encounter state
      const selectedPlayerId = ref('')

      // WebSocket Audio Handler
      const {
        isRecording,
        isProcessing,
        isUnsupported,
        startSession,
        stopSession,
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
        onBillingError: () => {
          showBillingErrorPopup.value = true
        },
        onModeration: (json) => {
          moderationPopupTitle.value = json.title || 'Moderation Warning'
          moderationPopupMessage.value = json.message || 'Your message was blocked.'
          showModerationPopup.value = true
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
        return getEncounterStatusText({
          isRecording: isRecording.value,
          isChallengeMode: isChallengeMode.value,
          hasSelectedSkill: Boolean(selectedSkill.value),
        })
      })

      const skills = computed(() => gameData.value?.skills || [])
      const selectedPlayer = computed(() =>
        players.value.find((player) => String(player.id) === String(selectedPlayerId.value))
      )
      const selectedPlayerName = computed(
        () => selectedPlayer.value?.rl_name || selectedPlayer.value?.name || 'Unknown Player'
      )
      const characterName = computed(() => props.character?.name || 'Unknown Character')

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

      const showResetHistory = computed(() => {
        return Boolean(selectedPlayerId.value) && !isChallengeMode.value && shouldShowScore.value
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
          stopSession()
        }
        closeWebSocket()

        // Reset state
        selectedPlayerId.value = ''
        isChallengeMode.value = false
        selectedSkill.value = ''
        diceRoll.value = null
        showBillingErrorPopup.value = false
        showModerationPopup.value = false

        emit('close')
      }

      const closeBillingErrorPopup = () => {
        showBillingErrorPopup.value = false
      }

      const closeModerationPopup = () => {
        showModerationPopup.value = false
      }

      const resetChallengeState = () => {
        selectedSkill.value = ''
        diceRoll.value = null
      }

      const resetConversationHistory = async () => {
        if (!selectedPlayerId.value || !props.character?.id) {
          return
        }

        const confirmMessage = `Are you sure you want to delete the history between ${selectedPlayerName.value} and ${characterName.value}?`
        if (!confirm(confirmMessage)) {
          return
        }

        try {
          await deleteConversationHistory(
            props.encounterId,
            selectedPlayerId.value,
            props.character.id
          )
          conversationDataStore.clearData(
            props.encounterId,
            selectedPlayerId.value,
            props.character.id
          )
          influenceScore.value = null
          revealsData.value = []
          rawRevealsData.value = []

          if (!isChallengeMode.value) {
            await fetchConversationData()
          }
        } catch (err) {
          console.error('Failed to reset history:', err)
          showError('Failed to reset history. Please try again.')
        }
      }

      const toggleChallengeMode = () => {
        if (isRecording.value || isProcessing.value) return

        isChallengeMode.value = !isChallengeMode.value
        resetChallengeState()
      }

      const prepareChallengeMode = () => {
        diceRoll.value = Math.floor(Math.random() * 20) + 1
        closeWebSocket()
      }

      const toggleRecording = async () => {
        if (isRecording.value) {
          await stopSession()
        } else {
          if (isChallengeMode.value) {
            prepareChallengeMode()
          }

          const ok = await startSession({
            encounterId: props.encounterId,
            selectedPlayerId: selectedPlayerId.value,
            characterId: props.character?.id,
            isChallengeMode: isChallengeMode.value,
            selectedSkill: selectedSkill.value,
            diceRoll: diceRoll.value,
            playerInitiated: false,
          })
          if (!ok) {
            return
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
        await cleanupAudioHandler()
      })

      // Also reset audio/websocket when navigating away to avoid mobile Safari quirks
      onBeforeRouteLeave(async () => {
        await cleanupAudioHandler()
      })

      return {
        players,
        selectedPlayerId,
        isRecording,
        isProcessing,
        buttonText,
        statusText,
        skills,
        selectedPlayerName,
        characterName,
        isChallengeMode,
        selectedSkill,
        diceRoll,
        scoreLabel,
        displayScore,
        shouldShowScore,
        showResetHistory,
        displayRevealsData,
        isPreviewMode,
        closePopup,
        closeBillingErrorPopup,
        closeModerationPopup,
        resetConversationHistory,
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
        showBillingErrorPopup,
        showModerationPopup,
        moderationPopupTitle,
        moderationPopupMessage,
      }
    },
  }
</script>

<style scoped>
  /* Import all encounter styles from EncountersPage.vue */
  .encounter-interface {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    --encounter-col-left: 150px;
    --encounter-col-right: 120px;
    --encounter-controls-gap: 20px;
    --encounter-controls-grid-margin-bottom: 20px;
    --encounter-placeholder-height: 52px;
    --encounter-mobile-max-width: 340px;
    --encounter-controls-mobile-gap: 12px;
    --encounter-controls-mobile-margin-bottom: 20px;
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

  /* Conversation stats container */
  .conversation-stats {
    margin: 20px 0;
    padding: 18px 36px 16px 16px;
    background: var(--gray-50);
    border-radius: 8px;
    border: 1px solid var(--gray-100);
    position: relative;
  }

  .reset-history-button {
    position: absolute;
    top: 6px;
    right: 6px;
    border: none;
    background: transparent;
    color: var(--gray-400);
    font-size: 18px;
    line-height: 1;
    cursor: pointer;
    padding: 2px;
    transition: color 0.2s ease;
  }

  .reset-history-button:hover {
    color: var(--gray-600);
  }

  .reset-history-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Influence display */
  .influence-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    font-size: 1.2em;
    padding-right: 10px;
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

  @media (max-width: 767px) {
    .skill-selection,
    .player-selection {
      width: 100%;
    }

    .encounter-interface .shared-encounter-skill-select {
      min-height: 48px;
      font-size: 16px;
    }
  }
</style>
