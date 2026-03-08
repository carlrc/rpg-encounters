export class UnsupportedStreamingError extends Error {
  constructor(message = 'Streaming audio playback not supported') {
    super(message)
    this.name = 'UnsupportedStreamingError'
  }
}
