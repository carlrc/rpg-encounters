import { expect } from '@playwright/test'

import { toAbsoluteUrl } from './baseUrl.js'

const clickWhenActionable = async (locator) => {
  await expect(locator).toBeVisible()
  await expect(locator).toBeEnabled()
  await locator.click()
}

const pickDeterministicFixture = (players, encounters) => {
  const sortedPlayers = [...players]
    .map((player) => ({
      id: Number(player?.id),
      name: typeof player?.name === 'string' ? player.name : '',
      rlName: typeof player?.rl_name === 'string' ? player.rl_name : '',
    }))
    .filter((player) => Number.isFinite(player.id))
    .sort((a, b) => a.id - b.id)

  const encounterByPlayerId = new Map()
  for (const encounter of encounters) {
    const encounterId = Number(encounter?.id)
    const playerIds = Array.isArray(encounter?.player_ids) ? encounter.player_ids : []
    const characterIds = Array.isArray(encounter?.character_ids) ? encounter.character_ids : []
    if (!Number.isFinite(encounterId) || characterIds.length < 1) {
      continue
    }
    const characterId = Number(characterIds[0])
    if (!Number.isFinite(characterId)) {
      continue
    }

    for (const rawPlayerId of playerIds) {
      const playerId = Number(rawPlayerId)
      if (Number.isFinite(playerId)) {
        encounterByPlayerId.set(playerId, { encounterId, characterId })
      }
    }
  }

  for (const player of sortedPlayers) {
    const fixture = encounterByPlayerId.get(player.id)
    if (fixture) {
      return {
        playerId: player.id,
        playerName: player.name,
        playerRlName: player.rlName,
        encounterId: fixture.encounterId,
        characterId: fixture.characterId,
      }
    }
  }

  return null
}

const loadPlayersViaUi = async (page) => {
  const playersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })
  await page.goto('/players')
  const playersResponse = await playersResponsePromise
  if (playersResponse.status() !== 200) {
    throw new Error(`Failed to load seeded players. Status: ${playersResponse.status()}`)
  }
  return await playersResponse.json()
}

const loadEncountersViaUi = async (page) => {
  const canvasResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/canvas') && response.request().method() === 'GET'
  })
  await page.goto('/encounters')
  const canvasResponse = await canvasResponsePromise
  if (canvasResponse.status() !== 200) {
    throw new Error(`Failed to load seeded encounters. Status: ${canvasResponse.status()}`)
  }
  const canvasPayload = await canvasResponse.json()
  return Array.isArray(canvasPayload?.encounters) ? canvasPayload.encounters : []
}

export const resolveSeededPlayerEncounterFixture = async (page, browser, testInfo) => {
  if (!browser || !testInfo) {
    throw new Error('resolveSeededPlayerEncounterFixture requires browser and testInfo.')
  }

  const players = await loadPlayersViaUi(page)
  if (!Array.isArray(players) || players.length < 1) {
    throw new Error('No seeded players available for deterministic fixture resolution.')
  }

  const encounters = await loadEncountersViaUi(page)

  const fixture = pickDeterministicFixture(players, encounters)
  if (!fixture) {
    throw new Error(
      'No deterministic player fixture found with an encounter that has at least one character.'
    )
  }

  const loginUrl = await generatePlayerLoginLinkForPlayer(
    page,
    testInfo,
    fixture.playerId,
    fixture.playerRlName || fixture.playerName
  )
  return {
    encounterId: fixture.encounterId,
    playerId: fixture.playerId,
    characterId: fixture.characterId,
    loginUrl,
  }
}

export const generatePlayerLoginLinkForPlayer = async (
  page,
  testInfo,
  playerId,
  playerDisplayName,
  retries = 3
) => {
  await page.goto('/players')
  const playerListItem = page
    .locator('.list-content .list-item')
    .filter({ hasText: playerDisplayName })
    .first()
  await clickWhenActionable(playerListItem)

  const generateButton = page.getByTitle('Generate new login link')
  let response
  for (let attempt = 0; attempt < retries; attempt++) {
    const generateResponsePromise = page.waitForResponse((candidate) => {
      return (
        candidate.url().endsWith(`/api/players/${playerId}/login`) &&
        candidate.request().method() === 'POST'
      )
    })
    await clickWhenActionable(generateButton)
    response = await generateResponsePromise
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
