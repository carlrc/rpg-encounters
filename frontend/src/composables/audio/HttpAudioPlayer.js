/**
 * HttpAudioPlayer
 * Buffered playback of small/short audio assets (e.g., voice preview samples).
 *
 * Public API:
 * - constructor({ onError, onLoadedData, onEnded, onPlaybackStart })
 * - playResponse(response: Response): Promise<void>
 * - playBlob(blob: Blob): Promise<void>
 * - stop(): Promise<void>  // idempotent
 */
export default class HttpAudioPlayer {
  /**
   * @param {{
   *   onError: (msg: string) => void,
   *   onLoadedData: () => void,
   *   onEnded: () => void,
   *   onPlaybackStart: () => void
   * }} opts
   */
  constructor(opts = {}) {
    this.onError = opts.onError
    this.onLoadedData = opts.onLoadedData
    this.onEnded = opts.onEnded
    this.onPlaybackStart = opts.onPlaybackStart

    this.audio = null
    this.url = null
  }

  async playResponse(response) {
    const blob = await response.blob()
    return this.playBlob(blob)
  }

  async playBlob(blob) {
    // Always stop any existing playback first
    await this.stop()

    try {
      const url = URL.createObjectURL(blob)
      this.url = url

      const audio = new Audio(url)
      this.audio = audio

      // Wire events
      audio.onloadeddata = () => {
        this.onLoadedData()
      }
      audio.onended = () => {
        this.onEnded()
        // Cleanup after playback ends
        this.stop()
      }
      audio.onerror = () => {
        this.onError('Audio playback failed')
        this.stop()
      }

      await audio.play()
      this.onPlaybackStart()
    } catch (err) {
      this.onError('Audio play failed')
      await this.stop()
    }
  }

  async stop() {
    // Idempotent cleanup
    if (this.audio) {
      try {
        this.audio.pause()
      } catch {}
      try {
        this.audio.onloadeddata = null
        this.audio.onended = null
        this.audio.onerror = null
        this.audio.removeAttribute('src')
        this.audio.load()
      } catch {}
    }

    if (this.url) {
      const toRevoke = this.url
      this.url = null
      setTimeout(() => {
        try {
          URL.revokeObjectURL(toRevoke)
        } catch {}
      }, 150)
    }

    this.audio = null
  }
}
