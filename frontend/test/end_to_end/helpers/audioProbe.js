import { expect } from '@playwright/test'

const DEFAULT_CONVERSATION_WS_REGEX = /\/api\/encounters\/\d+\/conversation\/\d+\/\d+/

export const installWebSocketProbe = async (page) => {
  await page.addInitScript(() => {
    if (window.__wsProbeInstalled) return
    window.__wsProbeInstalled = true

    window.__wsProbe = {
      wsUrls: [],
      outboundMessages: [],
      inboundBlobCount: 0,
      inboundTextMessages: [],
    }

    const NativeWebSocket = window.WebSocket
    class ProbedWebSocket extends NativeWebSocket {
      constructor(url, protocols) {
        super(url, protocols)
        window.__wsProbe.wsUrls.push(String(url))
        this.addEventListener('message', (event) => {
          if (event.data instanceof Blob) {
            window.__wsProbe.inboundBlobCount += 1
          } else if (typeof event.data === 'string') {
            window.__wsProbe.inboundTextMessages.push(event.data)
          }
        })
      }

      send(data) {
        if (typeof data === 'string') {
          window.__wsProbe.outboundMessages.push(data)
        } else {
          window.__wsProbe.outboundMessages.push('[binary]')
        }
        return super.send(data)
      }
    }

    window.WebSocket = ProbedWebSocket
  })
}

export const readWebSocketProbe = async (page) => {
  return page.evaluate(() => ({
    wsUrls: window.__wsProbe?.wsUrls || [],
    outboundMessages: window.__wsProbe?.outboundMessages || [],
    inboundBlobCount: window.__wsProbe?.inboundBlobCount || 0,
    inboundTextMessages: window.__wsProbe?.inboundTextMessages || [],
  }))
}

export const waitForAudioCompletion = async (
  page,
  { wsPathRegex = DEFAULT_CONVERSATION_WS_REGEX, timeoutMs = 60_000 } = {}
) => {
  await expect
    .poll(
      async () => {
        const probe = await readWebSocketProbe(page)
        const usedExpectedWs = probe.wsUrls.some((url) => wsPathRegex.test(url))
        const sentEnd = probe.outboundMessages.includes('END')
        const audioReturned = probe.inboundBlobCount > 0
        const completed = probe.inboundTextMessages.includes('AUDIO_COMPLETE')
        return usedExpectedWs && sentEnd && audioReturned && completed
      },
      { timeout: timeoutMs }
    )
    .toBe(true)
}

export const assertConversationAudioRoundtrip = async (page, options = {}) => {
  await waitForAudioCompletion(page, options)
}
