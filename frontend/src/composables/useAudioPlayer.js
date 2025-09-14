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
   * Handles streaming audio playback from WebSocket chunks using MediaSource Extensions
   *
   * Flow:
   * 1. Initialize MediaSource and Audio elements
   * 2. Receive chunks via appendChunk() - queued or written immediately
   * 3. Process chunk queue after each buffer update
   * 4. Start playback once first chunk is received
   * 5. Mark stream complete with markStreamComplete() when done
   * 6. Finalize MediaSource once all chunks are processed
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
      this.chunksReceived = 0
      this.hasStartedPlayback = false
      this.isSourceOpen = false
      this.isEnded = false
      this.mimeType = 'audio/mp4; codecs="mp4a.40.2"'
    }

    /**
     * Initialize MediaSource and Audio elements with event handlers
     * Must be called before using the player
     */
    initialize() {
      this.mediaSource = new MediaSource()
      this.audio = new Audio()
      this.audio.src = URL.createObjectURL(this.mediaSource)

      this.setupMediaSourceEvents()
      this.setupAudioEvents()
    }

    /**
     * Set up MediaSource event handlers
     * Creates source buffer when MediaSource opens
     */
    setupMediaSourceEvents() {
      this.mediaSource.addEventListener('sourceopen', () => {
        this.isSourceOpen = true
        this.createSourceBuffer()
      })

      this.mediaSource.addEventListener('error', () => {
        this.onError('Media source error')
      })
    }

    /**
     * Set up Audio element event handlers
     * Connects audio events to callback functions
     */
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

    /**
     * Create and configure the source buffer for audio data
     */
    createSourceBuffer() {
      try {
        this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
        this.setupSourceBufferEvents()
      } catch (err) {
        this.onError('Failed to create audio buffer')
      }
    }

    /**
     * Set up source buffer event handlers
     * After each chunk is processed, check if we can start playback or end stream
     */
    setupSourceBufferEvents() {
      this.sourceBuffer.addEventListener('updateend', () => {
        this.tryStartPlayback()
        this.checkAndEndStream()
      })

      this.sourceBuffer.addEventListener('error', () => {
        this.onError('Audio buffer error')
      })
    }

    /**
     * Start audio playback once we have received the first chunk
     * Only attempts to start once to avoid multiple play() calls
     */
    tryStartPlayback() {
      if (!this.hasStartedPlayback && this.chunksReceived > 0) {
        this.startPlayback()
      }
    }

    /**
     * Check if stream can be finalized and do so if all conditions are met
     * Called after each buffer update to ensure timely finalization
     */
    checkAndEndStream() {
      if (this.isEnded && this.mediaSource.readyState === 'open') {
        this.finalizeMediaSource()
      }
    }

    /**
     * Actually start audio playback and notify callbacks
     * Handles browser autoplay restrictions gracefully
     */
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

    /**
     * Write audio chunk directly to the source buffer
     * Caller should handle any failures by retrying
     */
    writeToBuffer(chunk) {
      this.sourceBuffer.appendBuffer(chunk)
    }

    /**
     * Public method to add audio chunks to the player
     * Waits for buffer to be ready, then writes chunk immediately
     */
    async appendChunk(chunk) {
      this.chunksReceived++

      // Wait for MediaSource and buffer to be ready
      while (!this.isSourceOpen || !this.sourceBuffer) {
        await new Promise((resolve) => setTimeout(resolve, 10))
      }

      // Wait for buffer to not be updating
      while (this.sourceBuffer.updating) {
        await new Promise((resolve) => setTimeout(resolve, 10))
      }

      try {
        this.writeToBuffer(chunk)
      } catch (err) {
        // If append fails, wait a bit and retry once
        await new Promise((resolve) => setTimeout(resolve, 10))
        try {
          this.writeToBuffer(chunk)
        } catch (retryErr) {
          this.onError('Failed to process audio chunk')
        }
      }
    }

    /**
     * Mark the audio stream as complete (no more chunks will be added)
     * If buffer is not busy, immediately finalize the MediaSource
     */
    markStreamComplete() {
      this.isEnded = true

      if (
        this.sourceBuffer &&
        !this.sourceBuffer.updating &&
        this.mediaSource.readyState === 'open'
      ) {
        this.finalizeMediaSource()
      }
    }

    /**
     * Finalize the MediaSource to signal end of stream
     * This allows the audio element to know playback is complete
     */
    finalizeMediaSource() {
      try {
        this.mediaSource.endOfStream()
      } catch (err) {
        // Ignore endOfStream errors as they're usually harmless
      }
    }

    /**
     * Get references to internal audio objects
     * Used for external access to audio element and MediaSource
     */
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
      endStream: () => player.markStreamComplete(),
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
