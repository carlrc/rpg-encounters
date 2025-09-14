import { ref, onUnmounted } from 'vue'

export function useAudioPlayer() {
  const activeAudio = ref(null)
  const playingAudioId = ref(null)
  const isLoading = ref(false)
  const isPlaying = ref(false)
  const error = ref(null)

  /**
   * Check if MediaSource Extensions are supported
   */
  const supportsMediaSource = () => {
    return window.MediaSource && MediaSource.isTypeSupported('audio/mp4; codecs="mp4a.40.2"')
  }

  /**
   * Play audio progressively from WebSocket chunks using MediaSource Extensions
   */
  const playWebSocketAudio = (audioId = 'websocket') => {
    try {
      stopAudio()

      isLoading.value = true
      error.value = null
      playingAudioId.value = audioId

      if (supportsMediaSource()) {
        playWebSocketAudioWithMediaSource()
      } else {
        error.value = 'Progressive audio playback not supported in this browser'
        isLoading.value = false
      }
    } catch (err) {
      error.value = 'Progressive audio setup failed'
      cleanup()
    }
  }

  /**
   * MediaSource-based progressive audio player class
   */
  class MediaSourceAudioPlayer {
    constructor(onError, onLoadedData, onEnded, onPlaybackStart) {
      this.onError = onError
      this.onLoadedData = onLoadedData
      this.onEnded = onEnded
      this.onPlaybackStart = onPlaybackStart

      this.audio = null
      this.mediaSource = null
      this.sourceBuffer = null
      this.pendingChunks = []
      this.chunksReceived = 0
      this.hasStartedPlayback = false
      this.isSourceOpen = false
      this.isEnded = false
      this.mimeType = 'audio/mp4; codecs="mp4a.40.2"'
    }

    initialize() {
      this.mediaSource = new MediaSource()
      this.audio = new Audio()
      this.audio.src = URL.createObjectURL(this.mediaSource)

      this.setupMediaSourceEvents()
      this.setupAudioEvents()
    }

    setupMediaSourceEvents() {
      this.mediaSource.addEventListener('sourceopen', () => {
        this.isSourceOpen = true
        this.createSourceBuffer()
      })

      this.mediaSource.addEventListener('error', () => {
        this.onError('Media source error')
      })
    }

    setupAudioEvents() {
      this.audio.onloadeddata = () => {
        this.onLoadedData()
      }

      this.audio.onended = () => {
        this.onEnded()
      }

      this.audio.onerror = () => {
        this.onError('Audio playback failed')
      }
    }

    createSourceBuffer() {
      try {
        this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
        this.setupSourceBufferEvents()
        this.processPendingChunks()
      } catch (err) {
        this.onError('Failed to create audio buffer')
      }
    }

    setupSourceBufferEvents() {
      this.sourceBuffer.addEventListener('updateend', () => {
        this.processPendingChunks()
        this.tryStartPlayback()
        this.tryEndStream()
      })

      this.sourceBuffer.addEventListener('error', () => {
        this.onError('Audio buffer error')
      })
    }

    processPendingChunks() {
      if (this.pendingChunks.length > 0 && !this.sourceBuffer.updating) {
        const nextChunk = this.pendingChunks.shift()
        this.appendToBuffer(nextChunk)
      }
    }

    tryStartPlayback() {
      if (!this.hasStartedPlayback && this.chunksReceived > 0) {
        this.startPlayback()
      }
    }

    tryEndStream() {
      if (
        this.isEnded &&
        this.pendingChunks.length === 0 &&
        this.mediaSource.readyState === 'open'
      ) {
        this.endMediaSource()
      }
    }

    async startPlayback() {
      if (this.hasStartedPlayback || !this.audio) return

      this.hasStartedPlayback = true
      try {
        await this.audio.play()
        this.onPlaybackStart()
      } catch (error) {
        this.onError('Audio play failed')
      }
    }

    appendToBuffer(chunk) {
      try {
        this.sourceBuffer.appendBuffer(chunk)
      } catch (err) {
        this.pendingChunks.push(chunk)
      }
    }

    appendChunk(chunk) {
      this.chunksReceived++

      if (this.isSourceOpen && this.sourceBuffer && !this.sourceBuffer.updating) {
        this.appendToBuffer(chunk)
      } else {
        this.pendingChunks.push(chunk)
      }
    }

    endStream() {
      this.isEnded = true

      if (
        this.sourceBuffer &&
        !this.sourceBuffer.updating &&
        this.pendingChunks.length === 0 &&
        this.mediaSource.readyState === 'open'
      ) {
        this.endMediaSource()
      }
    }

    endMediaSource() {
      try {
        this.mediaSource.endOfStream()
      } catch (err) {
        // Ignore endOfStream errors as they're usually harmless
      }
    }

    getAudioData() {
      return {
        audio: this.audio,
        url: this.audio?.src,
        mediaSource: this.mediaSource,
      }
    }
  }

  /**
   * Create and initialize MediaSource-based audio player
   */
  const playWebSocketAudioWithMediaSource = () => {
    const player = new MediaSourceAudioPlayer(
      (errorMessage) => {
        error.value = errorMessage
        cleanup()
      },
      () => {
        isLoading.value = false
        isPlaying.value = true
      },
      () => {
        cleanup()
      },
      () => {
        // Playback started successfully
      }
    )

    player.initialize()
    const audioData = player.getAudioData()

    // Store references for external access
    activeAudio.value = {
      ...audioData,
      appendChunk: (chunk) => player.appendChunk(chunk),
      endStream: () => player.endStream(),
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
   * Clean up audio resources including MediaSource objects
   */
  const cleanup = () => {
    if (activeAudio.value?.audio) {
      activeAudio.value.audio.pause()
      // Don't clear src immediately if using MediaSource - causes "Empty src" errors
      if (!activeAudio.value.mediaSource) {
        activeAudio.value.audio.src = ''
        activeAudio.value.audio.load()
      }
    }

    if (activeAudio.value?.mediaSource) {
      try {
        if (activeAudio.value.mediaSource.readyState === 'open') {
          activeAudio.value.mediaSource.endOfStream()
        }
      } catch (err) {
        console.log('MediaSource cleanup error (safe to ignore):', err)
      }
    }

    if (activeAudio.value?.url) {
      // Use setTimeout to delay URL cleanup for MediaSource to prevent "Empty src" errors
      if (activeAudio.value.mediaSource) {
        setTimeout(() => URL.revokeObjectURL(activeAudio.value?.url), 100)
      } else {
        URL.revokeObjectURL(activeAudio.value.url)
      }
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
    activeAudio,

    // Methods
    playWebSocketAudio, // For conversation/challenge audio (WebSocket chunks)
    playStreamingResponse, // For voice samples (REST streaming response)
    stopAudio,
  }
}
