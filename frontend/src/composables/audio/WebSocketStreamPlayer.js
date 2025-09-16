/**
 * WebSocketStreamPlayer
 * Progressive playback of MPEG-4 AAC chunks over MediaSource with explicit control.
 *
 * Public API:
 * - constructor({ mimeType = 'audio/mp4; codecs=mp4a.40.2', onError, onLoadedData, onEnded, onPlaybackStart })
 * - initWithFirstChunk(chunk: ArrayBuffer|Blob): Promise<void>
 * - append(chunk: ArrayBuffer|Blob): Promise<void>
 * - play(): Promise<void>
 * - end(): Promise<void>
 * - stop(): Promise<void>
 */
export default class WebSocketStreamPlayer {
  /**
   * @param {{
   *   mimeType?: string,
   *   onError?: (msg: string) => void,
   *   onLoadedData?: () => void,
   *   onEnded?: () => void,
   *   onPlaybackStart?: () => void
   * }} opts
   */
  constructor(opts = {}) {
    this.mimeType = opts.mimeType || 'audio/mp4; codecs=mp4a.40.2'
    this.onError = opts.onError
    this.onLoadedData = opts.onLoadedData
    this.onEnded = opts.onEnded
    this.onPlaybackStart = opts.onPlaybackStart

    // Core objects
    this.audio = null
    this.mediaSource = null
    this.sourceBuffer = null
    this.objectUrl = null

    // Internal state
    this.queue = []
    this.initialized = false
    this.firstChunkAppended = false
    this.stopped = false
    this.endedSignal = false
    this.shouldAutoplay = false
    this.playingStarted = false

    // Bound handlers
    this._onSourceOpen = this._onSourceOpen.bind(this)
    this._onSourceError = this._onSourceError.bind(this)
    this._onUpdateEnd = this._onUpdateEnd.bind(this)

    this._onAudioLoadedData = this._onAudioLoadedData.bind(this)
    this._onAudioEnded = this._onAudioEnded.bind(this)
    this._onAudioError = this._onAudioError.bind(this)
  }

  static isSupported(mimeType = 'audio/mp4; codecs=mp4a.40.2') {
    try {
      return !!(window.MediaSource && MediaSource.isTypeSupported(mimeType))
    } catch {
      return false
    }
  }

  _ensureSupported() {
    if (!WebSocketStreamPlayer.isSupported(this.mimeType)) {
      const msg = 'Progressive audio playback not supported in this browser'
      this.onError(msg)
      throw new Error(msg)
    }
  }

  _attachAudio() {
    if (this.audio) return
    this.audio = new Audio()

    // Audio events
    this.audio.onloadeddata = this._onAudioLoadedData
    this.audio.onended = this._onAudioEnded
    this.audio.onerror = this._onAudioError
  }

  _createMediaSource() {
    if (this.mediaSource) return
    this.mediaSource = new MediaSource()
    this.mediaSource.addEventListener('sourceopen', this._onSourceOpen)
    this.mediaSource.addEventListener('error', this._onSourceError)

    // Link the media source to audio
    this.objectUrl = URL.createObjectURL(this.mediaSource)
    this.audio.src = this.objectUrl
  }

  async initWithFirstChunk(chunk) {
    this._ensureSupported()
    if (this.stopped) return
    if (this.initialized) return

    const first = await this._toArrayBuffer(chunk)

    this._attachAudio()
    this._createMediaSource()

    // Enqueue first chunk; it will be appended when sourceopen fires
    this.queue.push(first)
    this.initialized = true
  }

  async append(chunk) {
    if (this.stopped) return
    if (!this.initialized) {
      // If not initialized, treat this as first chunk
      return this.initWithFirstChunk(chunk)
    }
    const ab = await this._toArrayBuffer(chunk)
    this.queue.push(ab)
    this._maybeAppend()
  }

  async play() {
    if (this.stopped) return
    // Explicit start requested; if first chunk already appended, try play now; else defer
    if (this.firstChunkAppended && !this.playingStarted) {
      await this._tryPlay()
    } else {
      this.shouldAutoplay = true
    }
  }

  async end() {
    if (this.stopped) return
    this.endedSignal = true
    this._maybeFinalize()
  }

