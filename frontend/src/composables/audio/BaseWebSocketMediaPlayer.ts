import { serializeError } from 'serialize-error'
import type { StreamAudioPlayer } from './StreamAudioPlayer'

const END_FINALIZE_DELAY_MS = 500

export default class BaseWebSocketMediaPlayer implements StreamAudioPlayer {
  // Create a base streaming player with shared state and handlers.
  constructor({
    mimeType = 'audio/mp4; codecs=mp4a.40.2',
    audioEl = null,
    mode = 'mediaSource',
    logPrefix = 'WebSocketMediaPlayer',
  } = {}) {
    this.mimeType = mimeType
    this.mode = mode
    this.logPrefix = logPrefix

    // Core objects
    this.audio = audioEl || null
    this.mediaSource = null
    this.sourceBuffer = null
    this.objectUrl = null

    // Internal state
    this.queue = []
    // Hard-stop state so we ignore late chunks and prevent double-teardown.
    this.stopped = false
    // Signals that no more chunks are expected; used to trigger end-of-stream.
    this.endedSignal = false
    // Prevents repeated play() calls when multiple chunks append.
    this.playingStarted = false
    // Tracks autoplay unlock state (important for iOS/WebKit).
    this.unlocked = false
    // Holds the deferred audio-ended handler so we can remove it on teardown.
    this._onAudioEnded = null
    // Tracks in-flight unlock request so we don't double-play during a gesture.
    this._unlockPromise = null
    // Resolves only after playback tail ends and teardown completes.
    this._endPromise = null
    this._endResolve = null
    // Prevents re-entrant teardown during errors or rapid state changes.
    this._tearingDown = false
    // Marks that end() was requested so teardown waits for audio.ended.
    this._endRequested = false

    // Bound handlers
    this._onSourceOpen = this._onSourceOpen.bind(this)
    this._onSourceError = this._onSourceError.bind(this)
    this._onUpdateEnd = this._onUpdateEnd.bind(this)
  }

  // Subclasses should override to throw UnsupportedStreamingError when needed.
  // Assert browser support before creating any media elements.
  _ensureSupported() {}

  // Subclasses must implement these hooks.
  // Construct the MediaSource/ManagedMediaSource instance.
  createMediaSource() {
    throw new Error('createMediaSource must be implemented by subclass')
  }
  // Attach the media source to the audio element.
  attachMediaSourceToAudio() {
    throw new Error('attachMediaSourceToAudio must be implemented by subclass')
  }

  // Subclasses can override for MMS gating.
  // Gate appends when the platform signals streaming readiness.
  canAppendNow() {
    return true
  }
  // Register subclass-specific MediaSource listeners.
  registerExtraListeners() {}
  // Remove subclass-specific MediaSource listeners.
  removeExtraListeners() {}
  // Apply subclass-specific audio element configuration.
  configureAudioElement() {}

  // Enqueue a chunk and start draining once the pipeline is ready.
  async append(chunk) {
    if (this.stopped) return
    await this._ensureReady()
    const ab = await this._toArrayBuffer(chunk)
    this.queue.push(ab)
    this._drainQueue()
  }

  // Signal end-of-stream and resolve once playback tail finishes.
  async end() {
    if (this.stopped) return
    this._endRequested = true
    this.endedSignal = true
    if (!this._endPromise) {
      this._endPromise = new Promise((resolve) => {
        this._endResolve = resolve
      })
    }
    try {
      await this._awaitDrain()
      // Allow a brief grace period for late chunks before ending the stream.
      await this._sleep(END_FINALIZE_DELAY_MS)
      if (this.mediaSource?.readyState === 'open') {
        this._endStream()
      }
      if (this.audio && !this.audio.ended) {
        await this._waitForAudioEnded()
      }
      await this._teardown()
    } catch (error) {
      console.error(
        `${this.logPrefix} failed to finalize stream`,
        JSON.stringify(serializeError(error))
      )
    }
    return this._endPromise
  }

