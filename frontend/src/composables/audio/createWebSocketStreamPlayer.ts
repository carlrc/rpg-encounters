import { UnsupportedStreamingError } from './streamErrors'
import MediaSourceWebSocketPlayer from './MediaSourceWebSocketPlayer'
import ManagedMediaSourceWebSocketPlayer from './ManagedMediaSourceWebSocketPlayer'
import BufferedWebSocketPlayer from './BufferedWebSocketPlayer'

export const canUseManagedMediaSource = (mimeType) => {
  return ManagedMediaSourceWebSocketPlayer.isSupported(mimeType)
}

export const canUseMediaSource = (mimeType) => {
  return MediaSourceWebSocketPlayer.isSupported(mimeType)
}

export const createWebSocketStreamPlayer = ({ audioEl, mimeType }) => {
  if (canUseManagedMediaSource(mimeType)) {
    return new ManagedMediaSourceWebSocketPlayer({ audioEl, mimeType })
  }

  if (canUseMediaSource(mimeType)) {
    return new MediaSourceWebSocketPlayer({ audioEl, mimeType })
  }

  if (window.Audio) {
    return new BufferedWebSocketPlayer({ audioEl, mimeType })
  }

  throw new UnsupportedStreamingError()
}
