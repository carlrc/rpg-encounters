import { expect } from '@playwright/test'

import { resolveBaseUrl, toAbsoluteUrl } from './baseUrl.js'

const clickWhenActionable = async (locator) => {
  await expect(locator).toBeVisible()
  await expect(locator).toBeEnabled()
  try {
    await locator.click({ timeout: 2_000 })
  } catch {
    await locator.evaluate((element) => element.click())
  }
}

const waitForPlayersPage = async (page) => {
  const playersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })
  await page.goto('/players')
  const response = await playersResponsePromise
  expect(response.status()).toBe(200)
}

const generatePlayerLoginByIndex = async (page, playerIndex, testInfo) => {
  const playerListItems = page.locator('.list-content .list-item')
  const playerCount = await playerListItems.count()
  if (playerIndex < 0 || playerIndex >= playerCount) {
    return null
  }

  await clickWhenActionable(playerListItems.nth(playerIndex))

  const generateResponsePromise = page.waitForResponse((response) => {
    return (
      /\/api\/players\/\d+\/login$/.test(response.url()) && response.request().method() === 'POST'
    )
  })
  await clickWhenActionable(page.getByTitle('Generate new login link'))
  const generateResponse = await generateResponsePromise
  if (generateResponse.status() !== 200) {
    return null
  }

  const payload = await generateResponse.json()
  const loginUrl = toAbsoluteUrl(payload?.login_url || '', testInfo)
  const playerId = Number(generateResponse.url().match(/\/api\/players\/(\d+)\/login$/)?.[1])
  if (!Number.isFinite(playerId)) {
    return null
  }

  return { loginUrl, playerId, playerCount }
}

const probeEncounterForPlayer = async (browser, testInfo, playerId, loginUrl) => {
  const probeContext = await browser.newContext({
    storageState: undefined,
    baseURL: resolveBaseUrl(testInfo),
  })
  const probePage = await probeContext.newPage()
  try {
    const consumePromise = probePage.waitForResponse((response) => {
      return (
        new RegExp(`/api/players/${playerId}/login\\?token=`).test(response.url()) &&
        response.request().method() === 'GET'
      )
    })
    const encounterPromise = probePage.waitForResponse((response) => {
      return (
        response.url().endsWith(`/api/players/${playerId}/encounter`) &&
        response.request().method() === 'GET'
      )
    })

    await probePage.goto(loginUrl)
    const consumeResponse = await consumePromise
    if (consumeResponse.status() !== 200) {
      return null
    }

    const encounterResponse = await encounterPromise
    if (encounterResponse.status() !== 200) {
      return null
    }

    const encounterPayload = await encounterResponse.json()
    const encounterId = Number(encounterPayload?.id)
    const characterId = Number(encounterPayload?.characters?.[0]?.id)
    if (!Number.isFinite(encounterId) || !Number.isFinite(characterId)) {
      return null
    }

    return { encounterId, characterId }
  } catch {
    return null
  } finally {
    await probeContext.close()
  }
}

export const resolveSeededPlayerEncounterFixture = async (page, browser, testInfo) => {
  if (!browser || !testInfo) {
    throw new Error('resolveSeededPlayerEncounterFixture requires browser and testInfo.')
  }

  await waitForPlayersPage(page)
  const firstResult = await generatePlayerLoginByIndex(page, 0, testInfo)
  if (!firstResult?.playerCount) {
    throw new Error('No players available for deterministic fixture resolution.')
  }

  for (let index = 0; index < firstResult.playerCount; index++) {
    const candidate =
      index === 0 ? firstResult : await generatePlayerLoginByIndex(page, index, testInfo)
    if (!candidate) {
      continue
    }

    const encounterFixture = await probeEncounterForPlayer(
      browser,
      testInfo,
      candidate.playerId,
      candidate.loginUrl
    )
    if (!encounterFixture) {
      continue
    }

    const freshLogin = await generatePlayerLoginByIndex(page, index, testInfo)
    if (!freshLogin) {
      continue
    }

    return {
      encounterId: encounterFixture.encounterId,
      playerId: freshLogin.playerId,
      characterId: encounterFixture.characterId,
      loginUrl: freshLogin.loginUrl,
    }
  }

  throw new Error('No player login produced an active encounter with at least one character.')
}

export const generatePlayerLoginLinkForPlayer = async (page, testInfo, playerId, retries = 3) => {
  let response
  for (let attempt = 0; attempt < retries; attempt++) {
    response = await page.request.post(`/api/players/${playerId}/login`)
    if (response.status() !== 429) {
      break
    }
    await page.waitForTimeout(500)
  }

  if (response.status() !== 200) {
    throw new Error(
      `Failed to generate login link for player ${playerId}. Status: ${response.status()}`
    )
  }
  const payload = await response.json()
  expect(typeof payload.login_url).toBe('string')
  expect(payload.login_url.length).toBeGreaterThan(0)
  expect(payload.login_url).toMatch(/\/players\/\d+\/login\?token=/)

  return toAbsoluteUrl(payload.login_url, testInfo)
}
