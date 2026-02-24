import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { serializeError } from 'serialize-error'
import { checkAuth } from '../../services/api.js'

// Constants
const WEBSOCKET_BASE_URL = import.meta.env.VITE_WEBSOCKET_URL
const AUDIO_SAMPLE_RATE = 16000
const AUDIO_CHANNEL_COUNT = 1
const MEDIA_RECORDER_TIMESLICE = 250

const isMobile = () => {
  return /iPhone|iPad|iPod|Android/.test(navigator.userAgent)
}

// Get MediaRecorder configuration for device
const getAudioConfig = () => {
  if (isMobile()) {
    // Try MP4 first for mobile compatibility, fallback to browser default
    try {
      if (MediaRecorder.isTypeSupported('audio/mp4')) {
        return {
          mimeType: 'audio/mp4',
          formatParam: 'mp4',
        }
      }
    } catch (e) {
      // MediaRecorder.isTypeSupported might not be available
    }
    // Fallback for mobile: use WebM which is more widely supported
    return {
      mimeType: 'audio/webm', // Explicitly request WebM
      formatParam: 'webm', // Tell backend it's WebM
    }
  } else {
    return {
      mimeType: 'audio/webm;codecs=opus', // Standard desktop format
      formatParam: 'webm',
    }
  }
}

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

  // Internal state
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const websocket = ref(null)
  const mediaRecorder = ref(null)

  /**
   * Check authentication status and redirect to login if expired
   */
  const checkAuthAndRedirect = async () => {
    const isAuthenticated = await checkAuth()
    if (!isAuthenticated) {
      router.push('/login')
    }
  }

  /**
   * Check microphone access permissions
   */
  const checkMicrophoneAccess = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: AUDIO_SAMPLE_RATE,
          channelCount: AUDIO_CHANNEL_COUNT,
          echoCancellation: true,
          noiseSuppression: true,
        },
      })
      // Stop the test stream immediately
      stream.getTracks().forEach((track) => track.stop())
      return true
    } catch (error) {
      alert('Could not access microphone. Please check permissions.')
      return false
    }
  }

  /**
   * Start audio recording
   */
  const startRecording = async () => {
    try {
      const audioConfig = getAudioConfig()

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: AUDIO_SAMPLE_RATE,
          channelCount: AUDIO_CHANNEL_COUNT,
          echoCancellation: !isMobile(), // Disable for mobile compatibility
          noiseSuppression: !isMobile(), // Disable for mobile compatibility
        },
      })

      mediaRecorder.value = new MediaRecorder(stream, {
        mimeType: audioConfig.mimeType,
      })

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
          websocket.value.send(event.data)
        }
      }

      mediaRecorder.value.start(MEDIA_RECORDER_TIMESLICE)
      isRecording.value = true
    } catch (error) {
      console.error('Audio recording failed', JSON.stringify(serializeError(error)))
      alert('Could not record audio. Refresh the page and try again.')
    }
  }

  /**
   * Stop audio recording
   */
  const stopRecording = () => {
    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop()
      mediaRecorder.value.stream.getTracks().forEach((track) => track.stop())
    }

    isRecording.value = false
    isProcessing.value = true

    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.send('END')
    }
  }

  /**
   * Close WebSocket connection
   */
  const closeWebSocket = () => {
    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.close()
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
   * Control handlers for WebSocket messages
   */
  const CONTROL = {
    AUDIO_COMPLETE: async (streamPlayer) => {
      // Signal end of stream for progressive playback
      if (streamPlayer) {
        try {
          await streamPlayer.end()
        } catch (e) {
          console.error('Failed to close audio stream', JSON.stringify(serializeError(e)))
        } finally {
          streamPlayer = null
        }
      }
      isProcessing.value = false
      closeWebSocket()
    },
  }

  /**
   * Handle WebSocket messages
   */
  const handleWSMessage = (data, streamPlayer, processAudioChunk) => {
    // Binary audio chunks
    if (data instanceof Blob) {
      processAudioChunk(data)
      // Binary frame handled. Nothing else to process in this message.
      return
    }

    // Text frames: fast path for control tokens
    if (typeof data === 'string') {
      const control = CONTROL[data]
      if (control) {
        control(streamPlayer)
        return
      }

      // Assume it's JSON
      const json = JSON.parse(data)

      if (isBillingError(json)) {
        isProcessing.value = false
        closeWebSocket()
        onBillingError(json)
        return
      }

      if (isConversationData(json) && onConversationData) {
        onConversationData(json)
      }
    }
  }

  /**
   * Connect to WebSocket
   */
  const connectWebSocket = ({
    encounterId,
    selectedPlayerId,
    characterId,
    isChallengeMode = false,
    selectedSkill = '',
    diceRoll = null,
    streamPlayer,
    processAudioChunk,
    playerInitiated = false,
  }) => {
    if (!selectedPlayerId || !characterId) return

    if (isChallengeMode && (!selectedSkill || diceRoll === null)) {
      return
    }

    const audioConfig = getAudioConfig()

    const wsUrl = isChallengeMode
      ? `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/challenge/${selectedPlayerId}/${characterId}?skill=${selectedSkill}&d20_roll=${diceRoll}&world_id=${worldId}&player_init=${playerInitiated}&audio_format=${audioConfig.formatParam}`
      : `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/conversation/${selectedPlayerId}/${characterId}?world_id=${worldId}&player_init=${playerInitiated}&audio_format=${audioConfig.formatParam}`

    try {
      websocket.value = new WebSocket(wsUrl)

      // Set binary type explicitly for better performance
      websocket.value.binaryType = 'blob'

      websocket.value.onopen = () => {
        // WebSocket connected
      }

      websocket.value.onmessage = (event) =>
        handleWSMessage(event.data, streamPlayer, processAudioChunk)

      websocket.value.onerror = (error) => {
        console.error('WebSocket connection error', JSON.stringify(serializeError(error)))
        isProcessing.value = false
        closeWebSocket()
      }

      websocket.value.onclose = async (event) => {
        // Code 1008 policy violation
        if (event.code === 1008) {
          // Check inf session is still valid and redirect if not
          await checkAuthAndRedirect()
        }
        websocket.value = null
      }
    } catch (error) {
      console.error('WebSocket creation failed', JSON.stringify(serializeError(error)))
      isProcessing.value = false
    }
  }

  /**
   * Cleanup function for component unmounting
   */
  const cleanup = async (streamPlayer) => {
    closeWebSocket()

    if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
      mediaRecorder.value.stop()
    }

    // Stop any playing audio
    if (streamPlayer) {
      await streamPlayer.stop()
      streamPlayer = null
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
  }

  return {
    // State
    isRecording,
    isProcessing,

    // Methods
    checkMicrophoneAccess,
    startRecording,
    stopRecording,
    connectWebSocket,
    closeWebSocket,
    cleanup,
  }
}
