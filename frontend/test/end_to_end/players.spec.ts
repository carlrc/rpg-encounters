import { expect, test } from '@playwright/test'
import { applyDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'

let dmSession: DmSession

test.beforeAll(async ({}, testInfo) => {
  dmSession = getSpecDmSession(testInfo)
})

test.beforeEach(async ({ page }) => {
  await applyDmSession(page, dmSession)
})

const waitForPlayersGet = async (page) => {
  const playersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })
  const response = await playersResponsePromise
  expect(response.status()).toBe(200)
}

const parseNumericValue = (text, label) => {
  const match = text.match(new RegExp(`${label}:\\s*([+-]?\\d+)`))
  if (!match) {
    throw new Error(`Could not parse numeric value for ${label} from "${text}"`)
  }
  return Number(match[1])
}

const nextValueInRange = (current, min, max) => {
  if (current < max) return current + 1
  return Math.max(min, current - 1)
}

const setSliderValue = async (page, label, value) => {
  const sliderContainer = page.locator('.threshold-slider', { hasText: `${label}:` }).first()
  const slider = sliderContainer.locator('input[type="range"]')
  await slider.evaluate((element, nextValue) => {
    element.value = String(nextValue)
    element.dispatchEvent(new Event('input', { bubbles: true }))
    element.dispatchEvent(new Event('change', { bubbles: true }))
  }, value)
}

const expectModifierChipValue = async (page, label, value) => {
  await expect(page.getByText(new RegExp(`^${label}:\\s*[+]?${value}$`))).toBeVisible()
}

