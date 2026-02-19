import { expect, test } from '@playwright/test'

const waitForCharactersGet = async (page) => {
  const charactersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
  })
  const response = await charactersResponsePromise
  expect(response.status()).toBe(200)
}

const selectFirstCharacter = async (page) => {
  const characterListItems = page.locator('.list-content .list-item')
  await expect(characterListItems.first()).toBeVisible()
  const itemCount = await characterListItems.count()
  expect(itemCount).toBeGreaterThan(0)
  const firstCharacterListText = (await characterListItems.first().innerText()).trim()
  await characterListItems.first().click()
  return firstCharacterListText
}

const fieldByLabel = (page, label) => {
  return page
    .locator('.shared-field')
    .filter({ has: page.locator('.shared-field-label', { hasText: label }) })
    .first()
}

test('CHARACTERS-SMOKE-01 loads character page, selects character, renders detail panel', async ({
  page,
}) => {
  await page.goto('/characters')
  await waitForCharactersGet(page)
  await expect(page).toHaveURL(/\/characters$/)

  await selectFirstCharacter(page)

  await expect(page.locator('.shared-title')).toBeVisible()

  for (const label of [
    'Race',
    'Alignment',
    'Size',
    'Profession',
    'Background',
    'Communication Style',
    'Motivation',
  ]) {
    await expect(page.locator('.shared-field-label', { hasText: label }).first()).toBeVisible()
  }

  await expect(page.getByRole('button', { name: 'Edit' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Delete' })).toBeVisible()

  const voiceButton = page.getByTitle('Play voice sample')
  if ((await voiceButton.count()) > 0) {
    await expect(voiceButton.first()).toBeVisible()
  }
})

test('CHARACTERS-EDIT-TEXT-01 edits and saves core text fields', async ({ page }) => {
  await page.goto('/characters')
  await waitForCharactersGet(page)
  await expect(page).toHaveURL(/\/characters$/)

  await selectFirstCharacter(page)

  const baselineName = (await page.locator('.shared-title').innerText()).trim()
  const baselineProfession = (
    await fieldByLabel(page, 'Profession').locator('.shared-field-value').innerText()
  ).trim()
  const baselineBackground = (
    await fieldByLabel(page, 'Background').locator('.shared-text-display').innerText()
  ).trim()
  const baselineMotivation = (
    await fieldByLabel(page, 'Motivation').locator('.shared-text-display').innerText()
  ).trim()

  const uniqueSuffix = Date.now().toString().slice(-6)
  const newName = `Auto Character ${uniqueSuffix}`
  const newProfession = `Auto Profession ${uniqueSuffix}`
  const newBackground = `Auto background ${uniqueSuffix} for persistence coverage.`
  const newMotivation = `Auto motivation ${uniqueSuffix} for save verification.`

  expect(baselineName).not.toContain(newName)
  expect(baselineProfession).not.toBe(newProfession)
  expect(baselineBackground).not.toBe(newBackground)
  expect(baselineMotivation).not.toBe(newMotivation)

  await page.getByRole('button', { name: 'Edit' }).click()

  await page.getByPlaceholder('Character name').fill(newName)
  await page.getByPlaceholder('Profession').fill(newProfession)
  await page.getByPlaceholder(/Character background \(max \d+ characters\)/).fill(newBackground)
  await page.getByPlaceholder(/Character motivation \(max \d+ characters\)/).fill(newMotivation)

  const saveResponsePromise = page.waitForResponse((response) => {
    return /\/api\/characters\/\d+$/.test(response.url()) && response.request().method() === 'PUT'
  })

  await page.getByRole('button', { name: 'Save' }).click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
  const responseJson = await saveResponse.json()
  expect(responseJson.name).toBe(newName)
  expect(responseJson.profession).toBe(newProfession)
  expect(responseJson.background).toBe(newBackground)
  expect(responseJson.motivation).toBe(newMotivation)

  await expect(page.getByText('Character updated successfully!')).toBeVisible()
  await expect(page.locator('.shared-title')).toContainText(newName)
  await expect(fieldByLabel(page, 'Profession').locator('.shared-field-value')).toHaveText(
    newProfession
  )
  await expect(fieldByLabel(page, 'Background').locator('.shared-text-display')).toHaveText(
    newBackground
  )
  await expect(fieldByLabel(page, 'Motivation').locator('.shared-text-display')).toHaveText(
    newMotivation
  )
  await expect(page).toHaveURL(/\/characters$/)

  const reloadCharactersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
  })
  await page.reload()
  const reloadCharactersResponse = await reloadCharactersResponsePromise
  expect(reloadCharactersResponse.status()).toBe(200)

  await page.locator('.list-content .list-item', { hasText: newName }).first().click()
  await expect(page.locator('.shared-title')).toContainText(newName)
  await expect(fieldByLabel(page, 'Profession').locator('.shared-field-value')).toHaveText(
    newProfession
  )
  await expect(fieldByLabel(page, 'Background').locator('.shared-text-display')).toHaveText(
    newBackground
  )
  await expect(fieldByLabel(page, 'Motivation').locator('.shared-text-display')).toHaveText(
    newMotivation
  )
})

test('CHARACTERS-VOICE-TEST-01 voice test button triggers sample request and loading state', async ({
  page,
}) => {
  await page.goto('/characters')
  await waitForCharactersGet(page)
  await expect(page).toHaveURL(/\/characters$/)

  await selectFirstCharacter(page)

  const voiceButton = page.getByTitle('Play voice sample').first()
  const voiceButtonCount = await page.getByTitle('Play voice sample').count()
  test.skip(voiceButtonCount === 0, 'Skipping: selected seeded character has no voice_id.')

  await expect(voiceButton).toBeVisible()
  await expect(voiceButton).toHaveText('▶️')

  await page.route(/\/voices\/[^/]+\/sample\?/, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 400))
    await route.continue()
  })

  const sampleResponsePromise = page.waitForResponse((response) => {
    return response.request().method() === 'GET' && /\/voices\/[^/]+\/sample\?/.test(response.url())
  })

  await voiceButton.click()
  await expect(voiceButton).toHaveText('⏳')

  const sampleResponse = await sampleResponsePromise
  expect(sampleResponse.status()).toBe(200)
  expect(sampleResponse.url()).toMatch(/\/voices\/[^/]+\/sample\?/)

  await expect(voiceButton).toHaveText('▶️')
  await page.unroute(/\/voices\/[^/]+\/sample\?/)
})
