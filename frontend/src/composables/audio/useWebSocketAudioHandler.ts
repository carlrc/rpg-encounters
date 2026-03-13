import { ref, toValue } from 'vue'
import { useRouter } from 'vue-router'
import { serializeError } from 'serialize-error'
import { checkAuth } from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { createWebSocketStreamPlayer } from './createWebSocketStreamPlayer'
import { UnsupportedStreamingError } from './streamErrors'
import { useNotification } from '../useNotification'
import { getMicrophoneErrorMessage } from './audioErrorUtils'

// Constants
const WEBSOCKET_BASE_URL = import.meta.env.VITE_WEBSOCKET_URL
const AUDIO_SAMPLE_RATE = 16000
const AUDIO_CHANNEL_COUNT = 1
const MEDIA_RECORDER_TIMESLICE = 250

const RECORDER_MIME_CANDIDATES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/ogg;codecs=opus',
  'audio/ogg',
  'audio/mp4',
]

const PLAYBACK_MIME_CANDIDATES = ['audio/mp4; codecs=mp4a.40.2', 'audio/mp4']

type LlmSlowNotice = {
  type: 'llm_slow'
  model: string
}

type ModerationBlockedNotice = {
  type: 'moderation_blocked'
  message: string
}

type WarningNotice = {
  type: 'warning'
  message: string
}

type ConnectWebSocketParams = {
  encounterId: number | string
  selectedPlayerId: number | string
  characterId: number | string
  resolvedWorldId: number
  isChallengeMode?: boolean
  selectedSkill?: string
  diceRoll?: number | null
  playerInitiated?: boolean
  audioFormatParam: string
}

export const pickRecorderMimeType = () => {
  if (!window.MediaRecorder || typeof MediaRecorder.isTypeSupported !== 'function') return ''
  return RECORDER_MIME_CANDIDATES.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) || ''
}

export const inferFormatParam = (mimeType) => {
  if (!mimeType) return 'webm'
  const lower = mimeType.toLowerCase()
  if (lower.includes('ogg')) return 'ogg'
  if (lower.includes('mp4')) return 'mp4'
  if (lower.includes('webm')) return 'webm'
  return 'webm'
}

export const pickPlaybackMimeType = () => PLAYBACK_MIME_CANDIDATES[0]

/**
 * WebSocket Audio Handler Composable
 * Handles websocket connections and audio recording for encounter interactions
 * while maintaining mobile compatibility. Pure audio/websocket handling only.
 */
