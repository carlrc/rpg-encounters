/**
 * HttpAudioPlayer
 * Buffered playback of small/short audio assets (e.g., voice preview samples).
 *
 * Public API:
 * - constructor()
 * - playResponse(response: Response): Promise<void>
 * - playBlob(blob: Blob): Promise<void>
 * - stop(): Promise<void>  // idempotent
 */
export default class HttpAudioPlayer {
  constructor() {
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

      // Minimal event wiring for internal cleanup only
      audio.onended = () => {
        // Cleanup after playback ends
        this.stop()
      }
      audio.onerror = (error) => {
        console.error('HttpAudioPlayer playback failed', error)
        this.stop()
      }

      await audio.play()
    } catch (error) {
      console.error('HttpAudioPlayer Audio play failed', error)
      await this.stop()
    }
  }

  async stop() {
    try {
      if (this.audio) {
        this.audio.pause()
        this.audio.onloadeddata = null
        this.audio.onended = null
        this.audio.onerror = null
        this.audio.removeAttribute('src')
        this.audio.load()
      }
      if (this.url) {
        const toRevoke = this.url
        this.url = null
        setTimeout(() => {
          try {
            URL.revokeObjectURL(toRevoke)
          } catch (error) {
            console.error('HttpAudioPlayer revokeObjectURL failed', error)
          }
        }, 150)
      }
    } catch (e) {
      console.error('HttpAudioPlayer stop action failed', e)
    } finally {
      this.audio = null
    }
  }
}
