import { devices, expect, test } from '@playwright/test'

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

const loginAsPlayerOnMobile = async (browser, loginUrl, playerId) => {
  const mobileContext = await browser.newContext({
    ...devices['iPhone 12'],
    storageState: undefined,
    baseURL: MOBILE_BASE_URL,
  })
  const mobilePage = await mobileContext.newPage()

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

  await expect(mobilePage).toHaveURL(new RegExp(`/players/${playerId}/encounter$`))

  return { mobileContext, mobilePage }
}

test('PLAYER-LOGIN-MOBILE-01 generates player login link (DM) and consumes it on iPhone 12', async ({
  page,
  browser,
}) => {
  const { loginUrl, playerId } = await generatePlayerLoginLinkFromDmView(page)

  const { mobileContext } = await loginAsPlayerOnMobile(browser, loginUrl, playerId)
  await mobileContext.close()
})

test('PLAYER-MOBILE-VIEW-01 player encounter content renders and basic tap flow works on iPhone 12', async ({
  page,
  browser,
}) => {
  const { loginUrl, playerId } = await generatePlayerLoginLinkFromDmView(page)
  const { mobileContext, mobilePage } = await loginAsPlayerOnMobile(browser, loginUrl, playerId)

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

  await mobileContext.close()
})