  async stop() {
    if (this.stopped) return
    this.stopped = true

    // Abort any pending appends
    try {
      if (this.sourceBuffer && this.sourceBuffer.updating) {
        try {
          this.sourceBuffer.abort()
        } catch {}
      }
    } catch {}

    // Cleanup media source
    try {
      if (this.mediaSource && this.mediaSource.readyState === 'open') {
        try {
          this.mediaSource.endOfStream()
        } catch {}
      }
    } catch {}

    // Cleanup audio
    if (this.audio) {
      try {
        this.audio.pause()
      } catch {}
      try {
        this.audio.removeAttribute('src')
        this.audio.load()
      } catch {}
    }

    // Revoke URL after a brief delay to avoid empty-src issues
    if (this.objectUrl) {
      const url = this.objectUrl
      setTimeout(() => {
        try {
          URL.revokeObjectURL(url)
        } catch {}
      }, 150)
    }

    // Detach listeners
    this._detachAllListeners()

    // Reset references
    this.queue = []
    this.objectUrl = null
    this.sourceBuffer = null
    this.mediaSource = null
    // keep audio instance for reuse if needed, but it's inert now
  }

  async _tryPlay() {
    if (this.playingStarted || this.stopped || !this.audio) return
    try {
      await this.audio.play()
      this.playingStarted = true
      this.onPlaybackStart()
    } catch (err) {
      this.onError('Audio play failed')
    }
  }

  _onSourceOpen() {
    if (this.stopped) return
    // Create SourceBuffer
    try {
      this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
      this.sourceBuffer.addEventListener('updateend', this._onUpdateEnd)
      this.sourceBuffer.addEventListener('error', this._onSourceError)
    } catch (err) {
      this.onError('Failed to create audio buffer')
      return
    }
    // Start appending any queued chunks
    this._maybeAppend()
  }

  _onSourceError() {
    if (this.stopped) return
    this.onError('Media source error')
  }

  _onUpdateEnd() {
    if (this.stopped) return
    // First appended chunk detected
    if (!this.firstChunkAppended) {
      this.firstChunkAppended = true
      // If play() was called earlier, start now
      if (this.shouldAutoplay && !this.playingStarted) {
        this._tryPlay()
      }
    }

    // Continue draining queue or finalize if ended
    if (!this._maybeAppend()) {
      this._maybeFinalize()
    }
  }

  _onAudioLoadedData() {
    if (this.stopped) return
    this.onLoadedData()
  }

  _onAudioEnded() {
    if (this.stopped) return
    this.onEnded()
  }

  _onAudioError() {
    if (this.stopped) return
    this.onError('Audio playback failed')
  }

  _maybeAppend() {
    if (this.stopped) return false
    if (!this.sourceBuffer) return false
    if (this.sourceBuffer.updating) return false
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
    if (this.stopped) return
    if (!this.endedSignal) return
    if (!this.mediaSource || this.mediaSource.readyState !== 'open') return
    if (this.sourceBuffer && this.sourceBuffer.updating) return
    if (this.queue.length > 0) return
    try {
      this.mediaSource.endOfStream()
    } catch {
      // Ignore finalize races
    }
  }

  _detachAllListeners() {
    if (this.sourceBuffer) {
      try {
        this.sourceBuffer.removeEventListener('updateend', this._onUpdateEnd)
        this.sourceBuffer.removeEventListener('error', this._onSourceError)
      } catch {}
    }
    if (this.mediaSource) {
      try {
        this.mediaSource.removeEventListener('sourceopen', this._onSourceOpen)
        this.mediaSource.removeEventListener('error', this._onSourceError)
      } catch {}
    }
    if (this.audio) {
      try {
        this.audio.onloadeddata = null
        this.audio.onended = null
        this.audio.onerror = null
      } catch {}
    }
  }

  async _toArrayBuffer(chunk) {
    if (chunk instanceof ArrayBuffer) return chunk
    if (chunk instanceof Blob) return chunk.arrayBuffer()
    // Typed arrays
    if (ArrayBuffer.isView(chunk)) return chunk.buffer
    throw new Error('Unsupported chunk type for audio append')
  }
}
