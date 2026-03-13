import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import { useWebSocketAudioHandler } from '../../src/composables/audio/useWebSocketAudioHandler'
import {
  installWebsocketAudioGlobals,
  resetWebsocketAudioTestState,
  websocketAudioTestState,
} from './fixtures/websocketAudioFakes'

// `vi.mock(...)` is hoisted by Vitest, so these mock refs must also be created
// in hoisted scope and then configured/reset inside each test lifecycle.
const { pushMock, checkAuthMock, createWebSocketStreamPlayerMock } = vi.hoisted(() => {
  return {
    pushMock: vi.fn(),
    checkAuthMock: vi.fn(),
    createWebSocketStreamPlayerMock: vi.fn(),
  }
})

vi.mock('vue-router', () => {
  return {
    useRouter: () => ({ push: pushMock }),
  }
})

vi.mock('../../src/services/api', () => {
  return {
    checkAuth: checkAuthMock,
  }
})

vi.mock('../../src/composables/audio/createWebSocketStreamPlayer', () => {
  return {
    createWebSocketStreamPlayer: createWebSocketStreamPlayerMock,
  }
})

describe('useWebSocketAudioHandler', () => {
  let getUserMediaMock: ReturnType<typeof vi.fn>

  const createAudioElement = () => {
    return {
      ended: true,
      paused: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      pause: vi.fn(),
      removeAttribute: vi.fn(),
      load: vi.fn(),
    }
  }

  const createStreamPlayer = () => {
    return {
      mode: 'mediaSource',
      prepare: vi.fn().mockResolvedValue(undefined),
      append: vi.fn().mockResolvedValue(undefined),
      end: vi.fn().mockResolvedValue(undefined),
      stop: vi.fn().mockResolvedValue(undefined),
    }
  }

  const getLatestWebSocket = () => {
    const ws = websocketAudioTestState.latestWebSocket
    expect(ws).not.toBeNull()
    return ws!
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    pushMock.mockReset()
    checkAuthMock.mockReset()
    createWebSocketStreamPlayerMock.mockReset()
    resetWebsocketAudioTestState()

    getUserMediaMock = vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    })
    installWebsocketAudioGlobals(getUserMediaMock)
  })

  it('returns false when selected player is missing and does not open media/websocket', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: null as any,
      characterId: 3,
    })

    expect(started).toBe(false)
    expect(getUserMediaMock).not.toHaveBeenCalled()
    expect(createWebSocketStreamPlayerMock).not.toHaveBeenCalled()
    expect(websocketAudioTestState.latestWebSocket).toBeNull()
  })

  it('returns false when character is missing and does not open media/websocket', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: null as any,
    })

    expect(started).toBe(false)
    expect(getUserMediaMock).not.toHaveBeenCalled()
    expect(createWebSocketStreamPlayerMock).not.toHaveBeenCalled()
    expect(websocketAudioTestState.latestWebSocket).toBeNull()
  })

  it('returns false for challenge mode without required skill or dice roll', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const missingSkill = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
      isChallengeMode: true,
      selectedSkill: '',
      diceRoll: 10,
    })
    const missingDiceRoll = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
      isChallengeMode: true,
      selectedSkill: 'persuasion',
      diceRoll: null,
    })

    expect(missingSkill).toBe(false)
    expect(missingDiceRoll).toBe(false)
    expect(getUserMediaMock).not.toHaveBeenCalled()
    expect(createWebSocketStreamPlayerMock).not.toHaveBeenCalled()
  })

  it('requires a ready world id and allows starting once world id becomes available', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)

    const worldIdRef = ref<number | null>(null)
    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: worldIdRef,
    })

    const startedWithoutWorld = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(startedWithoutWorld).toBe(false)
    expect(getUserMediaMock).not.toHaveBeenCalled()

    worldIdRef.value = 1
    const startedWithWorld = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(startedWithWorld).toBe(true)
    expect(getLatestWebSocket().url).toContain('world_id=1')

    await handler.cleanup()
  })

  it('handles AUDIO_COMPLETE by ending stream and clearing processing state', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)

    const audioListeners: Record<string, ((event?: unknown) => void)[]> = {}
    const audioElement: any = {
      ended: true,
      paused: true,
      addEventListener: vi.fn((name: string, handler: (event?: unknown) => void) => {
        audioListeners[name] = audioListeners[name] || []
        audioListeners[name].push(handler)
      }),
      removeEventListener: vi.fn((name: string, handler: (event?: unknown) => void) => {
        audioListeners[name] = (audioListeners[name] || []).filter((entry) => entry !== handler)
      }),
      pause: vi.fn(),
      removeAttribute: vi.fn(),
      load: vi.fn(),
    }

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(audioElement),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    await handler.stopSession()
    expect(handler.isProcessing.value).toBe(true)

    getLatestWebSocket().emitMessage('AUDIO_COMPLETE')
    await Promise.resolve()

    expect(streamPlayer.end).toHaveBeenCalledTimes(1)
    expect(handler.isProcessing.value).toBe(false)

    await handler.cleanup()
  })

  it('forwards conversation_data payloads to callback', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)

    const onConversationData = vi.fn()
    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData,
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    getLatestWebSocket().emitMessage(
      JSON.stringify({ type: 'conversation_data', influence: 17, reveals: [] })
    )

    expect(onConversationData).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'conversation_data', influence: 17 })
    )

    await handler.cleanup()
  })

  it('handles billing_error payload by closing websocket and invoking callback', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)

    const onBillingError = vi.fn()
    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError,
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    getLatestWebSocket().emitMessage(
      JSON.stringify({ type: 'billing_error', code: 'INSUFFICIENT_TOKENS' })
    )

    expect(onBillingError).toHaveBeenCalledTimes(1)
    expect(getLatestWebSocket().close).toHaveBeenCalledTimes(1)
    expect(handler.isProcessing.value).toBe(false)

    await handler.cleanup()
  })

  it('ignores malformed websocket JSON payloads safely', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)

    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    getLatestWebSocket().emitMessage('NOT_JSON')

    expect(warnSpy).toHaveBeenCalledWith('Ignoring non-JSON websocket message')
    warnSpy.mockRestore()

    await handler.cleanup()
  })

  it('checks auth and redirects to /login when websocket closes with 1008', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(false)

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    getLatestWebSocket().emitClose(1008)
    await Promise.resolve()
    await Promise.resolve()

    expect(checkAuthMock).toHaveBeenCalledTimes(1)
    expect(pushMock).toHaveBeenCalledWith('/login')

    await handler.cleanup()
  })

  it('does not throw when 1008 auth check fails and remains reusable', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockRejectedValue(new Error('auth check failed'))

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const started = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(started).toBe(true)

    getLatestWebSocket().emitClose(1008)
    await Promise.resolve()
    await Promise.resolve()

    expect(checkAuthMock).toHaveBeenCalledTimes(1)
    expect(handler.isRecording.value).toBe(false)

    checkAuthMock.mockResolvedValue(true)
    const restarted = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(restarted).toBe(true)

    await handler.cleanup()
  })

  it('can recover after websocket onerror and start a new session', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)
    websocketAudioTestState.autoErrorOnConstruct = true

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const firstAttempt = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(firstAttempt).toBe(false)
    expect(handler.isRecording.value).toBe(false)
    expect(handler.isProcessing.value).toBe(false)

    websocketAudioTestState.autoErrorOnConstruct = false
    const secondAttempt = await handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })
    expect(secondAttempt).toBe(true)

    await handler.cleanup()
  })

  it('closes a connecting websocket and fails start cleanly', async () => {
    const streamPlayer = createStreamPlayer()
    createWebSocketStreamPlayerMock.mockReturnValue(streamPlayer)
    checkAuthMock.mockResolvedValue(true)
    websocketAudioTestState.autoOpenDelayMs = 50

    const handler = useWebSocketAudioHandler({
      audioElementRef: ref(createAudioElement()),
      onConversationData: vi.fn(),
      onBillingError: vi.fn(),
      worldId: 1,
    })

    const startPromise = handler.startSession({
      encounterId: 1,
      selectedPlayerId: 2,
      characterId: 3,
    })

    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(getLatestWebSocket().readyState).toBe(WebSocket.CONNECTING)

    handler.closeWebSocket()
    expect(getLatestWebSocket().close).toHaveBeenCalledTimes(1)

    await expect(startPromise).resolves.toBe(false)
    expect(handler.isRecording.value).toBe(false)
  })
})