  // Hard-stop immediately tears down playback and buffers.
  async stop() {
    if (this.stopped) return
    try {
      await this._teardown({ force: true })
    } catch (error) {
      console.error(`${this.logPrefix} stop action failed`, JSON.stringify(serializeError(error)))
    } finally {
      this.queue = []
    }
  }

  // Lazily build the audio + media source pipeline before appends.
  async _ensureReady() {
    if (this.mediaSource) return
    // Avoid allocating elements on unsupported browsers.
    this._ensureSupported()
    this._ensureAudioElement()
    this._ensureMediaSource()
  }

  // Create and configure the audio element for streaming.
  _ensureAudioElement() {
    if (!this.audio) {
      this.audio = new Audio()
    }

    // Audio element defaults tuned for streaming playback.
    this.audio.preload = 'auto'
    this.audio.playsInline = true
    this.configureAudioElement()

    this.audio.onerror = (error) => {
      if (this.stopped) return
      console.error(`${this.logPrefix} audio error`, JSON.stringify(serializeError(error)))
    }
  }

  // Create the media source and bind its lifecycle listeners.
  _ensureMediaSource() {
    if (this.mediaSource) return
    // MediaSource setup must happen before any appends.
    this.mediaSource = this.createMediaSource()

    this.mediaSource.addEventListener('sourceopen', this._onSourceOpen)
    this.mediaSource.addEventListener('error', this._onSourceError)
    this.registerExtraListeners()

    this.attachMediaSourceToAudio()
  }

  // Prepare for autoplay by unlocking during a user gesture.
  prepare({ fromUserGesture = false } = {}) {
    // Unlock audio during a user gesture to satisfy autoplay restrictions.
    this._ensureReady()
    if (!fromUserGesture) return
    return this._unlockAudioElement()
  }

  // Perform a muted play to satisfy autoplay policies.
  _unlockAudioElement() {
    // Only perform the silent play once per gesture/unlock cycle.
    if (!this.audio || this.unlocked) return
    if (this._unlockPromise) return this._unlockPromise

    const previousMuted = this.audio.muted
    this.audio.muted = true

    this._unlockPromise = (async () => {
      try {
        await this.audio.play()
        this.unlocked = true
      } catch (error) {
        if (error?.name === 'AbortError') return
        console.warn(`${this.logPrefix} audio unlock failed`, JSON.stringify(serializeError(error)))
      } finally {
        this.audio.muted = previousMuted
        this._unlockPromise = null
      }
    })()

    return this._unlockPromise
  }

  // Start playback if we're not already playing.
  async _tryPlay() {
    if (this.stopped || !this.audio) return
    if (this._shouldSkipPlay()) return
    try {
      await this.audio.play()
      this.playingStarted = true
    } catch (error) {
      console.error(`${this.logPrefix} play action failed`, JSON.stringify(serializeError(error)))
    }
  }

  // Skip play when already playing and not paused.
  _shouldSkipPlay() {
    if (!this.playingStarted) return false
    return !this.audio.paused
  }

  // Create SourceBuffer only after MediaSource is open.
  _onSourceOpen() {
    if (this.stopped) return
    if (this.sourceBuffer) return
    // SourceBuffer can only be created after sourceopen fires.
    this._createSourceBuffer()
    this._bindSourceBufferListeners()
    this._drainQueue()
  }

  // Initialize the SourceBuffer for audio mimeType.
  _createSourceBuffer() {
    try {
      // Only safe to create SourceBuffer after sourceopen fires.
      this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
    } catch (error) {
      console.error(
        `${this.logPrefix} failed to create audio buffer`,
        JSON.stringify(serializeError(error))
      )
      void this._teardown({ force: true })
    }
  }

  // Bind SourceBuffer events that drive draining and error handling.
  _bindSourceBufferListeners() {
    if (!this.sourceBuffer) return
    this.sourceBuffer.addEventListener('updateend', this._onUpdateEnd)
    this.sourceBuffer.addEventListener('error', this._onSourceError)
  }

