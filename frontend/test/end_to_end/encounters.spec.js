import { expect, test } from '@playwright/test'
import { assertConversationAudioRoundtrip, installWebSocketProbe } from './helpers/audioProbe.js'
import { assertReturnedToReadyState, runSpeakStopLifecycle } from './helpers/audioLifecycle.js'

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
const getEncounterNodeByName = (page, encounterName) =>
  getEncounterNodeContainerByName(page, encounterName).locator('.encounter-node').first()

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

const saveCanvasAndAssertSuccess = async (page) => {
  const saveResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/canvas') && response.request().method() === 'POST'
  })
  await page.locator('.save-canvas-btn').click()
  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
}

const openPlayerDropdown = async (encounterNode) => {
  await encounterNode.locator('.add-player-btn').click()
  const dropdown = encounterNode.locator('.player-dropdown')
  await expect(dropdown).toBeVisible()
  return dropdown
}

const openCharacterDropdown = async (encounterNode) => {
  await encounterNode.locator('.add-character-btn').click()
  const dropdown = encounterNode.locator('.character-dropdown')
  await expect(dropdown).toBeVisible()
  return dropdown
}

const getOptionName = async (optionLocator) => {
  return (await optionLocator.locator('.option-name').first().innerText()).trim()
}

const ensureDescriptionDisplayVisible = async (encounterNode) => {
  let descriptionDisplay = encounterNode.locator('.encounter-description-display')
  if ((await descriptionDisplay.count()) === 0) {
    await encounterNode.locator('.info-btn').first().click()
    descriptionDisplay = encounterNode.locator('.encounter-description-display')
  }
  await expect(descriptionDisplay).toBeVisible()
  return descriptionDisplay
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

test('ENCOUNTERS-ASSIGN-PLAYER-01 adds/removes player and persists after save/reload', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNode(page)
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const playerDropdown = await openPlayerDropdown(encounterNode)
  const playerOptions = playerDropdown.locator('.character-option')
  const optionCount = await playerOptions.count()
  if (optionCount === 0) {
    throw new Error('No addable player options available for selected encounter.')
  }

  const selectedPlayerOption = playerOptions.first()
  const addedPlayerName = await getOptionName(selectedPlayerOption)
  await selectedPlayerOption.click()

  const addedPlayerChip = encounterNode.locator(
    '.players-section .player-chip:not(.add-player-chip)',
    { hasText: addedPlayerName }
  )
  await expect(addedPlayerChip).toBeVisible()

  await saveCanvasAndAssertSuccess(page)
  await page.reload()
  await waitForEncountersGet(page)

  const reloadedEncounterNode = getEncounterNodeByName(page, encounterName)
  await expect(reloadedEncounterNode).toBeVisible()

  const reloadedAddedPlayerChip = reloadedEncounterNode.locator(
    '.players-section .player-chip:not(.add-player-chip)',
    { hasText: addedPlayerName }
  )
  await expect(reloadedAddedPlayerChip).toBeVisible()

  await reloadedAddedPlayerChip.locator('.remove-character-btn').click()
  await expect(reloadedAddedPlayerChip).toHaveCount(0)

  await saveCanvasAndAssertSuccess(page)
  await page.reload()
  await waitForEncountersGet(page)

  const postRemoveEncounterNode = getEncounterNodeByName(page, encounterName)
  const postRemovePlayerChip = postRemoveEncounterNode.locator(
    '.players-section .player-chip:not(.add-player-chip)',
    { hasText: addedPlayerName }
  )
  await expect(postRemovePlayerChip).toHaveCount(0)
})

