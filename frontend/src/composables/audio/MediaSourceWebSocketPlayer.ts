import { UnsupportedStreamingError } from './streamErrors'
import BaseWebSocketMediaPlayer from './BaseWebSocketMediaPlayer'

export default class MediaSourceWebSocketPlayer extends BaseWebSocketMediaPlayer {
  constructor({ mimeType = 'audio/mp4; codecs=mp4a.40.2', audioEl = null } = {}) {
    super({
      mimeType,
      audioEl,
      mode: 'mediaSource',
      logPrefix: 'MediaSourceWebSocketPlayer',
    })
  }

  static isSupported(mimeType = 'audio/mp4; codecs=mp4a.40.2') {
    try {
      return !!(window.MediaSource && MediaSource.isTypeSupported(mimeType))
    } catch {
      return false
    }
  }

  _ensureSupported() {
    if (!MediaSourceWebSocketPlayer.isSupported(this.mimeType)) {
      throw new UnsupportedStreamingError()
    }
  }

  createMediaSource() {
    // Standard MSE path for Chromium/desktop browsers.
    return new MediaSource()
  }

  attachMediaSourceToAudio() {
    // MSE requires an object URL; srcObject is not supported here.
    this.objectUrl = URL.createObjectURL(this.mediaSource)
    this.audio.src = this.objectUrl
    this.audio.playsInline = true
  }

  canAppendNow() {
    // No additional gating for standard MSE.
    return true
  }
}