  // Log MediaSource/SourceBuffer errors for diagnosis.
  _onSourceError(error) {
    if (this.stopped) return
    console.error(`${this.logPrefix} media source error`, JSON.stringify(serializeError(error)))
  }

  // Continue appending after each successful updateend.
  _onUpdateEnd() {
    if (this.stopped) return
    // updateend is the safe time to append the next chunk.
    this._ensurePlaybackStarted()
    this._drainQueue()
  }

  // Ensure playback starts once we have buffered data.
  _ensurePlaybackStarted() {
    if (this.playingStarted) return
    this._tryPlay()
  }

  // Drain queued chunks while the buffer can accept data.
  _drainQueue() {
    if (this.stopped) return
    if (!this._canAppend()) return
    this._appendQueuedChunks()
  }

  // Guard against appending when buffer or platform is not ready.
  _canAppend() {
    if (!this.sourceBuffer) return false
    if (!this.canAppendNow()) return false
    if (this.sourceBuffer.updating) return false
    // Nothing queued means there's nothing to append yet.
    if (this.queue.length === 0) return false
    return true
  }

  // Append as many queued chunks as the buffer allows.
  _appendQueuedChunks() {
    while (this.queue.length > 0 && this._canAppend()) {
      if (!this._appendNextChunk()) {
        break
      }
    }
  }

  // Append a single chunk to the SourceBuffer.
  _appendNextChunk() {
    const next = this.queue.shift()
    try {
      this.sourceBuffer.appendBuffer(next)
      return true
    } catch (error) {
      console.error(
        `${this.logPrefix} failed to process audio chunk`,
        JSON.stringify(serializeError(error))
      )
      void this._teardown({ force: true })
      return false
    }
  }

  // Wait until the queue is empty and the SourceBuffer is idle.
  async _awaitDrain() {
    if (!this.endedSignal) return
    if (this._isDrained()) return
    if (!this.mediaSource || this.mediaSource.readyState !== 'open') return
    if (!this.sourceBuffer) return
    await new Promise((resolve) => {
      const onUpdateEnd = () => {
        if (!this._isDrained()) return
        this.sourceBuffer.removeEventListener('updateend', onUpdateEnd)
        resolve()
      }
      this.sourceBuffer.addEventListener('updateend', onUpdateEnd)
      // Ensure we resolve if the buffer drained between checks.
      onUpdateEnd()
    })
  }

  // Check if the queue is empty and the SourceBuffer is idle and open.
  _isDrained() {
    if (!this.endedSignal) return false
    if (!this.mediaSource || this.mediaSource.readyState !== 'open') return false
    if (!this.sourceBuffer) return false
    if (this.sourceBuffer.updating) return false
    if (this.queue.length > 0) return false
    return true
  }

  // Signal the MediaSource that no more data will arrive.
  _endStream() {
    this.mediaSource.endOfStream()
  }

  // Central teardown path for graceful end or forced stop.
  async _teardown({ force = false } = {}) {
    if (this._tearingDown) return
    this._tearingDown = true
    this.stopped = true

    // For graceful end(), wait for playback tail unless force-stopping.
    await this._awaitPlaybackTail({ force })

    // Remove event listeners before manipulating buffers to avoid re-entry.
    this._detachListeners()

    // Abort any in-flight append to avoid InvalidStateError during teardown.
    this._shutdownSourceBuffer()

    // Finalize the media timeline if still open.
    this._finalizeMediaSource()

    // Detach audio element and release any object URL memory.
    this._detachAudioElement()

    // Clear internal state and resolve end() waiters.
    this._resetStateAndResolve()
  }

  // Wait for playback tail unless force stopping.
  async _awaitPlaybackTail({ force = false } = {}) {
    if (force) return
    if (!this._endRequested) return
    if (!this.audio || this.audio.ended) return
    await this._waitForAudioEnded()
  }

