import { devices, expect, test } from '@playwright/test'
import { assertConversationAudioRoundtrip, installWebSocketProbe } from './helpers/audioProbe.js'
import { assertReturnedToReadyState, runSpeakStopLifecycle } from './helpers/audioLifecycle.js'

const MOBILE_BASE_URL = 'http://localhost:3001'

const waitForPlayersGet = async (page) => {
  const response = await page.waitForResponse((candidate) => {
    return candidate.url().endsWith('/api/players') && candidate.request().method() === 'GET'
  })
  expect(response.status()).toBe(200)
}

const toAbsolutePlayerLoginUrl = (rawLoginUrl) => {
  return new URL(rawLoginUrl, MOBILE_BASE_URL).toString()
}

const generatePlayerLoginLinkFromDmView = async (page) => {
  await page.goto('/players')
  await waitForPlayersGet(page)

  const playerListItems = page.locator('.list-content .list-item')
  await expect(playerListItems.first()).toBeVisible()
  await playerListItems.first().click()

  const generateResponsePromise = page.waitForResponse((response) => {
    return (
      /\/api\/players\/\d+\/login$/.test(response.url()) && response.request().method() === 'POST'
    )
  })

  await page.getByTitle('Generate new login link').click()
  const response = await generateResponsePromise
  expect(response.status()).toBe(200)

  const payload = await response.json()
  expect(typeof payload.login_url).toBe('string')
  expect(payload.login_url.length).toBeGreaterThan(0)
  expect(payload.login_url).toMatch(/\/players\/\d+\/login\?token=/)

  const absoluteLoginUrl = toAbsolutePlayerLoginUrl(payload.login_url)
  const parsed = new URL(absoluteLoginUrl)
  const playerId = parsed.pathname.match(/\/players\/(\d+)\/login/)?.[1]
  if (!playerId) {
    throw new Error(`Could not parse player id from login url: ${absoluteLoginUrl}`)
  }

  return {
    loginUrl: absoluteLoginUrl,
    playerId,
  }
}

const openPlayerEncounterOnMobile = async (browser, loginUrl, playerId) => {
  const mobileContext = await browser.newContext({
    ...devices['iPhone 12'],
    storageState: undefined,
    baseURL: MOBILE_BASE_URL,
  })
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
  expect(consumeResponse.status()).toBe(200)

  const encounterResponse = await encounterPromise
  expect(encounterResponse.status()).toBe(200)
  const encounterPayload = await encounterResponse.json()
  await expect(mobilePage).toHaveURL(new RegExp(`/players/${playerId}/encounter$`))

  return { mobileContext, mobilePage, playerId, encounterPayload }
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
}) => {
  test.skip(
    process.env.ENCOUNTERS_AUDIO_TEST !== '1',
    'Player mobile audio test runs only in dedicated player mobile audio command.'
  )
  test.setTimeout(90_000)

  const { loginUrl, playerId } = await generatePlayerLoginLinkFromDmView(page)
  const { mobileContext, mobilePage, encounterPayload } = await openPlayerEncounterOnMobile(
    browser,
    loginUrl,
    playerId
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

  await mobileContext.close()
})
