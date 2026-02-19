import { expect, test } from '@playwright/test'

const waitForEncountersGet = async (page) => {
  const encountersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/canvas') && response.request().method() === 'GET'
  })
  const response = await encountersResponsePromise
  expect(response.status()).toBe(200)
}

const getFirstEncounterNode = (page) => page.locator('.encounter-node').first()
const getEncounterNodes = (page) => page.locator('.encounter-node')
const getEncounterNodeContainerByName = (page, encounterName) =>
  page.locator('.vue-flow__node', {
    has: page.locator('.encounter-name', { hasText: encounterName }),
  })

const getEncounterCharacterTile = (encounterNode) =>
  encounterNode.locator('.characters-section .character-avatar:not(.add-character-tile)').first()

const getFirstInViewportEncounterNode = async (page) => {
  const nodes = getEncounterNodes(page)
  const nodeCount = await nodes.count()
  expect(nodeCount).toBeGreaterThan(0)

  const viewport = page.viewportSize()
  expect(viewport).not.toBeNull()

  for (let index = 0; index < nodeCount; index++) {
    const node = nodes.nth(index)
    const box = await node.boundingBox()
    if (!box) continue

    const isWithinViewport =
      box.x >= 0 &&
      box.y >= 60 &&
      box.x + box.width <= viewport.width &&
      box.y + box.height <= viewport.height

    if (isWithinViewport) {
      return node
    }
  }

  return nodes.first()
}

const getFirstInViewportEncounterNodeWithCharacter = async (page) => {
  const nodes = getEncounterNodes(page)
  const nodeCount = await nodes.count()
  expect(nodeCount).toBeGreaterThan(0)

  const viewport = page.viewportSize()
  expect(viewport).not.toBeNull()

  for (let index = 0; index < nodeCount; index++) {
    const node = nodes.nth(index)
    const box = await node.boundingBox()
    if (!box) continue

    const isWithinViewport =
      box.x >= 0 &&
      box.y >= 60 &&
      box.x + box.width <= viewport.width &&
      box.y + box.height <= viewport.height
    if (!isWithinViewport) continue

    const characterTileCount = await node
      .locator('.characters-section .character-avatar:not(.add-character-tile)')
      .count()
    if (characterTileCount > 0) {
      return node
    }
  }

  for (let index = 0; index < nodeCount; index++) {
    const node = nodes.nth(index)
    const characterTileCount = await node
      .locator('.characters-section .character-avatar:not(.add-character-tile)')
      .count()
    if (characterTileCount > 0) {
      return node
    }
  }

  return nodes.first()
}

const installWebSocketProbe = async (page) => {
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
        const urlAsString = String(url)
        window.__wsProbe.wsUrls.push(urlAsString)
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

test('ENCOUNTERS-VIEW-NAV-01 opens encounter popup, navigates to character/reveal pages, and returns to same encounter', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNodeWithCharacter(page)
  await expect(encounterNode).toBeVisible()

  const firstCharacterTile = getEncounterCharacterTile(encounterNode)
  await expect(firstCharacterTile).toBeVisible()
  await firstCharacterTile.evaluate((element) => element.click())

  await expect(page.locator('.encounter-popup-overlay')).toBeVisible()
  await expect(page.locator('.encounter-popup')).toBeVisible()

  const encounterId = page.url().match(/[?&]encounterId=([^&]+)/)?.[1]
  const characterId = page.url().match(/[?&]characterId=([^&]+)/)?.[1]
  expect(encounterId).toBeTruthy()
  expect(characterId).toBeTruthy()
  await expect(page).toHaveURL(/popup=encounter/)

  await page.locator('.character-name-link').first().click()
  await expect(page).toHaveURL(/\/characters\?id=\d+/)
  await expect(page.locator('.shared-title')).toBeVisible()

  await page.goBack()
  await expect(page).toHaveURL(/\/encounters/)
  await expect(page).toHaveURL(/popup=encounter/)
  await expect(page).toHaveURL(new RegExp(`encounterId=${encounterId}`))
  await expect(page).toHaveURL(new RegExp(`characterId=${characterId}`))
  await expect(page.locator('.encounter-popup')).toBeVisible()

  const playerSelect = page.locator('#player-select')
  await expect(playerSelect).toBeVisible()
  const playerOptionValues = await playerSelect
    .locator('option')
    .evaluateAll((options) =>
      options.map((option) => option.value).filter((value) => value && value !== 'Select a player')
    )
  expect(playerOptionValues.length).toBeGreaterThan(0)

  const conversationResponsePromise = page.waitForResponse((response) => {
    return (
      /\/api\/encounters\/\d+\/conversation\/\d+\/\d+$/.test(response.url()) &&
      response.request().method() === 'GET'
    )
  })
  await playerSelect.selectOption(playerOptionValues[0])
  const conversationResponse = await conversationResponsePromise
  expect(conversationResponse.status()).toBe(200)

  const revealItems = page.locator('.reveal-item.reveal-clickable')
  await expect(revealItems.first()).toBeVisible()
  await revealItems.first().click()
  await expect(page).toHaveURL(/\/reveals\?id=\d+/)
  await expect(page.locator('.shared-title')).toBeVisible()

  await page.goBack()
  await expect(page).toHaveURL(/\/encounters/)
  await expect(page).toHaveURL(/popup=encounter/)
  await expect(page).toHaveURL(new RegExp(`encounterId=${encounterId}`))
  await expect(page).toHaveURL(new RegExp(`characterId=${characterId}`))
  await expect(page.locator('.encounter-popup')).toBeVisible()
})