test('PLAYERS-SMOKE-01 loads players page, selects player, renders required player details and controls', async ({
  page,
}) => {
  await page.goto('/players')
  await waitForPlayersGet(page)
  await expect(page).toHaveURL(/\/players$/)

  const playerListItems = page.locator('.list-content .list-item')
  await expect(playerListItems.first()).toBeVisible()
  const playerCount = await playerListItems.count()
  expect(playerCount).toBeGreaterThan(0)

  const clickedListName = (await playerListItems.first().innerText()).trim()
  await playerListItems.first().click()

  const realNameHeading = page.locator('.real-name')
  const characterNameHeading = page.locator('.character-name')
  await expect(realNameHeading).toBeVisible()
  await expect(characterNameHeading).toBeVisible()
  await expect(realNameHeading).toContainText(clickedListName)

  for (const label of [
    'Race',
    'Class',
    'Size',
    'Alignment',
    'Appearance',
    'Ability & Skill Modifiers',
    'Ability Modifiers',
    'Skill Modifiers',
    'Player Login Link',
  ]) {
    await expect(page.getByText(label, { exact: true })).toBeVisible()
  }

  await expect(page.getByTitle('Generate new login link')).toBeVisible()
  await expect(page.getByTitle('Copy login link')).toBeVisible()
  await expect(page.getByPlaceholder('Click refresh to generate login link').first()).toBeVisible()

  await expect(page.getByRole('button', { name: 'Edit' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Delete' })).toBeVisible()
})

test('PLAYERS-LOGIN-LINK-01 generates player login link and renders result', async ({ page }) => {
  await page.goto('/players')
  await waitForPlayersGet(page)

  const playerListItems = page.locator('.list-content .list-item')
  await expect(playerListItems.first()).toBeVisible()
  await playerListItems.first().click()

  const loginInput = page.getByPlaceholder('Click refresh to generate login link').first()
  const copyButton = page.getByTitle('Copy login link')
  const refreshButton = page.getByTitle('Generate new login link')

  await expect(loginInput).toBeVisible()
  await expect(loginInput).toHaveValue('')
  await expect(page.getByText('Expires:', { exact: false })).toHaveCount(0)
  await expect(copyButton).toBeDisabled()

  const generateResponsePromise = page.waitForResponse((response) => {
    return (
      /\/api\/players\/\d+\/login$/.test(response.url()) && response.request().method() === 'POST'
    )
  })

  await refreshButton.click()

  const generateResponse = await generateResponsePromise
  expect(generateResponse.status()).toBe(200)
  const responseJson = await generateResponse.json()

  expect(typeof responseJson.login_url).toBe('string')
  expect(responseJson.login_url.length).toBeGreaterThan(0)
  expect(typeof responseJson.expires_at).toBe('string')
  expect(responseJson.expires_at.length).toBeGreaterThan(0)
  expect(responseJson.login_url).toMatch(/\/players\/\d+\/login\?token=/)

  await expect(loginInput).toHaveValue(/\/players\/\d+\/login\?token=/)
  await expect(loginInput).toHaveValue(/\/players\//)
  await expect(page.getByText('Expires:', { exact: false })).toBeVisible()
  await expect(page.getByText('Login link generated successfully')).toBeVisible()
  await expect(copyButton).toBeEnabled()
})

test('PLAYERS-EDIT-TEXT-01 edits and saves real name, character name, and appearance', async ({
  page,
}) => {
  await page.goto('/players')
  await waitForPlayersGet(page)

  const playerListItems = page.locator('.list-content .list-item')
  await expect(playerListItems.first()).toBeVisible()
  await playerListItems.first().click()

  const baselineRealName = (await page.locator('.real-name').innerText()).trim()
  const baselineCharacterName = (await page.locator('.character-name').innerText()).trim()
  const baselineAppearance = (await page.locator('.shared-text-display').first().innerText()).trim()

  const uniqueSuffix = Date.now().toString().slice(-6)
  const newRealName = `Auto RL ${uniqueSuffix}`
  const newCharacterName = `Auto Char ${uniqueSuffix}`
  const newAppearance = `Auto appearance ${uniqueSuffix} with persistent update coverage.`

  expect(newRealName).not.toBe(baselineRealName)
  expect(baselineCharacterName).not.toContain(newCharacterName)
  expect(newAppearance).not.toBe(baselineAppearance)

  await page.getByRole('button', { name: 'Edit' }).click()

  await page.getByPlaceholder('Real-life player name').fill(newRealName)
  await page.getByPlaceholder('Character name').fill(newCharacterName)
  await page.getByPlaceholder(/Player appearance \(max \d+ characters\)/).fill(newAppearance)

  const saveResponsePromise = page.waitForResponse((response) => {
    return /\/api\/players\/\d+$/.test(response.url()) && response.request().method() === 'PUT'
  })

  await page.getByRole('button', { name: 'Save' }).click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
  const responseJson = await saveResponse.json()
  expect(responseJson.rl_name).toBe(newRealName)
  expect(responseJson.name).toBe(newCharacterName)
  expect(responseJson.appearance).toBe(newAppearance)

  await expect(page.getByText('Player updated successfully!')).toBeVisible()
  await expect(page.locator('.real-name')).toHaveText(newRealName)
  await expect(page.locator('.character-name')).toContainText(newCharacterName)
  await expect(page.locator('.shared-text-display').first()).toHaveText(newAppearance)
  await expect(page).toHaveURL(/\/players$/)

  const reloadPlayersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })
  await page.reload()
  const reloadPlayersResponse = await reloadPlayersResponsePromise
  expect(reloadPlayersResponse.status()).toBe(200)

  await page.locator('.list-content .list-item', { hasText: newRealName }).first().click()
  await expect(page.locator('.real-name')).toHaveText(newRealName)
  await expect(page.locator('.character-name')).toContainText(newCharacterName)
  await expect(page.locator('.shared-text-display').first()).toHaveText(newAppearance)
})

test('PLAYERS-EDIT-MODIFIERS-01 adjusts and saves all modifier sliders', async ({ page }) => {
  await page.goto('/players')
  await waitForPlayersGet(page)

  const playerListItems = page.locator('.list-content .list-item')
  await expect(playerListItems.first()).toBeVisible()
  const clickedListName = (await playerListItems.first().innerText()).trim()
  await playerListItems.first().click()

  const baselineCharisma = parseNumericValue(
    await page.getByText(/^Charisma:\s*[+-]?\d+$/).innerText(),
    'Charisma'
  )
  const baselineDeception = parseNumericValue(
    await page.getByText(/^Deception:\s*[+-]?\d+$/).innerText(),
    'Deception'
  )
  const baselineIntimidation = parseNumericValue(
    await page.getByText(/^Intimidation:\s*[+-]?\d+$/).innerText(),
    'Intimidation'
  )
  const baselinePerformance = parseNumericValue(
    await page.getByText(/^Performance:\s*[+-]?\d+$/).innerText(),
    'Performance'
  )
  const baselinePersuasion = parseNumericValue(
    await page.getByText(/^Persuasion:\s*[+-]?\d+$/).innerText(),
    'Persuasion'
  )

  await page.getByRole('button', { name: 'Edit' }).click()

  const targetCharisma = nextValueInRange(baselineCharisma, -5, 10)
  const targetDeception = nextValueInRange(baselineDeception, -5, 25)
  const targetIntimidation = nextValueInRange(baselineIntimidation, -5, 25)
  const targetPerformance = nextValueInRange(baselinePerformance, -5, 25)
  const targetPersuasion = nextValueInRange(baselinePersuasion, -5, 25)

  await setSliderValue(page, 'Charisma', targetCharisma)
  await setSliderValue(page, 'Deception', targetDeception)
  await setSliderValue(page, 'Intimidation', targetIntimidation)
  await setSliderValue(page, 'Performance', targetPerformance)
  await setSliderValue(page, 'Persuasion', targetPersuasion)

  const saveResponsePromise = page.waitForResponse((response) => {
    return /\/api\/players\/\d+$/.test(response.url()) && response.request().method() === 'PUT'
  })

  await page.getByRole('button', { name: 'Save' }).click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
  const responseJson = await saveResponse.json()

  expect(responseJson.abilities.Charisma).toBe(targetCharisma)
  expect(responseJson.skills.Deception).toBe(targetDeception)
  expect(responseJson.skills.Intimidation).toBe(targetIntimidation)
  expect(responseJson.skills.Performance).toBe(targetPerformance)
  expect(responseJson.skills.Persuasion).toBe(targetPersuasion)

  await expect(page.getByText('Player updated successfully!')).toBeVisible()
  await expectModifierChipValue(page, 'Charisma', targetCharisma)
  await expectModifierChipValue(page, 'Deception', targetDeception)
  await expectModifierChipValue(page, 'Intimidation', targetIntimidation)
  await expectModifierChipValue(page, 'Performance', targetPerformance)
  await expectModifierChipValue(page, 'Persuasion', targetPersuasion)
  await expect(page).toHaveURL(/\/players$/)

  const reloadPlayersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })
  await page.reload()
  const reloadPlayersResponse = await reloadPlayersResponsePromise
  expect(reloadPlayersResponse.status()).toBe(200)

  await page.locator('.list-content .list-item', { hasText: clickedListName }).first().click()
  await expectModifierChipValue(page, 'Charisma', targetCharisma)
  await expectModifierChipValue(page, 'Deception', targetDeception)
  await expectModifierChipValue(page, 'Intimidation', targetIntimidation)
  await expectModifierChipValue(page, 'Performance', targetPerformance)
  await expectModifierChipValue(page, 'Persuasion', targetPersuasion)
})
