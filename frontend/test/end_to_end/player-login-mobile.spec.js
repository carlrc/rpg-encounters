import { devices, expect, test } from '@playwright/test'
import { resolveBaseUrl } from './helpers/baseUrl.js'
import {
  closeTrackedContexts,
  createContextRegistry,
  trackContext,
} from './helpers/contextLifecycle.js'
import { waitForApiResponse } from './helpers/networkAsserts.js'
import { resolveSeededPlayerEncounterFixture } from './helpers/playerEncounterLogin.js'

const loginAsPlayerOnMobile = async (browser, loginUrl, playerId, testInfo, contextRegistry) => {
  const mobileContext = trackContext(
    contextRegistry,
    await browser.newContext({
      ...devices['iPhone 12'],
      storageState: undefined,
      baseURL: resolveBaseUrl(testInfo),
    })
  )
  const mobilePage = await mobileContext.newPage()

  const consumePromise = waitForApiResponse(mobilePage, {
    method: 'GET',
    pathRegex: new RegExp(`/api/players/${playerId}/login\\?token=`),
    expectedStatus: 200,
  })
  const encounterPromise = mobilePage.waitForResponse((response) => {
    return (
      response.url().endsWith(`/api/players/${playerId}/encounter`) &&
      response.request().method() === 'GET'
    )
  })

  await mobilePage.goto(loginUrl)

  await consumePromise
  const encounterResponse = await encounterPromise
  const encounterStatus = encounterResponse.status()
  if (encounterStatus === 200) {
    await expect(mobilePage).toHaveURL(new RegExp(`/players/${playerId}/encounter$`))
  }

  return { mobileContext, mobilePage, encounterStatus }
}

const getLoginForPlayerWithEncounter = async (page, browser, testInfo, contextRegistry) => {
  const fixture = await resolveSeededPlayerEncounterFixture(page, browser, testInfo)
  const playerId = String(fixture.playerId)
  const loginUrl = fixture.loginUrl
  const { mobileContext, mobilePage, encounterStatus } = await loginAsPlayerOnMobile(
    browser,
    loginUrl,
    playerId,
    testInfo,
    contextRegistry
  )

  if (encounterStatus !== 200) {
    throw new Error(
      `Player encounter login did not return active encounter for seeded fixture player ${playerId}. Status: ${encounterStatus}`
    )
  }

  return {
    loginUrl,
    playerId,
    mobileContext,
    mobilePage,
  }
}

test('PLAYER-LOGIN-MOBILE-01 generates player login link (DM) and consumes it on iPhone 12', async ({
  page,
  browser,
}, testInfo) => {
  const contextRegistry = createContextRegistry()
  try {
    await getLoginForPlayerWithEncounter(page, browser, testInfo, contextRegistry)
  } finally {
    await closeTrackedContexts(contextRegistry)
  }
})

test('PLAYER-MOBILE-VIEW-01 player encounter content renders and basic tap flow works on iPhone 12', async ({
  page,
  browser,
}, testInfo) => {
  const contextRegistry = createContextRegistry()
  try {
    const loginResult = await getLoginForPlayerWithEncounter(
      page,
      browser,
      testInfo,
      contextRegistry
    )
    const { mobilePage } = loginResult

    await expect(mobilePage.locator('.encounter-title')).toBeVisible()
    await expect(mobilePage.locator('.section-title', { hasText: 'Characters' })).toBeVisible()

    const characterTile = mobilePage.locator('.character-tile').first()
    await expect(characterTile).toBeVisible()
    await characterTile.click()

    const interactionPanel = mobilePage.locator('.interaction-panel')
    await expect(interactionPanel).toBeVisible()
    await expect(interactionPanel.getByText(/Talking with/)).toBeVisible()
    await expect(mobilePage.getByRole('button', { name: 'Speak' })).toBeVisible()
    await expect(
      mobilePage.locator('.shared-status-text').filter({
        hasText: /Tap Speak to start conversation|Select a skill for challenge/,
      })
    ).toBeVisible()

    await mobilePage.locator('.close-btn').click()
    await expect(interactionPanel).toHaveCount(0)

    const viewportCheck = await mobilePage.evaluate(() => {
      return {
        width: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
      }
    })
    expect(viewportCheck.scrollWidth).toBeLessThanOrEqual(viewportCheck.width + 2)
  } finally {
    await closeTrackedContexts(contextRegistry)
  }
})
