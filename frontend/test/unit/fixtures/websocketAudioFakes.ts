import { vi } from 'vitest'

export const websocketAudioTestState = {
  latestWebSocket: null as FakeWebSocket | null,
  autoOpenDelayMs: 0,
  autoErrorOnConstruct: false,
}

export const resetWebsocketAudioTestState = () => {
  websocketAudioTestState.latestWebSocket = null
  websocketAudioTestState.autoOpenDelayMs = 0
  websocketAudioTestState.autoErrorOnConstruct = false
}

export class FakeWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = FakeWebSocket.CONNECTING
  url: string
  onopen: ((event?: unknown) => void) | null = null
  onmessage: ((event: { data: unknown }) => void) | null = null
  onerror: ((event?: unknown) => void) | null = null
  onclose: ((event: { code: number }) => void) | null = null
  send = vi.fn()
  close = vi.fn(() => {
    if (this.readyState === FakeWebSocket.CLOSED) return
    this.readyState = FakeWebSocket.CLOSED
    if (this.onclose) {
      this.onclose({ code: 1000 })
    }
  })

  constructor(url: string) {
    websocketAudioTestState.latestWebSocket = this
    this.url = url
    if (websocketAudioTestState.autoErrorOnConstruct) {
      setTimeout(() => {
        if (this.readyState !== FakeWebSocket.CLOSED && this.onerror) {
          this.onerror(new Error('forced websocket error'))
        }
      }, 0)
      return
    }
    setTimeout(() => {
      if (this.readyState === FakeWebSocket.CLOSED) return
      this.readyState = FakeWebSocket.OPEN
      if (this.onopen) {
        this.onopen()
      }
    }, websocketAudioTestState.autoOpenDelayMs)
  }

  emitMessage(data: unknown) {
    if (this.onmessage) {
      this.onmessage({ data })
    }
  }

  emitClose(code: number) {
    this.readyState = FakeWebSocket.CLOSED
    if (this.onclose) {
      this.onclose({ code })
    }
  }
}

export class FakeMediaRecorder {
  static isTypeSupported = vi.fn(() => true)
  state = 'inactive'
  mimeType: string
  ondataavailable: ((event: { data: Blob }) => void) | null = null
  onstop: (() => void) | null = null
  private listeners: Record<string, Array<() => void>> = {}

  constructor(_stream: unknown, opts?: { mimeType?: string }) {
    this.mimeType = opts?.mimeType || 'audio/webm'
  }

  start() {
    this.state = 'recording'
  }

  stop() {
    this.state = 'inactive'
    if (this.onstop) {
      this.onstop()
    }
    for (const listener of this.listeners.stop || []) {
      listener()
    }
  }

  addEventListener(name: string, handler: () => void) {
    this.listeners[name] = this.listeners[name] || []
    this.listeners[name].push(handler)
  }

  removeEventListener(name: string, handler: () => void) {
    this.listeners[name] = (this.listeners[name] || []).filter((entry) => entry !== handler)
  }
}

export const installWebsocketAudioGlobals = (getUserMediaMock: ReturnType<typeof vi.fn>) => {
  const globalAny = globalThis as any
  globalAny.window = globalAny
  globalAny.WebSocket = FakeWebSocket
  globalAny.MediaRecorder = FakeMediaRecorder
  Object.defineProperty(globalAny, 'navigator', {
    configurable: true,
    value: {
      mediaDevices: {
        getUserMedia: getUserMediaMock,
      },
    },
  })
}
