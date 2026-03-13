import { expect } from '@playwright/test'

const DEFAULT_CONVERSATION_WS_REGEX = /\/api\/encounters\/\d+\/conversation\/\d+\/\d+/

export const installWebSocketProbe = async (page) => {
  await page.addInitScript(() => {
    if (window.__wsProbeInstalled) return
    window.__wsProbeInstalled = true

    window.__wsProbe = {
      wsUrls: [],
      outboundMessages: [],
      endSentAt: null,
      inboundBlobCount: 0,
      inboundTextMessages: [],
      closeEvents: [],
      connections: [],
    }

    const NativeWebSocket = window.WebSocket
    class ProbedWebSocket extends NativeWebSocket {
      constructor(url, protocols) {
        super(url, protocols)
        window.__wsProbe.wsUrls.push(String(url))
        window.__wsProbe.connections.push(this)
        this.addEventListener('message', (event) => {
          if (event.data instanceof Blob) {
            window.__wsProbe.inboundBlobCount += 1
          } else if (typeof event.data === 'string') {
            window.__wsProbe.inboundTextMessages.push(event.data)
          }
        })
        this.addEventListener('close', (event) => {
          window.__wsProbe.closeEvents.push({
            url: String(this.url),
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
            ts: Date.now(),
          })
        })
      }

      send(data) {
        if (typeof data === 'string') {
          window.__wsProbe.outboundMessages.push(data)
          if (data === 'END') {
            window.__wsProbe.endSentAt = Date.now()
          }
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
    endSentAt: window.__wsProbe?.endSentAt || null,
    inboundBlobCount: window.__wsProbe?.inboundBlobCount || 0,
    inboundTextMessages: window.__wsProbe?.inboundTextMessages || [],
    closeEvents: window.__wsProbe?.closeEvents || [],
  }))
}

export const injectWebSocketTextMessage = async (
  page,
  { text, wsPathRegex = DEFAULT_CONVERSATION_WS_REGEX } = {}
) => {
  return page.evaluate(
    ({ text, wsPathRegexSource, wsPathRegexFlags }) => {
      const regex = new RegExp(wsPathRegexSource, wsPathRegexFlags)
      const connections = window.__wsProbe?.connections || []
      const targets = connections.filter((ws) => regex.test(String(ws.url)))
      targets.forEach((ws) => {
        ws.dispatchEvent(new MessageEvent('message', { data: text }))
      })
      return targets.length
    },
    {
      text,
      wsPathRegexSource: wsPathRegex.source,
      wsPathRegexFlags: wsPathRegex.flags,
    }
  )
}

export const forceWebSocketClose = async (
  page,
  { code = 1000, reason = '', wsPathRegex = DEFAULT_CONVERSATION_WS_REGEX } = {}
) => {
  // In Playwright probes, native `ws.close()` is not always observable by app-level handlers.
  // This helper targets the most recent matching socket and synthesizes a close callback/event.
  // Each Playwright worker has its own browser context, so sockets are already isolated per test.
  // We still pick the latest matching connection to avoid touching non-audio sockets on the page.
  return page.evaluate(
    ({ code, reason, wsPathRegexSource, wsPathRegexFlags }) => {
      const regex = new RegExp(wsPathRegexSource, wsPathRegexFlags)
      const connections = window.__wsProbe?.connections || []
      const targets = connections.filter((ws) => regex.test(String(ws.url)))
      const latestTarget = targets[targets.length - 1]
      const closableTargets = latestTarget ? [latestTarget] : []
      closableTargets.forEach((ws) => {
        const triggerCloseEvent = () => {
          if (typeof ws.onclose === 'function') {
            ws.onclose({ code, reason, wasClean: true })
          } else {
            const closeEvent = new CloseEvent('close', {
              code,
              reason,
              wasClean: true,
            })
            ws.dispatchEvent(closeEvent)
          }
        }
        const syntheticClose = () =>
          triggerCloseEvent()
        try {
          ws.close(code, reason)
          // `ws.close()` does not always deliver an observable close callback in this
          // probe setup, so we emit a synthetic close event for deterministic client handling.
          syntheticClose()
        } catch {
          // In some timing states `close()` throws; still deliver the policy-close event.
          syntheticClose()
        }
      })
      return closableTargets.length
    },
    {
      code,
      reason,
      wsPathRegexSource: wsPathRegex.source,
      wsPathRegexFlags: wsPathRegex.flags,
    }
  )
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
        const closedAfterEnd =
          probe.endSentAt &&
          probe.closeEvents.some(
            (event) => wsPathRegex.test(event.url) && event.ts >= probe.endSentAt
          )
        return usedExpectedWs && sentEnd && audioReturned && (completed || closedAfterEnd)
      },
      { timeout: timeoutMs }
    )
    .toBe(true)
}

export const assertConversationAudioRoundtrip = async (page, options = {}) => {
  await waitForAudioCompletion(page, options)
}
