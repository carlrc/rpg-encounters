import { useNotification } from '../useNotification.js'
import { serializeError } from 'serialize-error'

/**
 * WebSocketStreamPlayer
 * Progressive playback of MPEG-4 AAC chunks over MediaSource with auto-play and minimal API.
 *
 * Public API:
 * - constructor(mimeType?: string)
 * - append(chunk: ArrayBuffer|Blob): Promise<void>
 * - end(): Promise<void>
 * - stop(): Promise<void>
 */

export default class WebSocketStreamPlayer {
  constructor({ mimeType = 'audio/mp4; codecs=mp4a.40.2', audioEl = null } = {}) {
    this.mimeType = mimeType

    // Core objects
    this.audio = audioEl || null
    this.mediaSource = null
    this.sourceBuffer = null
    this.objectUrl = null

    // Internal state
    this.queue = []
    this.initialized = false
    this.firstChunkAppended = false
    this.stopped = false
    this.endedSignal = false
    this.playingStarted = false
    this.unlocked = false
    // Tracks an in-flight unlock attempt so we don't fire `play()` twice for a single gesture.
    this._unlockPromise = null

    // Bound handlers
    this._onSourceOpen = this._onSourceOpen.bind(this)
    this._onSourceError = this._onSourceError.bind(this)
    this._onUpdateEnd = this._onUpdateEnd.bind(this)
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
      const { showError } = useNotification()
      showError(
        'Streaming audio playback not supported in this browser. Try updating or switching to Chrome.'
      )
    }
  }

  _attachAudio() {
    if (!this.audio) {
      this.audio = new Audio()
    }

    this.audio.preload = 'auto'
    this.audio.playsInline = true
    this.audio.onerror = (error) => {
      if (this.stopped) return
      console.error('WebSocketStreamPlayer audio error', JSON.stringify(serializeError(error)))
    }
  }

  _createMediaSource() {
    if (this.mediaSource) return
    this.mediaSource = new MediaSource()
    this.mediaSource.addEventListener('sourceopen', this._onSourceOpen)
    this.mediaSource.addEventListener('error', this._onSourceError)

    // Link the media source to audio
    this.objectUrl = URL.createObjectURL(this.mediaSource)
    this.audio.src = this.objectUrl
    this.audio.playsInline = true
  }

  async append(chunk) {
    if (this.stopped) return
    await this._ensureReady()
    const ab = await this._toArrayBuffer(chunk)
    this.queue.push(ab)
    this._drainQueue()
  }

  async end() {
    if (this.stopped) return
    this.endedSignal = true
    this._maybeFinalize()
  }

  async stop() {
    if (this.stopped) return
    this.stopped = true

    try {
      // Detach listeners first to avoid further handler invocations
      this._detachAllListeners()

      // Abort any pending appends
      if (this.sourceBuffer && this.sourceBuffer.updating) {
        try {
          this.sourceBuffer.abort()
        } catch (error) {
          console.error(
            'WebSocketStreamPlayer sourceBuffer.abort failed',
            JSON.stringify(serializeError(error))
          )
        }
      }

      // Cleanup media source
      if (this.mediaSource && this.mediaSource.readyState === 'open') {
        this.mediaSource.endOfStream()
      }

      // Cleanup audio
      if (this.audio) {
        this.audio.pause()
        this.audio.removeAttribute('src')
        this.audio.load()
      }

      // Revoke URL after a brief delay to avoid empty-src issues
      if (this.objectUrl) {
        const url = this.objectUrl
        this.objectUrl = null
        setTimeout(() => {
          URL.revokeObjectURL(url)
        }, 150)
      }
    } catch (error) {
      console.error(
        'WebSocketStreamPlayer stop action failed',
        JSON.stringify(serializeError(error))
      )
    } finally {
      this.queue = []
      this.sourceBuffer = null
      this.mediaSource = null
      // keep audio instance; it's inert now
    }
  }

  async _ensureReady() {
    if (this.initialized) return
    this._ensureSupported()
    this._attachAudio()
    this._createMediaSource()
    this.initialized = true
  }

  prepare({ fromUserGesture = false } = {}) {
    // Unlock the audio element during a user gesture so iOS/iPadOS will allow later autoplay of streamed chunks.
    this._ensureReady()
    if (!fromUserGesture) return
    if (!this.audio || this.unlocked) return
    if (this._unlockPromise) return this._unlockPromise

    const previousMuted = this.audio.muted
    this.audio.muted = true

    this._unlockPromise = (async () => {
      try {
        await this.audio.play()
        this.unlocked = true
        this.playingStarted = true
      } catch (error) {
        console.warn(
          'WebSocketStreamPlayer audio unlock failed',
          JSON.stringify(serializeError(error))
        )
      } finally {
        this.audio.muted = previousMuted
        this._unlockPromise = null
      }
    })()

    return this._unlockPromise
  }

  async _tryPlay() {
    if (this.playingStarted || this.stopped || !this.audio) return
    try {
      await this.audio.play()
      this.playingStarted = true
    } catch (error) {
      console.error(
        'WebSocketStreamPlayer play action failed',
        JSON.stringify(serializeError(error))
      )
    }
  }

  _onSourceOpen() {
    if (this.stopped) return
    // Create SourceBuffer
    try {
      this.sourceBuffer = this.mediaSource.addSourceBuffer(this.mimeType)
      this.sourceBuffer.addEventListener('updateend', this._onUpdateEnd)
      this.sourceBuffer.addEventListener('error', this._onSourceError)
    } catch (error) {
      console.error(
        'WebSocketStreamPlayer failed to create audio buffer',
        JSON.stringify(serializeError(error))
      )
    }
    // Start appending any queued chunks
    this._drainQueue()
  }

  _onSourceError(error) {
    if (this.stopped) return
    console.error('WebSocketStreamPlayer media source error', JSON.stringify(serializeError(error)))
  }

  _onUpdateEnd() {
    if (this.stopped) return
    // First appended chunk detected
    if (!this.firstChunkAppended) {
      this.firstChunkAppended = true
      // Always auto-play on first chunk
      if (!this.playingStarted) {
        this._tryPlay()
      }
    }

    // Continue draining queue and maybe finalize
    this._drainQueue()
    this._maybeFinalize()
  }

  _drainQueue() {
    if (this.stopped) return
    if (!this.sourceBuffer) return
    if (this.sourceBuffer.updating) return
    if (this.queue.length === 0) return

    while (this.queue.length > 0 && !this.sourceBuffer.updating) {
      const next = this.queue.shift()
      try {
        this.sourceBuffer.appendBuffer(next)
      } catch (error) {
        console.error(
          'WebSocketStreamPlayer failed to process audio chunk',
          JSON.stringify(serializeError(error))
        )
        throw error
      }
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

      // Soft-reset so this instance can be reused on the next loop
      try {
        this._detachAllListeners()
      } catch (error) {
        console.error(
          'WebSocketStreamPlayer failed detaching listeners during finalize',
          JSON.stringify(serializeError(error))
        )
      }

      if (this.objectUrl) {
        const prev = this.objectUrl
        this.objectUrl = null
        try {
          URL.revokeObjectURL(prev)
        } catch (error) {
          console.error(
            'WebSocketStreamPlayer revokeObjectURL failed',
            JSON.stringify(serializeError(error))
          )
        }
      }

      // Reset internal state; keep the audio element and unlock state
      this.sourceBuffer = null
      this.mediaSource = null
      this.initialized = false
      this.firstChunkAppended = false
      this.playingStarted = false
      this.endedSignal = false
      this.stopped = false
      // Intentionally NOT resetting certain fields:
      // - this.unlocked: preserve prior user-gesture unlock so iOS/iPadOS autoplay
      //   continues to work across loops without requiring another gesture.
      // - this._unlockPromise: only non-null transiently during prepare(); it
      //   clears in prepare()'s finally, so no action needed here.
      // - this.queue: _maybeFinalize() runs only when the queue is already empty
      //   (guard above), so explicit clearing is unnecessary.
    } catch (error) {
      console.error(
        'WebSocketStreamPlayer failed to finalize stream',
        JSON.stringify(serializeError(error))
      )
    }
  }

  _detachAllListeners() {
    try {
      if (this.sourceBuffer) {
        this.sourceBuffer.removeEventListener('updateend', this._onUpdateEnd)
        this.sourceBuffer.removeEventListener('error', this._onSourceError)
      }
      if (this.mediaSource) {
        this.mediaSource.removeEventListener('sourceopen', this._onSourceOpen)
        this.mediaSource.removeEventListener('error', this._onSourceError)
      }

      if (this.audio) {
        this.audio.onerror = null
      }
    } catch (error) {
      console.error(
        'WebSocketStreamPlayer failed detaching listeners',
        JSON.stringify(serializeError(error))
      )
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
