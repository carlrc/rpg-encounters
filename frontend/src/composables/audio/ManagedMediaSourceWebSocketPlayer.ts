import { UnsupportedStreamingError } from './streamErrors'
import BaseWebSocketMediaPlayer from './BaseWebSocketMediaPlayer'

export default class ManagedMediaSourceWebSocketPlayer extends BaseWebSocketMediaPlayer {
  constructor({ mimeType = 'audio/mp4; codecs=mp4a.40.2', audioEl = null } = {}) {
    super({
      mimeType,
      audioEl,
      mode: 'managedMediaSource',
      logPrefix: 'ManagedMediaSourceWebSocketPlayer',
    })

    // Safari gate: only append when startstreaming has fired.
    this.streamingAllowed = false

    this._onStartStreaming = this._onStartStreaming.bind(this)
    this._onEndStreaming = this._onEndStreaming.bind(this)
    this._onSourceClose = this._onSourceClose.bind(this)
  }

  static isSupported(mimeType = 'audio/mp4; codecs=mp4a.40.2') {
    try {
      const ManagedMediaSourceCtor = window.ManagedMediaSource
      if (!ManagedMediaSourceCtor) return false
      if (typeof ManagedMediaSourceCtor.isTypeSupported !== 'function') return false
      return ManagedMediaSourceCtor.isTypeSupported(mimeType)
    } catch {
      return false
    }
  }

  _ensureSupported() {
    if (!ManagedMediaSourceWebSocketPlayer.isSupported(this.mimeType)) {
      throw new UnsupportedStreamingError()
    }
  }

  configureAudioElement() {
    // Required for MMS playback on iOS (prevents AirPlay-only routing).
    this.audio.disableRemotePlayback = true
  }

  createMediaSource() {
    // MMS constructor enables Safari/iOS managed streaming.
    const ManagedMediaSourceCtor = window.ManagedMediaSource
    return new ManagedMediaSourceCtor()
  }

  attachMediaSourceToAudio() {
    // MMS uses srcObject instead of an object URL.
    this.audio.srcObject = this.mediaSource
    this.audio.load()
  }

  canAppendNow() {
    // Safari signals when it wants data (power-friendly streaming).
    if (!this.streamingAllowed) return false
    if (this.mediaSource?.streaming === false) return false
    return true
  }

  registerExtraListeners() {
    // MMS emits streaming hints that gate appends on iOS.
    this._bindStreamingListeners()
  }

  removeExtraListeners() {
    this._unbindStreamingListeners()
  }

  _bindStreamingListeners() {
    if (!this.mediaSource) return
    this.mediaSource.addEventListener('startstreaming', this._onStartStreaming)
    this.mediaSource.addEventListener('endstreaming', this._onEndStreaming)
    this.mediaSource.addEventListener('sourceclose', this._onSourceClose)
  }

  _unbindStreamingListeners() {
    if (!this.mediaSource) return
    this.mediaSource.removeEventListener('startstreaming', this._onStartStreaming)
    this.mediaSource.removeEventListener('endstreaming', this._onEndStreaming)
    this.mediaSource.removeEventListener('sourceclose', this._onSourceClose)
  }

  _onStartStreaming() {
    // Safari signals when data fetch/appends are allowed.
    this.streamingAllowed = true
    this._drainQueue()
  }

  _onEndStreaming() {
    // Safari pauses streaming to conserve power.
    this.streamingAllowed = false
  }

  _onSourceClose() {
    if (this.stopped) return
    // iOS can reclaim buffers in the background; teardown defensively.
    void this._teardown({ force: true })
  }
}
