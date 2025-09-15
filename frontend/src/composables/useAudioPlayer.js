import { reactive, computed, onUnmounted } from 'vue'

/**
 * Audio player composable for handling progressive WebSocket audio and streaming responses
 * Refactored to:
 * - Separate buffering from playback
 * - Use event-driven SourceBuffer flow (no polling loops)
 * - Unify lifecycle/cleanup
 * - Provide a clear progressive StreamHandle API
 */
export function useAudioPlayer() {
  // Consolidated state management (UI-facing)
  const state = reactive({
    playingAudioId: null,
    isLoading: false,
    isPlaying: false,
    error: null,
    isInitialized: false,
    // Back-compat exposure (legacy shape; will be null unless progressive stream is active)
    activeAudio: null,
  })

  // Internal mutable runtime objects (not reactive)
  let generation = 0
  let token = null
  /** @type {null | { generation: number, aborted: boolean }} */
  let current = {
    type: null, // 'progressive' | 'sample' | null
    // Progressive
    player: null, // Player instance
    handle: null, // StreamHandle
    // Sample
    sampleAudio: null, // HTMLAudioElement
    sampleUrl: null, // objectURL string
  }

  /**
   * Check if MediaSource Extensions are supported
   * @returns {boolean} True if MediaSource is supported
   */
  const supportsMediaSource = () => {
    return !!(window.MediaSource && MediaSource.isTypeSupported('audio/mp4; codecs="mp4a.40.2"'))
  }

  /**
   * Central error setter with safe UI state flip
   * @param {string} errorMessage
   */
  const setError = (errorMessage) => {
    state.error = errorMessage
    state.isLoading = false
    state.isPlaying = false
  }

  /**
   * Simple abort token factory for session invalidation
   * @returns {{ generation: number, aborted: boolean }}
   */
  const newToken = () => ({ generation: ++generation, aborted: false })

  /**
   * Buffer controller that manages a queued, event-driven append flow to SourceBuffer
   * No polling; driven by 'updateend' events and readiness signals.
   */
  class MediaSourceBufferController {
    /**
     * @param {MediaSource} mediaSource
     * @param {string} mimeType
     * @param {{ generation: number, aborted: boolean }} tokenRef
     * @param {(msg: string) => void} onError
     * @param {() => void} onUpdateEnd
     */
    constructor(mediaSource, mimeType, tokenRef, onError, onUpdateEnd) {
      this.mediaSource = mediaSource
      this.mimeType = mimeType
      this.token = tokenRef
      this.onError = onError
      this.onUpdateEnd = onUpdateEnd

      this.sourceBuffer = null
      this.queue = []
      this.ready = false
      this.finalized = false
      this.streamEnded = false

      this._onSourceOpen = this._onSourceOpen.bind(this)
      this._onBufferUpdateEnd = this._onBufferUpdateEnd.bind(this)
      this._onBufferError = this._onBufferError.bind(this)

      this.mediaSource.addEventListener('sourceopen', this._onSourceOpen)
      this.mediaSource.addEventListener('error', () => {
        if (!this._valid()) return
        this.onError('Media source error')
      })
    }

    _valid() {
      return this.token && !this.token.aborted
    }

    _onSourceOpen() {
      if (!this._valid()) return
      try {
        this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
        this.sourceBuffer.addEventListener('updateend', this._onBufferUpdateEnd)
        this.sourceBuffer.addEventListener('error', this._onBufferError)
        this.ready = true
        // Try appending immediately if there are queued chunks
        this._maybeAppend()
      } catch (err) {
        this.onError('Failed to create audio buffer')
      }
    }

    _onBufferError() {
      if (!this._valid()) return
      this.onError('Audio buffer error')
    }

    _onBufferUpdateEnd() {
      if (!this._valid()) return
      // Component that wraps controller can use this to tryPlay on first data, etc.
      this.onUpdateEnd()
      // Continue draining queue or finalize when needed
      if (!this._maybeAppend()) {
        this._maybeFinalize()
      }
    }

    /**
     * Enqueue a chunk to append (ArrayBuffer). If ready and not updating, append now.
     * @param {ArrayBuffer} chunk
     */
    async write(chunk) {
      if (!this._valid()) return
      this.queue.push(chunk)
      this._maybeAppend()
    }

    /**
     * Mark no more chunks will come; when queue is empty and not updating, endOfStream.
     */
    async end() {
      if (!this._valid()) return
      this.streamEnded = true
      this._maybeFinalize()
    }

    /**
     * Abort further operations; the Player handles ultimate disposal.
     */
    abort() {
      if (!this.token) return
      this.queue = []
      this.token.aborted = true
    }

    /**
     * Attempt to append next queued chunk if ready and not updating.
     * @returns {boolean} true if appended something, false otherwise
     */
    _maybeAppend() {
      if (!this._valid()) return false
      if (!this.ready || !this.sourceBuffer || this.sourceBuffer.updating) return false
      if (this.queue.length === 0) return false

      const next = this.queue.shift()
      try {
        this.sourceBuffer.appendBuffer(next)
        return true
      } catch (err) {
        this.onError('Failed to process audio chunk')
        return false
      }
    }

    _maybeFinalize() {
      if (!this._valid()) return
      if (!this.streamEnded) return
      if (this.finalized) return
      if (this.mediaSource.readyState !== 'open') return
      if (this.sourceBuffer && this.sourceBuffer.updating) return
      if (this.queue.length > 0) return

      try {
        this.mediaSource.endOfStream()
        this.finalized = true
      } catch (err) {
        // Safe to ignore finalize races
        // console.debug('endOfStream race (ignored):', err)
      }
    }
  }

  /**
   * Player wraps Audio element and MediaSourceBufferController, coordinating playback and cleanup.
   */
  class Player {
    /**
     * @param {{
     *  mimeType: string,
     *  autostart: boolean,
     *  token: { generation: number, aborted: boolean },
     *  onError: (msg: string) => void,
     *  onLoadedData: () => void,
     *  onEnded: () => void,
     *  onPlaybackStart: () => void
     * }} opts
     */
    constructor(opts) {
      this.mimeType = opts.mimeType
      this.autostart = opts.autostart
      this.token = opts.token
      this.onError = opts.onError
      this.onLoadedData = opts.onLoadedData
      this.onEnded = opts.onEnded
      this.onPlaybackStart = opts.onPlaybackStart

      this.mediaSource = null
      this.audio = null
      this.url = null
      this.controller = null

      this.hasStartedPlayback = false
      this.disposed = false

      this._onAudioLoadedData = this._onAudioLoadedData.bind(this)
      this._onAudioEnded = this._onAudioEnded.bind(this)
      this._onAudioError = this._onAudioError.bind(this)
      this._onControllerUpdateEnd = this._onControllerUpdateEnd.bind(this)
    }

    _valid() {
      return this.token && !this.token.aborted && !this.disposed
    }

    initialize() {
      this.mediaSource = new MediaSource()
      this.audio = new Audio()
      this.url = URL.createObjectURL(this.mediaSource)
      this.audio.src = this.url

      // Audio events
      this.audio.onloadeddata = this._onAudioLoadedData
      this.audio.onended = this._onAudioEnded
      this.audio.onerror = this._onAudioError

      // Buffer controller
      this.controller = new MediaSourceBufferController(
        this.mediaSource,
        this.mimeType,
        this.token,
        (msg) => {
          if (this._valid()) this.onError(msg)
        },
        this._onControllerUpdateEnd
      )
    }

    _onAudioLoadedData() {
      if (!this._valid()) return
      this.onLoadedData()
    }

    _onAudioEnded() {
      if (!this._valid()) return
      this.onEnded()
    }

    _onAudioError() {
      if (!this._valid()) return
      this.onError('Audio playback failed')
    }

    async _tryStartPlayback() {
      if (!this._valid()) return
      if (this.hasStartedPlayback) return
      if (!this.autostart) return

      this.hasStartedPlayback = true
      try {
        await this.audio.play()
        if (this._valid()) this.onPlaybackStart()
      } catch (err) {
        if (this._valid()) this.onError('Audio play failed')
      }
    }

    _onControllerUpdateEnd() {
      if (!this._valid()) return
      // Start playback on first appended data
      this._tryStartPlayback()
    }

    /**
     * Append chunk to buffer
     * @param {ArrayBuffer} chunk
     */
    async write(chunk) {
      if (!this._valid()) return
      await this.controller.write(chunk)
    }

    /**
     * Signal end-of-stream
     */
    async end() {
      if (!this._valid()) return
      await this.controller.end()
    }

    /**
     * Dispose and cleanup resources
     */
    dispose() {
      if (this.disposed) return
      this.disposed = true
      if (this.controller) {
        this.controller.abort()
      }
      if (this.audio) {
        try {
          this.audio.pause()
        } catch {}
        try {
          // Keep a brief delay before revoking URL to avoid "Empty src" issues on some browsers
          const urlToRevoke = this.url
          this.audio.removeAttribute('src')
          this.audio.load()
          if (urlToRevoke) {
            setTimeout(() => {
              try {
                URL.revokeObjectURL(urlToRevoke)
              } catch {}
            }, 150)
          }
        } catch {}
      }
      // End the media source if still open
      if (this.mediaSource && this.mediaSource.readyState === 'open') {
        try {
          this.mediaSource.endOfStream()
        } catch {}
      }
      // Invalidate token to stop any further actions
      if (this.token) {
        this.token.aborted = true
      }
    }
  }

  /**
   * Reset UI state to idle
   */
  const resetUiState = () => {
    Object.assign(state, {
      playingAudioId: null,
      isPlaying: false,
      isLoading: false,
      isInitialized: false,
      error: null,
      activeAudio: null,
    })
  }

  /**
   * Stop any active audio (progressive or sample) and cleanup
   */
  const stop = async () => {
    // Progressive
    if (current.player) {
      try {
        current.player.dispose()
      } catch {}
    }

    // Sample
    if (current.sampleAudio) {
      try {
        current.sampleAudio.pause()
        current.sampleAudio.removeAttribute('src')
        current.sampleAudio.load()
      } catch {}
    }
    if (current.sampleUrl) {
      const urlToRevoke = current.sampleUrl
      setTimeout(() => {
        try {
          URL.revokeObjectURL(urlToRevoke)
        } catch {}
      }, 150)
    }

    // Invalidate current token
    if (token) token.aborted = true

    // Clear runtime refs
    current = {
      type: null,
      player: null,
      handle: null,
      sampleAudio: null,
      sampleUrl: null,
    }

    resetUiState()
  }

  /**
   * Create a progressive stream handle for chunked audio (WebSocket or any chunk source).
   * Returns an object with write(arrayBuffer), end(), abort().
   * @param {{ id: string, mimeType?: string, autostart?: boolean }} opts
   * @returns {Promise<{ id: string, write: (chunk: ArrayBuffer|Blob) => Promise<void>, end: () => Promise<void>, abort: () => void }>}
   */
  const createProgressiveStream = async (opts) => {
    const { id, mimeType = 'audio/mp4; codecs="mp4a.40.2"', autostart = true } = opts || {}

    // Only one active stream at a time
    await stop()

    if (!supportsMediaSource()) {
      setError('Progressive audio playback not supported in this browser')
      throw new Error('MediaSource not supported')
    }

    token = newToken()
    state.isLoading = true
    state.error = null
    state.playingAudioId = id

    const player = new Player({
      mimeType,
      autostart,
      token,
      onError: (msg) => {
        setError(msg)
        // Ensure cleanup of player
        try {
          player.dispose()
        } catch {}
      },
      onLoadedData: () => {
        state.isLoading = false
        state.isPlaying = true
      },
      onEnded: () => {
        // End of playback; cleanup everything and reset UI
        stop()
      },
      onPlaybackStart: () => {
        // no-op, but could be used to flip UI on first audio
      },
    })

    player.initialize()

    const handle = {
      id,
      write: async (chunk) => {
        if (chunk instanceof Blob) {
          chunk = await chunk.arrayBuffer()
        }
        await player.write(chunk)
      },
      end: async () => {
        await player.end()
      },
      abort: () => {
        player.dispose()
      },
    }

    current.type = 'progressive'
    current.player = player
    current.handle = handle

    // Back-compat legacy exposure (activeAudio) for existing callers
    state.activeAudio = {
      audio: player.audio,
      mediaSource: player.mediaSource,
      url: player.url,
      player: {
        invalidate: () => handle.abort(),
      },
      sessionId: token.generation, // indicative only
      appendChunk: (chunk) => handle.write(chunk),
      endStream: () => handle.end(),
    }

    state.isInitialized = true
    return handle
  }

  /**
   * Play audio from REST streaming response (voice samples) in buffered mode.
   * Keeps simple blob approach but shares unified cleanup and UI state.
   * @param {Response} response
   * @param {string} audioId
   */
  const playSampleResponse = async (response, audioId = 'sample') => {
    try {
      await stop()

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)

      token = newToken()
      state.isLoading = true
      state.error = null
      state.playingAudioId = audioId

      audio.onloadeddata = () => {
        if (!token || token.aborted) return
        state.isLoading = false
        state.isPlaying = true
      }

      audio.onended = () => {
        // Cleanup and reset
        stop()
      }

      audio.onerror = () => {
        try {
          URL.revokeObjectURL(url)
        } catch {}
        setError('Audio playback failed')
        stop()
      }

      current.type = 'sample'
      current.sampleAudio = audio
      current.sampleUrl = url
      state.isInitialized = true

      await audio.play()
    } catch (err) {
      console.error('Failed to play sample audio:', err)
      setError('Failed to play streaming audio')
      await stop()
    }
  }

  /**
   * Backward-compat shim: progressive audio from WebSocket chunks.
   * Initializes progressive stream and exposes legacy activeAudio.appendChunk/endStream.
   * @param {string} audioId
   */
  const playWebSocketAudio = async (audioId = 'websocket') => {
    try {
      // Always set up a fresh progressive stream for the given id
      await createProgressiveStream({ id: audioId })
    } catch (err) {
      console.error('Failed to initialize progressive audio:', err)
      setError('Progressive audio setup failed')
      await stop()
    }
  }

  /**
   * Backward-compat shim name: preserved alias for buffered sample playback
   * @param {Response} response
   * @param {string} audioId
   */
  const playStreamingResponse = async (response, audioId = 'stream') => {
    return playSampleResponse(response, audioId)
  }

  /**
   * Backward-compat name for stopping audio
   */
  const stopAudio = async () => {
    await stop()
  }

  // Cleanup on component unmount
  onUnmounted(async () => {
    await stop()
  })

  return {
    // State - using computed refs to maintain reactivity
    playingAudioId: computed(() => state.playingAudioId),
    isLoading: computed(() => state.isLoading),
    isPlaying: computed(() => state.isPlaying),
    error: computed(() => state.error),
    activeAudio: computed(() => state.activeAudio),
    isInitialized: computed(() => state.isInitialized),

    // New API
    createProgressiveStream, // For conversation/challenge audio (WebSocket chunks)
    playSampleResponse, // For voice samples (REST response blob)
    stop, // Unified stop

    // Back-compat API (kept to avoid breaking current consumers)
    playWebSocketAudio,
    playStreamingResponse,
    stopAudio,

    // Utility
    supportsMediaSource,
  }
}
