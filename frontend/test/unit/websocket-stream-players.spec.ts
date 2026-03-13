import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import BaseWebSocketMediaPlayer from '../../src/composables/audio/BaseWebSocketMediaPlayer'
import BufferedWebSocketPlayer from '../../src/composables/audio/BufferedWebSocketPlayer'
import ManagedMediaSourceWebSocketPlayer from '../../src/composables/audio/ManagedMediaSourceWebSocketPlayer'
import MediaSourceWebSocketPlayer from '../../src/composables/audio/MediaSourceWebSocketPlayer'
import { UnsupportedStreamingError } from '../../src/composables/audio/streamErrors'
import { createWebSocketStreamPlayer } from '../../src/composables/audio/createWebSocketStreamPlayer'

type RuntimeGlobals = typeof globalThis & {
  window?: Record<string, unknown>
  MediaSource?: unknown
  ManagedMediaSource?: unknown
  Audio?: unknown
  URL?: unknown
}

describe('websocket stream players', () => {
  const runtime = globalThis as RuntimeGlobals
  let originalWindow: typeof globalThis.window
  let originalMediaSource: typeof globalThis.MediaSource
  let originalManagedMediaSource: unknown
  let originalAudio: typeof globalThis.Audio
  let originalURL: typeof globalThis.URL
  const installManagedMediaSourceSupport = (supported: boolean) => {
    class FakeManagedMediaSource {
      static isTypeSupported() {
        return supported
      }
    }
    runtime.window!.ManagedMediaSource = FakeManagedMediaSource
    runtime.ManagedMediaSource = FakeManagedMediaSource
    return FakeManagedMediaSource
  }
  const installMediaSourceSupport = (supported: boolean) => {
    class FakeMediaSource {
      static isTypeSupported() {
        return supported
      }
    }
    runtime.window!.MediaSource = FakeMediaSource
    runtime.MediaSource = FakeMediaSource
    return FakeMediaSource
  }

  beforeEach(() => {
    originalWindow = runtime.window as typeof globalThis.window
    originalMediaSource = runtime.MediaSource as typeof globalThis.MediaSource
    originalManagedMediaSource = runtime.ManagedMediaSource
    originalAudio = runtime.Audio as typeof globalThis.Audio
    originalURL = runtime.URL as typeof globalThis.URL

    runtime.window = runtime.window || {}
    runtime.window.Audio = class FakeAudio {}
    runtime.Audio = runtime.window.Audio
    runtime.URL = {
      createObjectURL: vi.fn(() => 'blob:audio'),
      revokeObjectURL: vi.fn(),
    }
  })

  afterEach(() => {
    runtime.window = originalWindow as unknown as Record<string, unknown>
    runtime.MediaSource = originalMediaSource
    runtime.ManagedMediaSource = originalManagedMediaSource
    runtime.Audio = originalAudio
    runtime.URL = originalURL
    vi.restoreAllMocks()
  })

  it('base player teardown is idempotent under end+stop race', async () => {
    const audio = {
      ended: true,
      pause: vi.fn(),
      removeAttribute: vi.fn(),
      load: vi.fn(),
      removeEventListener: vi.fn(),
      addEventListener: vi.fn(),
      srcObject: null,
    }
    const sourceBuffer = {
      updating: false,
      removeEventListener: vi.fn(),
      addEventListener: vi.fn(),
      abort: vi.fn(),
    }
    const mediaSource = {
      readyState: 'open',
      sourceBuffers: [],
      endOfStream: vi.fn(),
      removeSourceBuffer: vi.fn(),
      removeEventListener: vi.fn(),
      addEventListener: vi.fn(),
    }

    const player = new BaseWebSocketMediaPlayer({
      audioEl: audio as any,
      logPrefix: 'TestPlayer',
    }) as any
    player.mediaSource = mediaSource
    player.sourceBuffer = sourceBuffer
    player._sleep = vi.fn().mockResolvedValue(undefined)

    const endPromise = player.end()
    const stopPromise = player.stop()
    await Promise.all([endPromise, stopPromise])

    expect(audio.pause).toHaveBeenCalledTimes(1)
    expect(player.mediaSource).toBeNull()
    expect(player.sourceBuffer).toBeNull()
    expect(player.audio).toBeNull()
  })

  it('buffered player end resolves and releases resources on success', async () => {
    const audio = {
      muted: false,
      src: '',
      playsInline: false,
      pause: vi.fn(),
      removeAttribute: vi.fn(),
      load: vi.fn(),
      play: vi.fn().mockResolvedValue(undefined),
      addEventListener: vi.fn((name: string, handler: () => void) => {
        if (name === 'ended') {
          setTimeout(() => handler(), 0)
        }
      }),
    }

    const player = new BufferedWebSocketPlayer({
      audioEl: audio as any,
      mimeType: 'audio/mp4; codecs=mp4a.40.2',
    }) as any

    await player.append(new Uint8Array([1, 2, 3]).buffer)
    await expect(player.end()).resolves.toBeNull()

    expect((runtime.URL as typeof URL).createObjectURL).toHaveBeenCalledTimes(1)
    expect((runtime.URL as typeof URL).revokeObjectURL).toHaveBeenCalledTimes(1)
    expect(player.objectUrl).toBeNull()
    expect(player.chunks).toEqual([])
    expect(player.audio).toBeNull()
  })

  it('buffered player end resolves and releases resources when playback errors', async () => {
    const audio = {
      muted: false,
      src: '',
      playsInline: false,
      pause: vi.fn(),
      removeAttribute: vi.fn(),
      load: vi.fn(),
      play: vi.fn().mockRejectedValue(new Error('playback failed')),
      addEventListener: vi.fn(),
    }

    const player = new BufferedWebSocketPlayer({
      audioEl: audio as any,
      mimeType: 'audio/mp4; codecs=mp4a.40.2',
    }) as any

    await player.append(new Uint8Array([1, 2, 3]).buffer)
    await expect(player.end()).resolves.toBeNull()

    expect((runtime.URL as typeof URL).createObjectURL).toHaveBeenCalledTimes(1)
    expect((runtime.URL as typeof URL).revokeObjectURL).toHaveBeenCalledTimes(1)
    expect(player.objectUrl).toBeNull()
    expect(player.chunks).toEqual([])
    expect(player.audio).toBeNull()
  })

  it('selects ManagedMediaSource player when supported', () => {
    installManagedMediaSourceSupport(true)

    const player = createWebSocketStreamPlayer({
      mimeType: 'audio/mp4; codecs=mp4a.40.2',
    })

    expect(player).toBeInstanceOf(ManagedMediaSourceWebSocketPlayer)
  })

  it('falls back to MediaSource player when ManagedMediaSource is unsupported', () => {
    installManagedMediaSourceSupport(false)
    installMediaSourceSupport(true)

    const player = createWebSocketStreamPlayer({
      mimeType: 'audio/mp4; codecs=mp4a.40.2',
    })

    expect(player).toBeInstanceOf(MediaSourceWebSocketPlayer)
  })

  it('falls back to buffered player when MSE variants are unsupported', () => {
    installManagedMediaSourceSupport(false)
    installMediaSourceSupport(false)
    runtime.window!.Audio = class FakeAudio {}
    runtime.Audio = runtime.window!.Audio

    const player = createWebSocketStreamPlayer({
      mimeType: 'audio/mp4; codecs=mp4a.40.2',
    })

    expect(player).toBeInstanceOf(BufferedWebSocketPlayer)
  })

  it('throws UnsupportedStreamingError when no audio streaming strategy is available', () => {
    installManagedMediaSourceSupport(false)
    installMediaSourceSupport(false)
    delete runtime.window!.Audio
    delete runtime.Audio

    expect(() =>
      createWebSocketStreamPlayer({
        mimeType: 'audio/mp4; codecs=mp4a.40.2',
      })
    ).toThrow(UnsupportedStreamingError)
  })
})
