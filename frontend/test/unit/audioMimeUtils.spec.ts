import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import {
  inferFormatParam,
  pickPlaybackMimeType,
  pickRecorderMimeType,
} from '../../src/composables/audio/useWebSocketAudioHandler'

describe('audio mime helpers', () => {
  const originalWindow = globalThis.window
  const originalMediaRecorder = globalThis.MediaRecorder

  beforeEach(() => {
    globalThis.window = {}
  })

  afterEach(() => {
    if (originalWindow === undefined) {
      delete globalThis.window
    } else {
      globalThis.window = originalWindow
    }

    if (originalMediaRecorder === undefined) {
      delete globalThis.MediaRecorder
    } else {
      globalThis.MediaRecorder = originalMediaRecorder
    }

    vi.restoreAllMocks()
  })

  it('pickRecorderMimeType returns empty when unsupported', () => {
    expect(pickRecorderMimeType()).toBe('')
  })

  it('pickRecorderMimeType returns first supported candidate', () => {
    class FakeRecorder {
      static isTypeSupported(mimeType) {
        return mimeType === 'audio/ogg;codecs=opus'
      }
    }

    globalThis.MediaRecorder = FakeRecorder
    globalThis.window.MediaRecorder = FakeRecorder

    expect(pickRecorderMimeType()).toBe('audio/ogg;codecs=opus')
  })

  it('inferFormatParam maps common mime types', () => {
    expect(inferFormatParam('audio/webm;codecs=opus')).toBe('webm')
    expect(inferFormatParam('audio/mp4')).toBe('mp4')
    expect(inferFormatParam('audio/ogg;codecs=opus')).toBe('ogg')
    expect(inferFormatParam('')).toBe('webm')
    expect(inferFormatParam('audio/unknown')).toBe('webm')
  })

  it('pickPlaybackMimeType returns first supported', () => {
    expect(pickPlaybackMimeType()).toBe('audio/mp4; codecs=mp4a.40.2')
  })

  it('pickPlaybackMimeType returns empty when none supported', () => {
    expect(pickPlaybackMimeType()).toBe('audio/mp4; codecs=mp4a.40.2')
  })
})
