import { ref, onUnmounted } from 'vue'

export function useAudioPlayer() {
  const activeAudio = ref(null)
  const playingAudioId = ref(null)
  const isLoading = ref(false)
  const isPlaying = ref(false)
  const error = ref(null)

  /**
   * Play audio from WebSocket chunks (conversations/challenges)
   * Exact copy of playAccumulatedAudio() from CharacterEncounterPopup.vue
   */
  const playWebSocketAudio = (audioChunks, audioId = 'websocket') => {
    if (audioChunks.length === 0) {
      return
    }

    try {
      stopAudio() // Stop any currently playing audio first

      isLoading.value = true
      error.value = null
      playingAudioId.value = audioId

      const audioBlob = new Blob(audioChunks)
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        cleanup()
      }

      audio.onerror = () => {
        console.error('Audio playback error')
        URL.revokeObjectURL(audioUrl)
        error.value = 'Audio playback failed'
        cleanup()
      }

      audio.onloadeddata = () => {
        isLoading.value = false
        isPlaying.value = true
      }

      activeAudio.value = { audio, url: audioUrl }

      audio.play().catch(() => {
        console.error('Audio play failed')
        URL.revokeObjectURL(audioUrl)
        error.value = 'Audio play failed'
        cleanup()
      })
    } catch (error) {
      console.error('Audio processing error')
      error.value = 'Audio processing error'
      cleanup()
    }
  }

  /**
   * Play audio from REST streaming response (voice samples)
   */
  const playStreamingResponse = async (response, audioId = 'stream') => {
    try {
      stopAudio()

      isLoading.value = true
      error.value = null
      playingAudioId.value = audioId

      // Convert streaming response to blob
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onloadeddata = () => {
        isLoading.value = false
        isPlaying.value = true
      }

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        cleanup()
      }

      audio.onerror = () => {
        console.error('Audio playback error')
        URL.revokeObjectURL(audioUrl)
        error.value = 'Audio playback failed'
        cleanup()
      }

      activeAudio.value = { audio, url: audioUrl }
      await audio.play()
    } catch (err) {
      console.error('Failed to play streaming audio:', err)
      error.value = 'Failed to play streaming audio'
      cleanup()
    }
  }

  /**
   * Stop currently playing audio
   */
  const stopAudio = () => {
    if (activeAudio.value?.audio) {
      activeAudio.value.audio.pause()
      activeAudio.value.audio.currentTime = 0
    }
    cleanup()
  }

  /**
   * Clean up audio resources
   */
  const cleanup = () => {
    if (activeAudio.value?.url) {
      URL.revokeObjectURL(activeAudio.value.url)
    }
    activeAudio.value = null
    playingAudioId.value = null
    isPlaying.value = false
    isLoading.value = false
  }

  // Cleanup on component unmount
  onUnmounted(() => {
    stopAudio()
  })

  return {
    // State
    playingAudioId,
    isLoading,
    isPlaying,
    error,

    // Methods
    playWebSocketAudio, // For conversation/challenge audio (WebSocket chunks)
    playStreamingResponse, // For voice samples (REST streaming response)
    stopAudio,
  }
}
