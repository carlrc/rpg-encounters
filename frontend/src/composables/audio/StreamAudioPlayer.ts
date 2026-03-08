export interface StreamAudioPlayer {
  mode: 'mediaSource' | 'managedMediaSource' | 'buffered'
  prepare(opts?: { fromUserGesture?: boolean }): Promise<void> | void
  append(chunk: ArrayBuffer | Blob): Promise<void>
  end(): Promise<void>
  stop(): Promise<void>
}
