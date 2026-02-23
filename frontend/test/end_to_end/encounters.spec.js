import { expect, test } from '@playwright/test'
import { assertConversationAudioRoundtrip, installWebSocketProbe } from './helpers/audioProbe.js'
import { assertReturnedToReadyState, runSpeakStopLifecycle } from './helpers/audioLifecycle.js'
import { makeScopedSuffix } from './helpers/entityNaming.js'

test.describe.configure({ mode: 'serial' })

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
const getEncounterNodeById = (page, encounterId) =>
  page.locator(`.vue-flow__node[data-id="${encounterId}"] .encounter-node`).first()

const getEncounterCharacterTile = (encounterNode) =>
  encounterNode.locator('.characters-section .character-avatar:not(.add-character-tile)').first()
const CLEAN_NAME_REGEX = /^[\p{L}\p{N}\s'-]+$/u
const CLEAN_INITIALS_REGEX = /^[\p{L}\p{N}]{1,2}$/u

const MUTABLE_ENCOUNTERS = [
  "The Captain's Quarters",
  'The Lower Deck',
  'The Crew Quarters',
  'The Main Deck',
  'The Upper Deck',
]

const getProjectHash = (testInfo) => {
  const projectName = testInfo?.project?.name || 'default'
  return [...projectName].reduce((hash, char) => hash + char.charCodeAt(0), 0)
}

const getProjectScopedEncounterName = (testInfo, offset = 0) => {
  const index = (getProjectHash(testInfo) + offset) % MUTABLE_ENCOUNTERS.length
  return MUTABLE_ENCOUNTERS[index]
}

const clickWhenActionable = async (locator) => {
  await expect(locator).toBeVisible()
  await expect(locator).toBeEnabled()
  try {
    await locator.click({ timeout: 2_000 })
  } catch {
    // Vue Flow keeps some controls visually visible but outside Playwright's clickable viewport.
    await locator.evaluate((element) => element.click())
  }
}

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
  for (let attempt = 0; attempt < 2; attempt++) {
    const saveResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/canvas') && response.request().method() === 'POST'
    })
    await page.locator('.save-canvas-btn').click()
    const saveResponse = await saveResponsePromise
    if (saveResponse.status() === 200) {
      return
    }
    if (attempt === 1) {
      expect(saveResponse.status()).toBe(200)
    }
    await page.waitForTimeout(300)
  }
}

const openPlayerDropdown = async (encounterNode) => {
  await clickWhenActionable(encounterNode.locator('.add-player-btn'))
  const dropdown = encounterNode.locator('.player-dropdown')
  await expect(dropdown).toBeVisible()
  return dropdown
}