export function useWebSocketAudioHandler({
  audioElementRef,
  onConversationData,
  onBillingError,
  worldId,
}) {
  const router = useRouter()
  const authStore = useAuthStore()
  const { showError, showWarning } = useNotification()

  // Internal state
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const isUnsupported = ref(false)
  const websocket = ref(null)
  const mediaRecorder = ref(null)
  const mediaStream = ref(null)
  const streamPlayer = ref(null)
  let playbackAudioEl = null
  let hasShownLlmSlowNotice = false
  const playbackHandlers = {
    pause: () => {
      if (isProcessing.value) {
        clearProcessingIfPlaybackComplete()
      }
    },
    ended: () => {
      if (isProcessing.value) {
        clearProcessingIfPlaybackComplete()
      }
    },
    error: () => {
      if (isProcessing.value) {
        isProcessing.value = false
      }
    },
  }

  const detachPlaybackListeners = () => {
    if (!playbackAudioEl) return
    playbackAudioEl.removeEventListener('pause', playbackHandlers.pause)
    playbackAudioEl.removeEventListener('ended', playbackHandlers.ended)
    playbackAudioEl.removeEventListener('error', playbackHandlers.error)
    playbackAudioEl = null
  }

  const ensurePlaybackListeners = () => {
    const audioEl = audioElementRef?.value
    if (!audioEl) return
    if (playbackAudioEl === audioEl) return
    detachPlaybackListeners()
    playbackAudioEl = audioEl
    playbackAudioEl.addEventListener('pause', playbackHandlers.pause)
    playbackAudioEl.addEventListener('ended', playbackHandlers.ended)
    playbackAudioEl.addEventListener('error', playbackHandlers.error)
  }

  const isAudioPlaybackActive = () => {
    const audioEl = audioElementRef?.value
    if (!audioEl) return false
    if (audioEl.ended) return false
    return true
  }

  const clearProcessingIfPlaybackComplete = () => {
    if (!isAudioPlaybackActive()) {
      isProcessing.value = false
    }
  }

  /**
   * Validate auth session and route to login if it is no longer valid.
   */
  const validateAuthAndRouteToLogin = async (): Promise<void> => {
    let isAuthenticated = false
    try {
      isAuthenticated = await checkAuth()
    } catch {
      // Treat auth-check failures as invalid session and route to login.
      isAuthenticated = false
    }
    if (!isAuthenticated) {
      authStore.setAuthenticated(false)
      router.push('/login')
    }
  }

  const resolveWorldId = (): number | null => {
    // `worldId` is passed by callers from `worldStore.currentWorldId` (Pinia) in DM/player views.
    // `toValue` unwraps ref/computed/plain values; during hydration this can be `number|string|null`.
    // Normalize to a strict positive integer for WS URLs.
    // World IDs are auto-increment DB primary keys, so `0` is not a valid value.
    const rawWorldId = toValue(worldId)
    const normalizedWorldId = Number(rawWorldId)
    if (!Number.isInteger(normalizedWorldId) || normalizedWorldId <= 0) {
      return null
    }
    return normalizedWorldId
  }

  const stopActiveStream = () => {
    if (mediaStream.value) {
      mediaStream.value.getTracks().forEach((track) => track.stop())
      mediaStream.value = null
    }
  }

  /**
   * Close WebSocket connection
   */
  const closeWebSocket = () => {
    if (websocket.value && websocket.value.readyState !== WebSocket.CLOSED) {
      try {
        websocket.value.close()
      } catch (error) {
        console.warn('Failed to close websocket', JSON.stringify(serializeError(error)))
      }
    }
    websocket.value = null
  }

  /**
   * Check if message is conversation data
   */
  const isConversationData = (v) =>
    v && v.type === 'conversation_data' && 'influence' in v && 'reveals' in v

  /**
   * Check if message is billing error
   */
  const isBillingError = (v) => v && v.type === 'billing_error' && v.code === 'INSUFFICIENT_TOKENS'

  /**
   * Check if message is moderation warning
   */
  const isModerationBlocked = (v): v is ModerationBlockedNotice =>
    v && v.type === 'moderation_blocked' && typeof v.message === 'string'

  /**
   * Check if message is warning notice
   */
  const isWarningNotice = (v): v is WarningNotice =>
    v && v.type === 'warning' && typeof v.message === 'string'

  /**
   * Check if message is LLM slow notice
   */
  const isLlmSlowNotice = (v): v is LlmSlowNotice =>
    v && v.type === 'llm_slow' && typeof v.model === 'string'

  /**
   * Control handlers for WebSocket messages
   */
  const CONTROL = {
    AUDIO_COMPLETE: async () => {
      // Signal end of stream for progressive playback
      if (streamPlayer.value) {
        try {
          await streamPlayer.value.end()
        } catch (e) {
          console.error('Failed to close audio stream', JSON.stringify(serializeError(e)))
        } finally {
          streamPlayer.value = null
        }
      }
      clearProcessingIfPlaybackComplete()
      closeWebSocket()
    },
  }

  /**
   * Handle WebSocket messages
   */
  const handleWSMessage = (data: unknown): void => {
    // Binary audio chunks
    if (data instanceof Blob || data instanceof ArrayBuffer || ArrayBuffer.isView(data)) {
      void streamPlayer.value?.append(data).catch((error) => {
        console.error('Audio append failed', JSON.stringify(serializeError(error)))
        isProcessing.value = false
        void streamPlayer.value?.stop()
        streamPlayer.value = null
        closeWebSocket()
      })
      // Binary frame handled. Nothing else to process in this message.
      return
    }

    // Text frames: fast path for control tokens
    if (typeof data === 'string') {
      const control = CONTROL[data]
      if (control) {
        control()
        return
      }

      // Assume it's JSON
      let json: unknown = null
      try {
        json = JSON.parse(data)
      } catch (error) {
        console.warn('Ignoring non-JSON websocket message')
        return
      }

      if (isBillingError(json)) {
        isProcessing.value = false
        closeWebSocket()
        onBillingError(json)
        return
      }

      if (isWarningNotice(json)) {
        showError(json.message)
        return
      }

      if (isModerationBlocked(json)) {
        showWarning(json.message)
        return
      }

      if (isLlmSlowNotice(json)) {
        if (!hasShownLlmSlowNotice) {
          showWarning(`Model ${json.model} is responding slower than usual...`)
          hasShownLlmSlowNotice = true
        }
        return
      }

      if (isConversationData(json) && onConversationData) {
        onConversationData(json)
        return
      }
    }

    const preview = JSON.stringify(data) || '{}'
    console.warn('Unhandled websocket message type', preview)
  }

  /**
   * Connect to WebSocket
   */
  const connectWebSocket = ({
    encounterId,
    selectedPlayerId,
    characterId,
    resolvedWorldId,
    isChallengeMode = false,
    selectedSkill,
    diceRoll = null,
    playerInitiated = false,
    audioFormatParam = 'webm',
  }: ConnectWebSocketParams): Promise<boolean> => {
    const wsUrl = isChallengeMode
      ? `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/challenge/${selectedPlayerId}/${characterId}?skill=${selectedSkill}&d20_roll=${diceRoll}&world_id=${resolvedWorldId}&player_init=${playerInitiated}&audio_format=${audioFormatParam}`
      : `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/conversation/${selectedPlayerId}/${characterId}?world_id=${resolvedWorldId}&player_init=${playerInitiated}&audio_format=${audioFormatParam}`

    return new Promise<boolean>((resolve, reject) => {
      // This promise models startup handshake only: resolve(true) once socket opens,
      // resolve(false) if the socket closes/errors before open.
      let opened = false
      try {
        websocket.value = new WebSocket(wsUrl)

        // Set binary type explicitly for better performance
        websocket.value.binaryType = 'blob'

        websocket.value.onopen = () => {
          opened = true
          resolve(true)
        }

        websocket.value.onmessage = (event) => handleWSMessage(event.data)

        websocket.value.onerror = (error) => {
          console.error('WebSocket connection error', JSON.stringify(serializeError(error)))
          isProcessing.value = false
          isRecording.value = false
          closeWebSocket()
          if (!opened) {
            // Startup failed before the handshake completed.
            resolve(false)
          }
        }

        websocket.value.onclose = (event) => {
          if (event.code === 1008) {
            // Check if session is still valid and redirect if not.
            void validateAuthAndRouteToLogin()
          }
          if (!opened) {
            console.error('WebSocket closed before connection was established')
            websocket.value = null
            resolve(false)
          } else {
            // `onclose` still fires after a successful open; this is runtime teardown.
            // The startup promise was already settled in `onopen`, so only cleanup here.
            clearProcessingIfPlaybackComplete()
            isRecording.value = false
            websocket.value = null
          }
        }
      } catch (error) {
        console.error('WebSocket creation failed', JSON.stringify(serializeError(error)))
        isProcessing.value = false
        reject(error)
      }
    })
  }

  const createStreamPlayer = (mimeType) => {
    try {
      if (streamPlayer.value) {
        void streamPlayer.value.stop()
        streamPlayer.value = null
      }
      streamPlayer.value = createWebSocketStreamPlayer({
        audioEl: audioElementRef?.value || undefined,
        mimeType,
      })
      void streamPlayer.value.prepare({ fromUserGesture: true })
      if (streamPlayer.value?.mode === 'buffered') {
        showError(
          'Audio streaming not supported in this browser. Playback will start after processing.'
        )
      }
      return true
    } catch (error) {
      if (error instanceof UnsupportedStreamingError) {
        return false
      }
      throw error
    }
  }

  const startSession = async ({
    encounterId,
    selectedPlayerId,
    characterId,
    isChallengeMode = false,
    selectedSkill,
    diceRoll = null,
    playerInitiated = false,
  }): Promise<boolean> => {
    if (isRecording.value || isProcessing.value) return false
    isUnsupported.value = false
    ensurePlaybackListeners()

    const resolvedWorldId = resolveWorldId()
    if (!resolvedWorldId || !selectedPlayerId || !characterId) {
      return false
    }
    if (isChallengeMode && (!selectedSkill || diceRoll === null)) {
      return false
    }

    if (!window.MediaRecorder) {
      showError('Audio not supported in this browser.')
      isUnsupported.value = true
      return false
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      showError('Microphone access is not supported on this browser')
      return false
    }

    const audioConstraints = {
      sampleRate: AUDIO_SAMPLE_RATE,
      channelCount: AUDIO_CHANNEL_COUNT,
      echoCancellation: true,
      noiseSuppression: true,
    }

    const requestMicrophone = async () => {
      // Request mic permission first (must be the earliest async step).
      return navigator.mediaDevices.getUserMedia({ audio: audioConstraints })
    }

    try {
      mediaStream.value = await requestMicrophone()
    } catch (error) {
      // Retry with minimal constraints for iOS/WebKit compatibility.
      try {
        mediaStream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
      } catch (fallbackError) {
        showError(getMicrophoneErrorMessage(fallbackError ?? error))
        console.error('getUserMedia failed', JSON.stringify(serializeError(fallbackError)))
        return false
      }
    }

    try {
      const recorderMimeType = pickRecorderMimeType()

      const playbackMimeType = pickPlaybackMimeType()
      if (!playbackMimeType) {
        isUnsupported.value = true
        return false
      }

      const streamReady = createStreamPlayer(playbackMimeType)
      if (!streamReady) {
        showError('Audio not supported in this browser.')
        isUnsupported.value = true
        return false
      }

      mediaRecorder.value = recorderMimeType
        ? new MediaRecorder(mediaStream.value, { mimeType: recorderMimeType })
        : new MediaRecorder(mediaStream.value)

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
          websocket.value.send(event.data)
        }
      }

      mediaRecorder.value.onstop = () => {
        stopActiveStream()
        if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
          websocket.value.send('END')
        }
      }

      const audioFormatParam = inferFormatParam(mediaRecorder.value.mimeType)

      const connected = await connectWebSocket({
        encounterId,
        selectedPlayerId,
        characterId,
        resolvedWorldId,
        isChallengeMode,
        selectedSkill,
        diceRoll,
        playerInitiated,
        audioFormatParam,
      })
      if (!connected) {
        await cleanup()
        return false
      }

      mediaRecorder.value.start(MEDIA_RECORDER_TIMESLICE)
      isRecording.value = true
      return true
    } catch (error) {
      console.error('Audio session failed', JSON.stringify(serializeError(error)))
      showError('Could not start audio. Refresh the page and try again.')
      await cleanup()
      isUnsupported.value = false
      return false
    }
  }

  const stopSession = async () => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      await stopRecorderAndSendEnd()
      isRecording.value = false
      isProcessing.value = true
      return
    }

    isRecording.value = false
  }

  const stopRecorderAndSendEnd = async ({ closeAfter = false } = {}) => {
    if (!mediaRecorder.value || mediaRecorder.value.state === 'inactive') return

    const recorder = mediaRecorder.value
    const stopped = new Promise((resolve) => {
      const handler = () => {
        recorder.removeEventListener('stop', handler)
        resolve(true)
      }
      recorder.addEventListener('stop', handler, { once: true })
    })

    try {
      recorder.stop()
    } catch (error) {
      console.warn('Failed to stop recorder', JSON.stringify(serializeError(error)))
    }

    // Wait for stop event or timeout
    await Promise.race([stopped, new Promise((resolve) => setTimeout(resolve, 1500))])

    if (closeAfter) {
      closeWebSocket()
    }
  }

  /**
   * Cleanup function for component unmounting
   */
  const cleanup = async () => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      await stopRecorderAndSendEnd({ closeAfter: true })
    } else {
      closeWebSocket()
    }

    // Stop any playing audio
    if (streamPlayer.value) {
      await streamPlayer.value.stop()
      streamPlayer.value = null
    }

    // Wipe the audio element to avoid stale state on mobile
    if (audioElementRef?.value) {
      try {
        audioElementRef.value.pause()
        audioElementRef.value.removeAttribute('src')
        audioElementRef.value.load()
      } catch (error) {
        console.warn('Audio element cleanup failed', JSON.stringify(serializeError(error)))
      }
    }

    stopActiveStream()
    mediaRecorder.value = null
    isRecording.value = false
    isProcessing.value = false
    isUnsupported.value = false
    detachPlaybackListeners()
  }

  return {
    // State
    isRecording,
    isProcessing,
    isUnsupported,

    // Methods
    startSession,
    stopSession,
    closeWebSocket,
    cleanup,
  }
}
