import { devices, expect, test } from '@playwright/test'
import { assertConversationAudioRoundtrip, installWebSocketProbe } from './helpers/audioProbe.js'
import { assertReturnedToReadyState, runSpeakStopLifecycle } from './helpers/audioLifecycle.js'
import { resolveBaseUrl } from './helpers/baseUrl.js'
import {
  closeTrackedContexts,
  createContextRegistry,
  trackContext,
} from './helpers/contextLifecycle.js'
import { resolveSeededPlayerEncounterFixture } from './helpers/playerEncounterLogin.js'

const getMicrophonePermissionState = async (page) => {
  try {
    return await page.evaluate(async () => {
      if (!navigator.permissions?.query) {
        return 'unsupported'
      }
      const result = await navigator.permissions.query({ name: 'microphone' })
      return result.state
    })
  } catch (error) {
    return `unavailable: ${error.message}`
  }
}

const openPlayerEncounterOnMobile = async (
  browser,
  loginUrl,
  playerId,
  testInfo,
  contextRegistry
) => {
  const mobileContext = trackContext(
    contextRegistry,
    await browser.newContext({
      ...devices['iPhone 12'],
      storageState: undefined,
      baseURL: resolveBaseUrl(testInfo),
      permissions: ['microphone'],
    })
  )
  const mobilePage = await mobileContext.newPage()
  await installWebSocketProbe(mobilePage)

  const consumePromise = mobilePage.waitForResponse((response) => {
    return (
      new RegExp(`/api/players/${playerId}/login\\?token=`).test(response.url()) &&
      response.request().method() === 'GET'
    )
  })
  const encounterPromise = mobilePage.waitForResponse((response) => {
    return (
      response.url().endsWith(`/api/players/${playerId}/encounter`) &&
      response.request().method() === 'GET'
    )
  })

  await mobilePage.goto(loginUrl)
  const consumeResponse = await consumePromise
  const consumeStatus = consumeResponse.status()
  const encounterResponse = await encounterPromise
  const encounterStatus = encounterResponse.status()
  if (consumeStatus === 200 && encounterStatus === 200) {
    await expect(mobilePage).toHaveURL(new RegExp(`/players/${playerId}/encounter$`))
  }
  const encounterPayload = encounterStatus === 200 ? await encounterResponse.json() : null

  return { mobileContext, mobilePage, playerId, encounterPayload, encounterStatus, consumeStatus }
}

const getLoginForPlayerWithEncounter = async (page, browser, testInfo, contextRegistry) => {
  for (let attempt = 0; attempt < 3; attempt++) {
    const fixture = await resolveSeededPlayerEncounterFixture(page, browser, testInfo)
    const playerId = String(fixture.playerId)
    const loginUrl = fixture.loginUrl

    const mobileResult = await openPlayerEncounterOnMobile(
      browser,
      loginUrl,
      playerId,
      testInfo,
      contextRegistry
    )

    if (mobileResult.consumeStatus === 429) {
      await mobileResult.mobileContext.close()
      await page.waitForTimeout(500)
      continue
    }
    if (mobileResult.consumeStatus !== 200 || mobileResult.encounterStatus !== 200) {
      throw new Error(
        `Player encounter login did not return active encounter for seeded fixture player ${playerId}. ` +
          `consume=${mobileResult.consumeStatus}, encounter=${mobileResult.encounterStatus}`
      )
    }

    return {
      playerId,
      mobilePage: mobileResult.mobilePage,
      encounterPayload: mobileResult.encounterPayload,
    }
  }

  throw new Error(
    'Player mobile audio fixture exceeded login consume retries due repeated 429 responses.'
  )
}

const assertEncounterHasCharactersAndTiles = async (mobilePage, encounterPayload, playerId) => {
  const apiCharacters = Array.isArray(encounterPayload?.characters)
    ? encounterPayload.characters
    : []
  if (apiCharacters.length === 0) {
    throw new Error(
      `Player encounter API returned zero characters for player ${playerId}. ` +
        `Encounter payload: ${JSON.stringify({
          id: encounterPayload?.id,
          name: encounterPayload?.name,
          charactersLength: apiCharacters.length,
        })}`
    )
  }

  const tileCount = await mobilePage.locator('.character-tile').count()
  if (tileCount > 0) {
    return
  }

  try {
    await expect
      .poll(async () => await mobilePage.locator('.character-tile').count(), {
        timeout: 10_000,
      })
      .toBeGreaterThan(0)
    return
  } catch {
    const noEncounterVisible =
      (await mobilePage.getByText('No Active Encounter', { exact: true }).count()) > 0
    const loadingVisible =
      (await mobilePage.getByText('Loading encounter...', { exact: false }).count()) > 0
    throw new Error(
      `Character tiles failed to render for player ${playerId} despite API characters. ` +
        `Diagnostics: ${JSON.stringify({
          currentUrl: mobilePage.url(),
          apiCharacterIds: apiCharacters.map((character) => character.id),
          apiCharacterNames: apiCharacters.map((character) => character.name),
          noActiveEncounterVisible: noEncounterVisible,
          loadingVisible,
        })}`
    )
  }
}

test('PLAYER-MOBILE-TALKING-AUDIO-01 returns audio over websocket and completes processing', async ({
  page,
  browser,
}, testInfo) => {
  test.skip(
    testInfo.project.use?.browserName === 'webkit',
    'WebKit microphone automation is not reliably supported for this audio flow.'
  )
  test.skip(
    process.env.ENCOUNTERS_AUDIO_TEST !== '1',
    'Player mobile audio test runs only in dedicated player mobile audio command.'
  )
  test.setTimeout(90_000)

  const browserName = testInfo.project.use?.browserName || testInfo.project.name
  const contextRegistry = createContextRegistry()
  try {
    const { playerId, mobilePage, encounterPayload } = await getLoginForPlayerWithEncounter(
      page,
      browser,
      testInfo,
      contextRegistry
    )
    await assertEncounterHasCharactersAndTiles(mobilePage, encounterPayload, playerId)
    const characterTiles = mobilePage.locator('.character-tile')

    await characterTiles.first().click()
    await expect(mobilePage.locator('.interaction-panel')).toBeVisible()

    await runSpeakStopLifecycle(mobilePage, { clickWithEvaluate: true })
    await assertConversationAudioRoundtrip(mobilePage, {
      wsPathRegex: /\/api\/encounters\/\d+\/conversation\/\d+\/\d+/,
      timeoutMs: 60_000,
    })
    await assertReturnedToReadyState(mobilePage, {
      readyTextPattern: /Tap Speak/,
      timeoutMs: 60_000,
    })
  } catch (error) {
    const dmMicPermission = await getMicrophonePermissionState(page)
    let mobileMicPermission = 'unavailable'
    const trackedContexts = [...contextRegistry]
    if (trackedContexts.length > 0) {
      const maybePage = trackedContexts[trackedContexts.length - 1]?.pages?.()[0]
      if (maybePage) {
        mobileMicPermission = await getMicrophonePermissionState(maybePage)
      }
    }
    throw new Error(
      `Player mobile audio flow failed in ${browserName}. Diagnostics: ${JSON.stringify({
        dmUrl: page.url(),
        mobileUrl:
          trackedContexts[trackedContexts.length - 1]?.pages?.()[0]?.url?.() || 'unavailable',
        dmMicPermission,
        mobileMicPermission,
      })}. Root error: ${error.message}`
    )
  } finally {
    await closeTrackedContexts(contextRegistry)
  }
})