  // Detach MediaSource/SourceBuffer/audio listeners defensively.
  _detachListeners() {
    try {
      // Remove listeners before buffer operations to avoid re-entry.
      if (this.sourceBuffer) {
        this.sourceBuffer.removeEventListener('updateend', this._onUpdateEnd)
        this.sourceBuffer.removeEventListener('error', this._onSourceError)
      }
      if (this.mediaSource) {
        this.mediaSource.removeEventListener('sourceopen', this._onSourceOpen)
        this.mediaSource.removeEventListener('error', this._onSourceError)
      }
      this.removeExtraListeners()
      if (this.audio) {
        this.audio.onerror = null
      }
    } catch (error) {
      console.error(
        `${this.logPrefix} failed detaching listeners`,
        JSON.stringify(serializeError(error))
      )
    }

    if (this._onAudioEnded && this.audio) {
      this.audio.removeEventListener('ended', this._onAudioEnded)
      this._onAudioEnded = null
    }
  }

  // Abort any in-flight append to safely finalize buffers.
  _shutdownSourceBuffer() {
    if (this.sourceBuffer && this.sourceBuffer.updating) {
      try {
        this.sourceBuffer.abort()
      } catch (error) {
        console.error(
          `${this.logPrefix} sourceBuffer.abort failed`,
          JSON.stringify(serializeError(error))
        )
      }
    }
  }

  // End the MediaSource timeline and remove SourceBuffer.
  _finalizeMediaSource() {
    if (this.mediaSource && this.mediaSource.readyState === 'open') {
      try {
        this.mediaSource.endOfStream()
      } catch (error) {
        console.error(`${this.logPrefix} endOfStream failed`, JSON.stringify(serializeError(error)))
      }
    }

    if (this.sourceBuffer && this.mediaSource?.sourceBuffers?.length) {
      try {
        this.mediaSource.removeSourceBuffer(this.sourceBuffer)
      } catch (error) {
        console.error(
          `${this.logPrefix} removeSourceBuffer failed`,
          JSON.stringify(serializeError(error))
        )
      }
    }
  }

  // Detach audio element sources and release object URLs.
  _detachAudioElement() {
    if (this.objectUrl) {
      const prev = this.objectUrl
      this.objectUrl = null
      try {
        URL.revokeObjectURL(prev)
      } catch (error) {
        console.error(
          `${this.logPrefix} revokeObjectURL failed`,
          JSON.stringify(serializeError(error))
        )
      }
    }

    if (this.audio) {
      // Clearing src forces sourceclose and releases internal buffers.
      this.audio.pause()
      if (this.audio.srcObject) {
        this.audio.srcObject = null
      }
      this.audio.removeAttribute('src')
      this.audio.load()
    }
  }

  // Reset internal state and resolve any pending end() promise.
  _resetStateAndResolve() {
    this.sourceBuffer = null
    this.mediaSource = null
    this.audio = null
    this.queue = []
    this.playingStarted = false
    this.endedSignal = false
    this.unlocked = false
    this._tearingDown = false
    if (this._endResolve) {
      this._endResolve()
      this._endResolve = null
      this._endPromise = null
    }
  }

  // Await audio ended or error to avoid hanging teardown.
  _waitForAudioEnded() {
    if (!this.audio || this.audio.ended) return Promise.resolve()
    // Resolve on ended or error to avoid hanging teardown.
    return new Promise((resolve) => {
      const onEnded = () => resolve()
      const onError = () => resolve()
      this.audio.addEventListener('ended', onEnded, { once: true })
      this.audio.addEventListener('error', onError, { once: true })
    })
  }

  // Convert supported chunk types into an ArrayBuffer.
  async _toArrayBuffer(chunk) {
    // Normalize Blob/ArrayBuffer/TypedArray into ArrayBuffer.
    if (chunk instanceof ArrayBuffer) return chunk
    if (chunk instanceof Blob) return chunk.arrayBuffer()
    if (ArrayBuffer.isView(chunk)) return chunk.buffer
    throw new Error('Unsupported chunk type for audio append')
  }

  // Simple async delay helper used for short grace periods.
  _sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }
}
