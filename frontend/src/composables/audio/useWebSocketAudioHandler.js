import { ref } from 'vue'
import { serializeError } from 'serialize-error'

// Constants
const WEBSOCKET_BASE_URL = import.meta.env.VITE_WEBSOCKET_URL
const AUDIO_SAMPLE_RATE = 16000
const AUDIO_CHANNEL_COUNT = 1
const MEDIA_RECORDER_TIMESLICE = 250

/**
 * WebSocket Audio Handler Composable
 * Handles websocket connections and audio recording for encounter interactions
 * while maintaining mobile compatibility. Pure audio/websocket handling only.
 */
export function useWebSocketAudioHandler({ audioElementRef, onConversationData, worldId }) {
  // Internal state
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const websocket = ref(null)
  const mediaRecorder = ref(null)

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
  }) => {
    if (!selectedPlayerId || !characterId) return

    if (isChallengeMode && (!selectedSkill || diceRoll === null)) {
      return
    }

    const wsUrl = isChallengeMode
      ? `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/challenge/${selectedPlayerId}/${characterId}?skill=${selectedSkill}&d20_roll=${diceRoll}&world_id=${worldId}`
      : `${WEBSOCKET_BASE_URL}/api/encounters/${encounterId}/conversation/${selectedPlayerId}/${characterId}?world_id=${worldId}`

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

      websocket.value.onclose = () => {
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
