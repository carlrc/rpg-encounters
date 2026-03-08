import { devices, expect, test } from '@playwright/test'
import { resolveBaseUrl } from './helpers/baseUrl'
import { applyDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'
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
    await expect(mobilePage.getByRole('button', { name: 'Profile' })).toHaveCount(0)
  }

  return { mobileContext, mobilePage, encounterStatus }
}

const getLoginForPlayerWithEncounter = async (page, browser, testInfo, contextRegistry) => {
  const fixture = await resolveSeededPlayerEncounterFixture(page, testInfo)
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

let dmSession: DmSession

test.beforeAll(async ({}, testInfo) => {
  dmSession = getSpecDmSession(testInfo)
})

test.beforeEach(async ({ page }) => {
  await applyDmSession(page, dmSession)
})

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

test('PLAYER-MOBILE-CHALLENGE-SKILL-PICKER-01 challenge skill picker opens, selects, and clears on mobile', async ({
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

    await mobilePage.locator('.character-tile').first().click()
    await expect(mobilePage.locator('.interaction-panel')).toBeVisible()

    const challengeButton = mobilePage.getByRole('button', { name: 'Challenge' })
    await challengeButton.click()

    const speakButton = mobilePage.getByRole('button', { name: 'Speak' })
    await expect(speakButton).toBeDisabled()

    const skillTrigger = mobilePage.locator('.mobile-skill-trigger')
    await expect(skillTrigger).toBeVisible()
    await expect(skillTrigger).toContainText('Select a skill')
    await expect(skillTrigger).toHaveAttribute('aria-expanded', 'false')

    await skillTrigger.click()
    await expect(skillTrigger).toHaveAttribute('aria-expanded', 'true')
    const mobileSkillList = mobilePage.locator('.mobile-skill-list')
    await expect(mobileSkillList).toBeVisible()
    await expect(
      mobileSkillList.getByRole('button', { name: 'Select a skill', exact: true })
    ).toBeVisible()
    await expect(
      mobileSkillList.getByRole('button', { name: 'Deception', exact: true })
    ).toBeVisible()

    await mobileSkillList.getByRole('button', { name: 'Deception', exact: true }).click()
    await expect(mobilePage.locator('.mobile-skill-list')).toHaveCount(0)
    await expect(skillTrigger).toContainText('Deception')
    await expect(skillTrigger).toHaveAttribute('aria-expanded', 'false')
    await expect(speakButton).toBeEnabled()

    await skillTrigger.click()
    await mobilePage
      .locator('.mobile-skill-list')
      .getByRole('button', { name: 'Select a skill', exact: true })
      .click()
    await expect(mobilePage.locator('.mobile-skill-list')).toHaveCount(0)
    await expect(skillTrigger).toContainText('Select a skill')
    await expect(speakButton).toBeDisabled()
  } finally {
    await closeTrackedContexts(contextRegistry)
  }
})
