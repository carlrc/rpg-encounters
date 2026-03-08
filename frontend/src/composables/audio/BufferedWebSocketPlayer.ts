import { serializeError } from 'serialize-error'
import type { StreamAudioPlayer } from './StreamAudioPlayer'

export default class BufferedWebSocketPlayer implements StreamAudioPlayer {
  constructor({ mimeType = 'audio/mp4; codecs=mp4a.40.2', audioEl = null } = {}) {
    this.mimeType = mimeType
    this.mode = 'buffered'
    this.audio = audioEl || null
    this.chunks = []
    this.objectUrl = null
    this.stopped = false
    this.unlocked = false
    this._unlockPromise = null
    this._endPromise = null
    this._endResolve = null
  }

  async append(chunk) {
    if (this.stopped) return
    const ab = await this._toArrayBuffer(chunk)
    this.chunks.push(ab)
  }

  async end() {
    if (this.stopped) return
    if (!this._endPromise) {
      this._endPromise = new Promise((resolve) => {
        this._endResolve = resolve
      })
    }
    await this._playBuffered()
    return this._endPromise
  }

  async stop() {
    if (this.stopped) return
    this.stopped = true
    await this._cleanup()
  }

  prepare({ fromUserGesture = false } = {}) {
    if (!fromUserGesture) return
    if (!this.audio) {
      this.audio = new Audio()
    }
    if (this.unlocked || this._unlockPromise) return this._unlockPromise

    const previousMuted = this.audio.muted
    this.audio.muted = true

    this._unlockPromise = (async () => {
      try {
        await this.audio.play()
        this.unlocked = true
      } catch (error) {
        if (error?.name === 'AbortError') return
        console.warn('BufferedWebSocketPlayer audio unlock failed', JSON.stringify(error))
      } finally {
        this.audio.muted = previousMuted
        this._unlockPromise = null
      }
    })()

    return this._unlockPromise
  }

  async _playBuffered() {
    if (this.stopped) return
    if (!this.audio) {
      this.audio = new Audio()
    }

    const blob = new Blob(this.chunks, { type: this.mimeType })
    this.objectUrl = URL.createObjectURL(blob)
    this.audio.src = this.objectUrl
    this.audio.playsInline = true

    try {
      await this.audio.play()
      await new Promise((resolve) => {
        if (!this.audio) return resolve()
        const onEnded = () => resolve()
        const onError = () => resolve()
        this.audio.addEventListener('ended', onEnded, { once: true })
        this.audio.addEventListener('error', onError, { once: true })
      })
    } catch (error) {
      console.error('BufferedWebSocketPlayer play failed', JSON.stringify(serializeError(error)))
    } finally {
      await this._cleanup()
    }
  }

  async _cleanup() {
    if (this.audio) {
      this.audio.pause()
      this.audio.removeAttribute('src')
      this.audio.load()
    }

    if (this.objectUrl) {
      const prev = this.objectUrl
      this.objectUrl = null
      try {
        URL.revokeObjectURL(prev)
      } catch (error) {
        console.error('BufferedWebSocketPlayer revokeObjectURL failed', JSON.stringify(error))
      }
    }

    this.chunks = []
    this.audio = null
    this.unlocked = false

    if (this._endResolve) {
      this._endResolve()
      this._endResolve = null
      this._endPromise = null
    }
  }

  async _toArrayBuffer(chunk) {
    if (chunk instanceof ArrayBuffer) return chunk
    if (chunk instanceof Blob) return chunk.arrayBuffer()
    if (ArrayBuffer.isView(chunk)) return chunk.buffer
    throw new Error('Unsupported chunk type for audio append')
  }
}