test('ENCOUNTERS-ASSIGN-CHARACTER-01 adds/removes character and persists after save/reload', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNode(page)
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const characterDropdown = await openCharacterDropdown(encounterNode)
  const characterOptions = characterDropdown.locator('.character-option')
  const optionCount = await characterOptions.count()
  if (optionCount === 0) {
    throw new Error('No addable character options available for selected encounter.')
  }

  const selectedCharacterOption = characterOptions.first()
  const addedCharacterName = await getOptionName(selectedCharacterOption)
  await selectedCharacterOption.evaluate((element) => element.click())

  const addedCharacterTile = encounterNode.locator(
    '.characters-section .character-avatar:not(.add-character-tile)',
    { hasText: addedCharacterName }
  )
  await expect(addedCharacterTile).toBeVisible()

  await saveCanvasAndAssertSuccess(page)
  await page.reload()
  await waitForEncountersGet(page)

  const reloadedEncounterNode = getEncounterNodeByName(page, encounterName)
  await expect(reloadedEncounterNode).toBeVisible()

  const reloadedAddedCharacterTile = reloadedEncounterNode.locator(
    '.characters-section .character-avatar:not(.add-character-tile)',
    { hasText: addedCharacterName }
  )
  await expect(reloadedAddedCharacterTile).toBeVisible()

  await reloadedAddedCharacterTile.locator('.remove-character-btn').click()
  await expect(reloadedAddedCharacterTile).toHaveCount(0)

  await saveCanvasAndAssertSuccess(page)
  await page.reload()
  await waitForEncountersGet(page)

  const postRemoveEncounterNode = getEncounterNodeByName(page, encounterName)
  const postRemoveCharacterTile = postRemoveEncounterNode.locator(
    '.characters-section .character-avatar:not(.add-character-tile)',
    { hasText: addedCharacterName }
  )
  await expect(postRemoveCharacterTile).toHaveCount(0)
})

test('ENCOUNTERS-DESCRIPTION-EDIT-01 edits description and persists after save/reload', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNode(page)
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const infoButton = encounterNode.locator('.info-btn').first()
  await infoButton.click()
  const descriptionDisplay = await ensureDescriptionDisplayVisible(encounterNode)

  const baselineDescription = (await descriptionDisplay.innerText()).trim()
  const newDescription = `Encounter description e2e ${Date.now()}`

  await descriptionDisplay.click()
  const descriptionTextarea = encounterNode.locator('.encounter-description-input .shared-textarea')
  await expect(descriptionTextarea).toBeVisible()
  await descriptionTextarea.fill(newDescription)
  await descriptionTextarea.press('Control+Enter')
  const updatedDescriptionDisplay = await ensureDescriptionDisplayVisible(encounterNode)
  await expect(updatedDescriptionDisplay).toContainText(newDescription)

  await saveCanvasAndAssertSuccess(page)
  await page.reload()
  await waitForEncountersGet(page)

  const reloadedEncounterNode = getEncounterNodeByName(page, encounterName)
  await expect(reloadedEncounterNode).toBeVisible()
  const reloadedInfoButton = reloadedEncounterNode.locator('.info-btn').first()
  await reloadedInfoButton.click()
  const reloadedDescriptionDisplay = await ensureDescriptionDisplayVisible(reloadedEncounterNode)
  await expect(reloadedDescriptionDisplay).toContainText(newDescription)

  // Cleanup to reduce drift between test runs.
  await reloadedDescriptionDisplay.click()
  const cleanupTextarea = reloadedEncounterNode.locator(
    '.encounter-description-input .shared-textarea'
  )
  await expect(cleanupTextarea).toBeVisible()
  const restoreDescription =
    baselineDescription === 'No description available. Click to add one.' ? '' : baselineDescription
  await cleanupTextarea.fill(restoreDescription)
  await cleanupTextarea.press('Control+Enter')
  await saveCanvasAndAssertSuccess(page)
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

  await runSpeakStopLifecycle(page, { clickWithEvaluate: true })
  await assertConversationAudioRoundtrip(page, {
    wsPathRegex: /\/api\/encounters\/\d+\/conversation\/\d+\/\d+/,
    timeoutMs: 60_000,
  })
  await assertReturnedToReadyState(page, {
    readyTextPattern: /Click Speak/,
    timeoutMs: 60_000,
  })
})