const openCharacterDropdown = async (encounterNode) => {
  await clickWhenActionable(encounterNode.locator('.add-character-btn'))
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

const findEncounterNodeWithCharacterAndPlayerOptions = async (page) => {
  const nodes = getEncounterNodes(page)
  const nodeCount = await nodes.count()
  expect(nodeCount).toBeGreaterThan(0)

  for (let index = 0; index < nodeCount; index++) {
    const encounterNode = nodes.nth(index)
    const characterTile = getEncounterCharacterTile(encounterNode)
    if ((await characterTile.count()) === 0) {
      continue
    }

    await clickWhenActionable(characterTile)
    await expect(page.locator('.encounter-popup')).toBeVisible()
    const playerOptions = await page
      .locator('#player-select option')
      .evaluateAll((options) =>
        options
          .map((option) => option.value)
          .filter((value) => value && value !== 'Select a player')
      )
    if (playerOptions.length > 0) {
      return { encounterNode, firstPlayerOption: playerOptions[0] }
    }

    await page.locator('.close-button').click()
    await expect(page.locator('.encounter-popup')).toHaveCount(0)
  }

  throw new Error('No encounter popup had both a character tile and selectable players.')
}

test('ENCOUNTERS-VIEW-NAV-01 opens encounter popup, navigates to character/reveal pages, and returns to same encounter', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const { encounterNode, firstPlayerOption } =
    await findEncounterNodeWithCharacterAndPlayerOptions(page)

  const characterTiles = encounterNode.locator(
    '.characters-section .character-avatar:not(.add-character-tile)'
  )
  const characterTileCount = await characterTiles.count()
  expect(characterTileCount).toBeGreaterThan(0)

  let encounterId
  let characterId
  let foundRevealConversation = false

  for (let index = 0; index < characterTileCount; index++) {
    await clickWhenActionable(characterTiles.nth(index))
    await expect(page.locator('.encounter-popup-overlay')).toBeVisible()
    await expect(page.locator('.encounter-popup')).toBeVisible()

    encounterId = page.url().match(/[?&]encounterId=([^&]+)/)?.[1]
    characterId = page.url().match(/[?&]characterId=([^&]+)/)?.[1]
    expect(encounterId).toBeTruthy()
    expect(characterId).toBeTruthy()

    const playerSelect = page.locator('#player-select')
    await expect(playerSelect).toBeVisible()
    const conversationResponsePromise = page.waitForResponse((response) => {
      return (
        /\/api\/encounters\/\d+\/conversation\/\d+\/\d+$/.test(response.url()) &&
        response.request().method() === 'GET'
      )
    })
    await playerSelect.selectOption(firstPlayerOption)
    const conversationResponse = await conversationResponsePromise
    expect(conversationResponse.status()).toBe(200)

    const conversationPayload = await conversationResponse.json()
    const reveals = Array.isArray(conversationPayload?.reveals) ? conversationPayload.reveals : []
    if (reveals.length > 0) {
      foundRevealConversation = true
      break
    }

    await page.locator('.close-button').click()
    await expect(page.locator('.encounter-popup')).toHaveCount(0)
  }

  if (!/popup=encounter/.test(page.url())) {
    await clickWhenActionable(characterTiles.first())
    await expect(page.locator('.encounter-popup')).toBeVisible()
    encounterId = page.url().match(/[?&]encounterId=([^&]+)/)?.[1]
    characterId = page.url().match(/[?&]characterId=([^&]+)/)?.[1]
  }
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

  const revealItems = page.locator('.reveal-item.reveal-clickable')
  let usedPopupRevealNavigation = false
  if (foundRevealConversation && (await revealItems.count()) > 0) {
    await revealItems.first().click()
    usedPopupRevealNavigation = true
  } else {
    await page.locator('.close-button').click()
    await expect(page.locator('.encounter-popup')).toHaveCount(0)
    await page.getByRole('link', { name: 'Reveals' }).click()
  }
  await expect(page).toHaveURL(/\/reveals/)
  await expect(page.locator('.list-content')).toBeVisible()

  await page.goBack()
  await expect(page).toHaveURL(/\/encounters/)
  if (usedPopupRevealNavigation) {
    await expect(page).toHaveURL(/popup=encounter/)
    await expect(page).toHaveURL(new RegExp(`encounterId=${encounterId}`))
    await expect(page).toHaveURL(new RegExp(`characterId=${characterId}`))
    await expect(page.locator('.encounter-popup')).toBeVisible()
  } else {
    await clickWhenActionable(getEncounterCharacterTile(encounterNode))
    await expect(page.locator('.encounter-popup')).toBeVisible()
  }
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
  await clickWhenActionable(infoButton)
  await expect(descriptionSection).toBeVisible()
  await expect(encounterNode.locator('.encounter-description-display')).toBeVisible()

  await clickWhenActionable(infoButton)
  await expect(descriptionSection).toHaveCount(0)

  await clickWhenActionable(infoButton)
  await expect(descriptionSection).toBeVisible()
  await page.locator('.encounter-canvas').click({ position: { x: 10, y: 10 } })
  await expect(descriptionSection).toHaveCount(0)
})

