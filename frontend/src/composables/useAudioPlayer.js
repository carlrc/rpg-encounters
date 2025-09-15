import { reactive, computed, onUnmounted } from 'vue'

/**
 * Audio player composable for handling progressive WebSocket audio and streaming responses
 * Provides unified state management and proper cleanup for audio playback
 */
export function useAudioPlayer() {
  // Consolidated state management
  const state = reactive({
    activeAudio: null,
    playingAudioId: null,
    isLoading: false,
    isPlaying: false,
    error: null,
    currentSessionId: null,
    isInitialized: false,
  })

  /**
   * Check if MediaSource Extensions are supported
   * @returns {boolean} True if MediaSource is supported
   */
  const supportsMediaSource = () => {
    return window.MediaSource && MediaSource.isTypeSupported('audio/mp4; codecs="mp4a.40.2"')
  }

  /**
   * Validates if the current session is still active
   * @param {string} sessionId - Session ID to validate
   * @returns {boolean} True if session is valid
   */
  const isSessionValid = (sessionId) => {
    return sessionId && sessionId === state.currentSessionId
  }

  /**
   * Safely sets error state with proper cleanup
   * @param {string} errorMessage - Error message to set
   */
  const setError = (errorMessage) => {
    state.error = errorMessage
    state.isLoading = false
    state.isPlaying = false
  }

  /**
   * Play audio progressively from WebSocket chunks using MediaSource Extensions
   * @param {string} audioId - Unique identifier for this audio stream
   * @returns {Promise<void>}
   */
  const playWebSocketAudio = async (audioId = 'websocket') => {
    try {
      // Only stop existing audio if we're switching to a different stream
      if (state.playingAudioId && state.playingAudioId !== audioId) {
        await stopAudio()
      }

      // Always initialize when called - caller knows this is needed
      state.currentSessionId = crypto.randomUUID()
      state.isLoading = true
      state.error = null
      state.playingAudioId = audioId

      if (supportsMediaSource()) {
        await playWebSocketAudioWithMediaSource()
      } else {
        setError('Progressive audio playback not supported in this browser')
      }
    } catch (err) {
      console.error('Failed to initialize progressive audio:', err)
      setError('Progressive audio setup failed')
      await cleanup()
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
   *
   * @class MediaSourceAudioPlayer
   */
  class MediaSourceAudioPlayer {
    /**
     * Creates a new MediaSourceAudioPlayer instance
     * @param {Function} onError - Callback for error handling
     * @param {Function} onLoadedData - Callback when audio data is loaded
     * @param {Function} onEnded - Callback when playback ends
     * @param {Function} onPlaybackStart - Callback when playback starts
     * @param {string} sessionId - Unique session identifier
     */
    constructor(onError, onLoadedData, onEnded, onPlaybackStart, sessionId) {
      this.onError = onError
      this.onLoadedData = onLoadedData
      this.onEnded = onEnded
      this.onPlaybackStart = onPlaybackStart
      this.sessionId = sessionId

      this.audio = null
      this.mediaSource = null
      this.sourceBuffer = null
      this.hasStartedPlayback = false
      this.isSourceOpen = false
      this.isEnded = false
      this.isValid = true
      this.mimeType = 'audio/mp4; codecs="mp4a.40.2"'
    }

    /**
     * Initialize MediaSource and Audio elements with event handlers
     * Must be called before using the player
     * @returns {void}
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
     * @private
     */
    setupMediaSourceEvents() {
      this.mediaSource.addEventListener('sourceopen', () => {
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.isSourceOpen = true
          this.createSourceBuffer()
        }
      })

      this.mediaSource.addEventListener('error', () => {
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.onError('Media source error')
        }
      })
    }

    /**
     * Set up Audio element event handlers
     * Connects audio events to callback functions
     * @private
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
     * @private
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
     * @private
     */
    setupSourceBufferEvents() {
      this.sourceBuffer.addEventListener('updateend', () => {
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.tryStartPlayback()
          this.checkAndEndStream()
        }
      })

      this.sourceBuffer.addEventListener('error', () => {
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.onError('Audio buffer error')
        }
      })
    }

    /**
     * Start audio playback once we have received the first chunk
     * Only attempts to start once to avoid multiple play() calls
     * @private
     */
    tryStartPlayback() {
      if (!this.hasStartedPlayback) {
        this.startPlayback()
      }
    }

    /**
     * Check if stream can be finalized and do so if all conditions are met
     * Called after each buffer update to ensure timely finalization
     * @private
     */
    checkAndEndStream() {
      if (this.isEnded && this.mediaSource.readyState === 'open') {
        this.finalizeMediaSource()
      }
    }

    /**
     * Actually start audio playback and notify callbacks
     * Handles browser autoplay restrictions gracefully
     * @private
     * @returns {Promise<void>}
     */
    async startPlayback() {
      if (this.hasStartedPlayback || !this.audio || !this.isValid) return

      // Final session check before starting playback
      if (!isSessionValid(this.sessionId)) {
        return
      }

      this.hasStartedPlayback = true
      try {
        await this.audio.play()
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.onPlaybackStart()
        }
      } catch (error) {
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.onError('Audio play failed')
        }
      }
    }

    /**
     * Write audio chunk directly to the source buffer
     * Caller should handle any failures by retrying
     * @private
     * @param {ArrayBuffer} chunk - Audio chunk to write
     */
    writeToBuffer(chunk) {
      this.sourceBuffer.appendBuffer(chunk)
    }

    /**
     * Public method to add audio chunks to the player
     * Waits for buffer to be ready, then writes chunk immediately
     * @param {ArrayBuffer} chunk - Audio chunk to append
     */
    async appendChunk(chunk) {
      // Check if this player is still valid/active
      if (!this.isValid || !isSessionValid(this.sessionId)) {
        return // Ignore chunks for inactive sessions
      }

      // Wait for MediaSource and buffer to be ready
      while (!this.isSourceOpen || !this.sourceBuffer || this.sourceBuffer.updating) {
        await new Promise((resolve) => setTimeout(resolve, 10))
      }

      try {
        this.writeToBuffer(chunk)
      } catch (err) {
        console.error('Failed to write audio chunk:', err)
        if (this.isValid && isSessionValid(this.sessionId)) {
          this.onError('Failed to process audio chunk')
        }
      }
    }

    /**
     * Mark the audio stream as complete (no more chunks will be added)
     * Wait for buffer to finish updating, then finalize MediaSource
     * @returns {Promise<void>}
     */
    async markStreamComplete() {
      // Check if this player is still valid/active
      if (!this.isValid || !isSessionValid(this.sessionId)) {
        return // Ignore end stream for inactive sessions
      }

      this.isEnded = true

      if (this.sourceBuffer && this.mediaSource && this.mediaSource.readyState === 'open') {
        // Simple wait for buffer to stop updating
        while (this.sourceBuffer.updating) {
          await new Promise((resolve) => setTimeout(resolve, 10))
        }
        this.finalizeMediaSource()
      }
    }

    /**
     * Invalidate this player instance to prevent further operations
     * Also cleans up any remaining resources
     * @returns {void}
     */
    invalidate() {
      this.isValid = false

      // Clean up audio element
      if (this.audio) {
        this.audio.pause()
        this.audio.removeAttribute('src')
        this.audio.load()
      }

      // Clean up MediaSource
      if (this.mediaSource && this.mediaSource.readyState === 'open') {
        try {
          this.mediaSource.endOfStream()
        } catch (err) {
          // Ignore errors during cleanup
        }
      }
    }

    /**
     * Finalize the MediaSource to signal end of stream
     * This allows the audio element to know playback is complete
     * @private
     * @returns {Promise<void>}
     */
    async finalizeMediaSource() {
      try {
        if (!this.mediaSource || this.mediaSource.readyState !== 'open' || !this.isValid) {
          return
        }

        // Check session validity before finalizing
        if (!isSessionValid(this.sessionId)) {
          return
        }

        // Simple wait for all buffers to stop updating
        if (this.mediaSource.sourceBuffers.length > 0) {
          while (Array.from(this.mediaSource.sourceBuffers).some((buffer) => buffer.updating)) {
            await new Promise((resolve) => setTimeout(resolve, 10))
          }
        }

        // Final validation before ending stream
        if (
          this.isValid &&
          isSessionValid(this.sessionId) &&
          this.mediaSource.readyState === 'open'
        ) {
          this.mediaSource.endOfStream()
        }
      } catch (err) {
        console.log('MediaSource finalization error (safe to ignore):', err.message)
      }
    }

    /**
     * Get references to internal audio objects
     * Used for external access to audio element and MediaSource
     * @returns {Object} Audio data object
     */
    getAudioData() {
      return {
        audio: this.audio,
        url: this.audio?.src,
        mediaSource: this.mediaSource,
        isValid: this.isValid,
        sessionId: this.sessionId,
      }
    }
  }

  /**
   * Create and initialize MediaSource-based audio player
   * @returns {Promise<void>}
   */
  const playWebSocketAudioWithMediaSource = async () => {
    // Invalidate any existing player before creating a new one
    if (state.activeAudio?.player) {
      state.activeAudio.player.invalidate()
    }

    const player = new MediaSourceAudioPlayer(
      (errorMessage) => {
        setError(errorMessage)
        cleanup()
      },
      () => {
        state.isLoading = false
        state.isPlaying = true
      },
      () => {
        cleanup()
      },
      () => {
        // Playback started successfully
      },
      state.currentSessionId
    )

    player.initialize()
    const audioData = player.getAudioData()

    // Store references for external access
    state.activeAudio = {
      ...audioData,
      player: player,
      sessionId: state.currentSessionId,
      appendChunk: (chunk) => player.appendChunk(chunk),
      endStream: () => player.markStreamComplete(),
    }

    state.isInitialized = true
  }

  /**
   * Play audio from REST streaming response (voice samples)
   * @param {Response} response - Fetch response containing audio data
   * @param {string} audioId - Unique identifier for this audio stream
   * @returns {Promise<void>}
   */
  const playStreamingResponse = async (response, audioId = 'stream') => {
    try {
      await stopAudio()

      state.isLoading = true
      state.error = null
      state.playingAudioId = audioId
      state.currentSessionId = crypto.randomUUID()

      // Convert streaming response to blob
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onloadeddata = () => {
        if (isSessionValid(state.currentSessionId)) {
          state.isLoading = false
          state.isPlaying = true
        }
      }

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        cleanup()
      }

      audio.onerror = () => {
        console.error('Audio playback error')
        URL.revokeObjectURL(audioUrl)
        setError('Audio playback failed')
        cleanup()
      }

      state.activeAudio = {
        audio,
        url: audioUrl,
        sessionId: state.currentSessionId,
      }
      state.isInitialized = true

      await audio.play()
    } catch (err) {
      console.error('Failed to play streaming audio:', err)
      setError('Failed to play streaming audio')
      await cleanup()
    }
  }

  /**
   * Stop currently playing audio
   * @returns {Promise<void>}
   */
  const stopAudio = async () => {
    if (state.activeAudio?.audio) {
      state.activeAudio.audio.pause()
      state.activeAudio.audio.currentTime = 0
    }
    await cleanup()
  }

  /**
   * Clean up audio resources including MediaSource objects
   * @returns {Promise<void>}
   */
  const cleanup = async () => {
    // Invalidate any existing player first to prevent new operations
    if (state.activeAudio?.player) {
      state.activeAudio.player.invalidate()
    }

    if (state.activeAudio?.audio) {
      try {
        state.activeAudio.audio.pause()
        // Don't clear src immediately if using MediaSource - causes "Empty src" errors
        if (!state.activeAudio.mediaSource) {
          state.activeAudio.audio.removeAttribute('src')
          state.activeAudio.audio.load()
        }
      } catch (err) {
        // Ignore audio cleanup errors
      }
    }

    if (state.activeAudio?.mediaSource) {
      try {
        if (state.activeAudio.mediaSource.readyState === 'open') {
          state.activeAudio.mediaSource.endOfStream()
        }
      } catch (err) {
        // Safe to ignore MediaSource finalization errors
      }
    }

    // Clean up URLs with proper timing
    if (state.activeAudio?.url) {
      const urlToRevoke = state.activeAudio.url
      if (state.activeAudio.mediaSource) {
        // Delay URL cleanup for MediaSource to prevent "Empty src" errors
        setTimeout(() => {
          try {
            URL.revokeObjectURL(urlToRevoke)
          } catch (err) {
            // Ignore URL cleanup errors
          }
        }, 150)
      } else {
        try {
          URL.revokeObjectURL(urlToRevoke)
        } catch (err) {
          // Ignore URL cleanup errors
        }
      }
    }

    // Reset all state atomically
    Object.assign(state, {
      activeAudio: null,
      playingAudioId: null,
      isPlaying: false,
      isLoading: false,
      currentSessionId: null,
      isInitialized: false,
      error: null,
    })
  }

  // Cleanup on component unmount
  onUnmounted(async () => {
    await stopAudio()
  })

  return {
    // State - using computed refs to maintain reactivity
    playingAudioId: computed(() => state.playingAudioId),
    isLoading: computed(() => state.isLoading),
    isPlaying: computed(() => state.isPlaying),
    error: computed(() => state.error),
    activeAudio: computed(() => state.activeAudio),
    isInitialized: computed(() => state.isInitialized),

    // Methods - all properly async
    playWebSocketAudio, // For conversation/challenge audio (WebSocket chunks)
    playStreamingResponse, // For voice samples (REST streaming response)
    stopAudio,
    cleanup, // Expose cleanup for manual resource management

    // Utility methods
    isSessionValid: (sessionId) => isSessionValid(sessionId),
    supportsMediaSource,
  }
}
