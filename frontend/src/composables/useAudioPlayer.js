import { ref, onUnmounted } from 'vue'

export function useAudioPlayer() {
  const activeAudio = ref(null)
  const playingAudioId = ref(null)
  const isLoading = ref(false)
  const isPlaying = ref(false)
  const error = ref(null)

  /**
   * Check if MediaSource Extensions are supported
   */
  const supportsMediaSource = () => {
    return window.MediaSource && MediaSource.isTypeSupported('audio/mp4; codecs="mp4a.40.2"')
  }

  /**
   * Play audio progressively from WebSocket chunks using MediaSource Extensions
   */
  const playWebSocketAudio = (audioId = 'websocket') => {
    console.log('playWebSocketAudio called with audioId:', audioId)
    try {
      stopAudio() // Stop any currently playing audio first

      isLoading.value = true
      error.value = null
      playingAudioId.value = audioId

      // Use MediaSource for progressive playback
      if (supportsMediaSource()) {
        playWebSocketAudioWithMediaSource(audioId)
      } else {
        console.error(
          'MediaSource Extensions not supported - progressive audio playback unavailable'
        )
        error.value = 'Progressive audio playback not supported in this browser'
        isLoading.value = false
      }
    } catch (err) {
      console.error('Progressive audio setup error:', err)
      error.value = 'Progressive audio setup failed'
      cleanup()
    }
  }

  /**
   * MediaSource-based progressive audio player
   */
  const playWebSocketAudioWithMediaSource = (audioId) => {
    let chunksReceived = 0
    let audio = null
    let mediaSource = null
    let sourceBuffer = null
    let hasStartedPlayback = false
    let isSourceOpen = false
    let pendingChunks = []
    let isEnded = false

    const mimeType = 'audio/mp4; codecs="mp4a.40.2"'

    const initializeMediaSource = () => {
      mediaSource = new MediaSource()
      audio = new Audio()
      audio.src = URL.createObjectURL(mediaSource)

      mediaSource.addEventListener('sourceopen', () => {
        console.log('MediaSource opened')
        isSourceOpen = true

        try {
          sourceBuffer = mediaSource.addSourceBuffer(mimeType)

          sourceBuffer.addEventListener('updateend', () => {
            // Process any pending chunks
            if (pendingChunks.length > 0 && !sourceBuffer.updating) {
              const nextChunk = pendingChunks.shift()
              sourceBuffer.appendBuffer(nextChunk)
            }

            // Start playback after first chunk is processed
            if (!hasStartedPlayback && chunksReceived > 0) {
              startPlayback()
            }

            // End the stream if all chunks processed and stream ended
            if (isEnded && pendingChunks.length === 0 && mediaSource.readyState === 'open') {
              console.log('Ending MediaSource - all chunks processed')
              try {
                mediaSource.endOfStream()
              } catch (err) {
                console.log('Error ending MediaSource:', err)
              }
            }
          })

          sourceBuffer.addEventListener('error', (event) => {
            console.error('SourceBuffer error:', event)
            error.value = 'Audio buffer error'
            cleanup()
          })

          // Process first pending chunk if available
          if (pendingChunks.length > 0) {
            const firstChunk = pendingChunks.shift()
            sourceBuffer.appendBuffer(firstChunk)
          }
        } catch (err) {
          console.error('Failed to create source buffer:', err)
          error.value = 'Failed to create audio buffer'
          cleanup()
        }
      })

      mediaSource.addEventListener('sourceended', () => {
        console.log('MediaSource ended - stream complete, audio should continue playing')
        // Don't cleanup here - let audio.onended handle cleanup when playback actually finishes
      })

      mediaSource.addEventListener('error', (event) => {
        console.error('MediaSource error:', event)
        error.value = 'Media source error'
        cleanup()
      })

      audio.onloadeddata = () => {
        console.log('Audio loaded via MediaSource')
        isLoading.value = false
        isPlaying.value = true
      }

      audio.onended = () => {
        cleanup()
      }

      audio.onerror = (event) => {
        console.error('Audio playback error:', event, event.target?.error)
        error.value = 'Audio playback failed'
        cleanup()
      }
    }

    const startPlayback = () => {
      if (hasStartedPlayback || !audio) return

      hasStartedPlayback = true
      audio
        .play()
        .then(() => {
          console.log('MediaSource audio playback started successfully')
        })
        .catch((err) => {
          console.error('MediaSource audio play failed:', err)
          error.value = 'Audio play failed'
          cleanup()
        })
    }

    const appendChunkToBuffer = (chunk) => {
      if (!sourceBuffer || sourceBuffer.updating) {
        pendingChunks.push(chunk)
        return
      }

      try {
        sourceBuffer.appendBuffer(chunk)
      } catch (err) {
        console.error('Failed to append chunk to buffer:', err)
        pendingChunks.push(chunk)
      }
    }

    initializeMediaSource()

    // Store references for chunk appending
    activeAudio.value = {
      audio,
      url: audio.src,
      mediaSource,
      sourceBuffer,
      appendChunk: (chunk) => {
        chunksReceived++
        console.log('Received chunk', chunksReceived, 'size:', chunk.byteLength, 'bytes')

        if (isSourceOpen) {
          appendChunkToBuffer(chunk)
        } else {
          pendingChunks.push(chunk)
        }
      },
      endStream: () => {
        isEnded = true
        console.log('Stream ended, total chunks received:', chunksReceived)

        // End the stream if source buffer is ready and no pending chunks
        if (
          sourceBuffer &&
          !sourceBuffer.updating &&
          pendingChunks.length === 0 &&
          mediaSource.readyState === 'open'
        ) {
          console.log('Ending MediaSource immediately - no pending operations')
          try {
            mediaSource.endOfStream()
          } catch (err) {
            console.log('Error ending MediaSource in endStream:', err)
          }
        } else {
          console.log('Deferring MediaSource end - waiting for buffer updates to complete')
        }
      },
    }
  }

  /**
   * Play audio from REST streaming response (voice samples)
   */
  const playStreamingResponse = async (response, audioId = 'stream') => {
    try {
      stopAudio()

      isLoading.value = true
      error.value = null
      playingAudioId.value = audioId

      // Convert streaming response to blob
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onloadeddata = () => {
        isLoading.value = false
        isPlaying.value = true
      }

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        cleanup()
      }

      audio.onerror = () => {
        console.error('Audio playback error')
        URL.revokeObjectURL(audioUrl)
        error.value = 'Audio playback failed'
        cleanup()
      }

      activeAudio.value = { audio, url: audioUrl }
      await audio.play()
    } catch (err) {
      console.error('Failed to play streaming audio:', err)
      error.value = 'Failed to play streaming audio'
      cleanup()
    }
  }

  /**
   * Stop currently playing audio
   */
  const stopAudio = () => {
    if (activeAudio.value?.audio) {
      activeAudio.value.audio.pause()
      activeAudio.value.audio.currentTime = 0
    }
    cleanup()
  }

  /**
   * Clean up audio resources including MediaSource objects
   */
  const cleanup = () => {
    if (activeAudio.value?.audio) {
      activeAudio.value.audio.pause()
      // Don't clear src immediately if using MediaSource - causes "Empty src" errors
      if (!activeAudio.value.mediaSource) {
        activeAudio.value.audio.src = ''
        activeAudio.value.audio.load()
      }
    }

    if (activeAudio.value?.mediaSource) {
      try {
        if (activeAudio.value.mediaSource.readyState === 'open') {
          activeAudio.value.mediaSource.endOfStream()
        }
      } catch (err) {
        console.log('MediaSource cleanup error (safe to ignore):', err)
      }
    }

    if (activeAudio.value?.url) {
      // Use setTimeout to delay URL cleanup for MediaSource to prevent "Empty src" errors
      if (activeAudio.value.mediaSource) {
        setTimeout(() => URL.revokeObjectURL(activeAudio.value?.url), 100)
      } else {
        URL.revokeObjectURL(activeAudio.value.url)
      }
    }

    activeAudio.value = null
    playingAudioId.value = null
    isPlaying.value = false
    isLoading.value = false
  }

  // Cleanup on component unmount
  onUnmounted(() => {
    stopAudio()
  })

  return {
    // State
    playingAudioId,
    isLoading,
    isPlaying,
    error,
    activeAudio,

    // Methods
    playWebSocketAudio, // For conversation/challenge audio (WebSocket chunks)
    playStreamingResponse, // For voice samples (REST streaming response)
    stopAudio,
  }
}