test('ENCOUNTERS-VIEW-DESCRIPTION-01 toggles encounter description open and closed', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNode(page)
  await expect(encounterNode).toBeVisible()

  const descriptionSection = encounterNode.locator('.encounter-description-section')
  await expect(descriptionSection).toHaveCount(0)

  const infoButton = encounterNode.locator('.info-btn').first()
  await infoButton.evaluate((element) => element.click())
  await expect(descriptionSection).toBeVisible()
  await expect(encounterNode.locator('.encounter-description-display')).toBeVisible()

  await infoButton.evaluate((element) => element.click())
  await expect(descriptionSection).toHaveCount(0)

  await infoButton.evaluate((element) => element.click())
  await expect(descriptionSection).toBeVisible()
  await page.locator('.encounter-canvas').click({ position: { x: 10, y: 10 } })
  await expect(descriptionSection).toHaveCount(0)
})

test('ENCOUNTERS-SAVE-CANVAS-01 saves canvas and returns success status', async ({ page }) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  await expect(getFirstEncounterNode(page)).toBeVisible()

  const saveResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/canvas') && response.request().method() === 'POST'
  })
  await page.locator('.save-canvas-btn').click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
})

test('ENCOUNTERS-TALKING-AUDIO-01 returns audio over websocket and completes processing', async ({
  page,
}) => {
  test.skip(
    process.env.ENCOUNTERS_AUDIO_TEST !== '1',
    'Audio talking test runs only in dedicated encounters audio command.'
  )
  test.setTimeout(90_000)
  await installWebSocketProbe(page)

  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNodeWithCharacter(page)
  await expect(encounterNode).toBeVisible()

  const firstCharacterTile = getEncounterCharacterTile(encounterNode)
  await expect(firstCharacterTile).toBeVisible()
  await firstCharacterTile.evaluate((element) => element.click())

  await expect(page.locator('.encounter-popup-overlay')).toBeVisible()
  await expect(page.locator('.encounter-popup')).toBeVisible()

  const playerSelect = page.locator('#player-select')
  await expect(playerSelect).toBeVisible()
  const playerOptionValues = await playerSelect
    .locator('option')
    .evaluateAll((options) =>
      options.map((option) => option.value).filter((value) => value && value !== 'Select a player')
    )
  test.skip(
    playerOptionValues.length === 0,
    'Skipping: selected encounter has no assigned players.'
  )

  await playerSelect.selectOption(playerOptionValues[0])

  const speakButton = page.getByRole('button', { name: 'Speak' })
  await expect(speakButton).toBeEnabled()
  await speakButton.evaluate((element) => element.click())

  await expect(page.getByRole('button', { name: 'Stop' })).toBeVisible()
  await expect(page.locator('.shared-status-text')).toContainText('Listening')
  await page.waitForTimeout(1200)

  await page.getByRole('button', { name: 'Stop' }).evaluate((element) => element.click())
  await expect(page.locator('.shared-status-text')).toContainText('Processing')

  await expect
    .poll(
      async () => {
        const probe = await page.evaluate(() => ({
          wsUrls: window.__wsProbe?.wsUrls || [],
          outboundMessages: window.__wsProbe?.outboundMessages || [],
          inboundBlobCount: window.__wsProbe?.inboundBlobCount || 0,
          inboundTextMessages: window.__wsProbe?.inboundTextMessages || [],
        }))

        const audioReturned = probe.inboundBlobCount > 0
        const completed = probe.inboundTextMessages.includes('AUDIO_COMPLETE')
        return audioReturned && completed
      },
      { timeout: 60_000 }
    )
    .toBe(true)

  await expect(page.getByRole('button', { name: 'Speak' })).toBeVisible({ timeout: 60_000 })
  await expect(page.locator('.shared-status-text')).toContainText('Click Speak', {
    timeout: 60_000,
  })
})