test('ENCOUNTERS-NAMES-01 character names and initials render without symbols', async ({
  page,
}) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)

  const encounterNode = await getFirstInViewportEncounterNodeWithCharacter(page)
  await expect(encounterNode).toBeVisible()

  const characterTiles = encounterNode.locator(
    '.characters-section .character-avatar:not(.add-character-tile)'
  )
  const characterTileCount = await characterTiles.count()
  expect(characterTileCount).toBeGreaterThan(0)

  for (let index = 0; index < characterTileCount; index++) {
    const tile = characterTiles.nth(index)
    const nameText = (await tile.locator('.character-info .character-name').innerText()).trim()
    expect(nameText).toMatch(CLEAN_NAME_REGEX)

    const initials = tile.locator('.avatar-placeholder .avatar-initials')
    if ((await initials.count()) > 0) {
      const initialsText = (await initials.first().innerText()).trim()
      expect(initialsText).toMatch(CLEAN_INITIALS_REGEX)
    }
  }
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
}, testInfo) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = getEncounterNodeByName(page, getProjectScopedEncounterName(testInfo, 0))
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const playerDropdown = await openPlayerDropdown(encounterNode)
  const playerOptions = playerDropdown.locator('.character-option')
  const optionCount = await playerOptions.count()
  expect(optionCount).toBeGreaterThan(0)

  const selectedPlayerOption = playerOptions.nth(getProjectHash(testInfo) % optionCount)
  const addedPlayerName = await getOptionName(selectedPlayerOption)
  await clickWhenActionable(selectedPlayerOption)

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

  await clickWhenActionable(reloadedAddedPlayerChip.locator('.remove-character-btn'))
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
}, testInfo) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = getEncounterNodeByName(page, getProjectScopedEncounterName(testInfo, 1))
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const characterDropdown = await openCharacterDropdown(encounterNode)
  const characterOptions = characterDropdown.locator('.character-option')
  const optionCount = await characterOptions.count()
  expect(optionCount).toBeGreaterThan(0)

  const selectedCharacterOption = characterOptions.nth(getProjectHash(testInfo) % optionCount)
  const addedCharacterName = await getOptionName(selectedCharacterOption)
  await clickWhenActionable(selectedCharacterOption)

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

  await clickWhenActionable(reloadedAddedCharacterTile.locator('.remove-character-btn'))
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
}, testInfo) => {
  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const encounterNode = await getFirstInViewportEncounterNode(page)
  await expect(encounterNode).toBeVisible()
  const encounterName = (await encounterNode.locator('.encounter-name').first().innerText()).trim()
  expect(encounterName).not.toBe('')

  const infoButton = encounterNode.locator('.info-btn').first()
  await clickWhenActionable(infoButton)
  const descriptionDisplay = await ensureDescriptionDisplayVisible(encounterNode)

  const baselineDescription = (await descriptionDisplay.innerText()).trim()
  const restoreDescription =
    baselineDescription === 'No description available. Click to add one.' ? '' : baselineDescription
  const newDescription = `Encounter description e2e ${makeScopedSuffix(testInfo)}`

  await clickWhenActionable(descriptionDisplay)
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
  await clickWhenActionable(reloadedInfoButton)
  const reloadedDescriptionDisplay = await ensureDescriptionDisplayVisible(reloadedEncounterNode)
  const reloadedDescriptionText = (await reloadedDescriptionDisplay.innerText()).trim()
  expect(reloadedDescriptionText).toContain('Encounter description e2e')
  expect(reloadedDescriptionText).not.toBe(restoreDescription)

  // Cleanup only when this test's own write is still present. Cross-browser runs can overwrite
  // the same seeded encounter while this test is in-flight.
  if (reloadedDescriptionText === newDescription) {
    await clickWhenActionable(reloadedDescriptionDisplay)
    const cleanupTextarea = reloadedEncounterNode.locator(
      '.encounter-description-input .shared-textarea'
    )
    await expect(cleanupTextarea).toBeVisible()
    await cleanupTextarea.fill(restoreDescription)
    await cleanupTextarea.press('Control+Enter')
    await saveCanvasAndAssertSuccess(page)
  }
})

test('ENCOUNTERS-TALKING-AUDIO-01 returns audio over websocket and completes processing', async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.use?.browserName === 'webkit',
    'WebKit microphone automation is not reliably supported for this audio flow.'
  )
  test.skip(
    process.env.ENCOUNTERS_AUDIO_TEST !== '1',
    'Audio talking test runs only in dedicated encounters audio command.'
  )
  test.setTimeout(90_000)
  await installWebSocketProbe(page)

  await page.goto('/encounters')
  await waitForEncountersGet(page)
  await expect(page).toHaveURL(/\/encounters/)

  const { firstPlayerOption } = await findEncounterNodeWithCharacterAndPlayerOptions(page)
  const playerSelect = page.locator('#player-select')
  await playerSelect.selectOption(firstPlayerOption)

  try {
    await runSpeakStopLifecycle(page, { clickWithEvaluate: true })
    await assertConversationAudioRoundtrip(page, {
      wsPathRegex: /\/api\/encounters\/\d+\/conversation\/\d+\/\d+/,
      timeoutMs: 60_000,
    })
    await assertReturnedToReadyState(page, {
      readyTextPattern: /Click Speak/,
      timeoutMs: 60_000,
    })
  } catch (error) {
    const micPermission = await getMicrophonePermissionState(page)
    const browserName = testInfo.project.use?.browserName || testInfo.project.name
    throw new Error(
      `Audio roundtrip failed in ${browserName}. Diagnostics: ${JSON.stringify({
        url: page.url(),
        micPermission,
      })}. Root error: ${error.message}`
    )
  }
})
