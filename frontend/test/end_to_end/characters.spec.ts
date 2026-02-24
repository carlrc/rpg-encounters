import { expect, test } from '@playwright/test'
import { waitForApiResponse } from './helpers/networkAsserts'

const waitForCharactersGet = async (page, timeout = 30_000) => {
  await waitForApiResponse(page, {
    method: 'GET',
    pathRegex: /\/api\/characters$/,
    timeout,
    expectedStatus: 200,
  })
}

const gotoCharactersPage = async (page) => {
  const charactersResponsePromise = waitForCharactersGet(page, 10_000)
  await page.goto('/characters')
  await expect(page).toHaveURL(/\/characters$/)
  await charactersResponsePromise
}

const characterListItems = (page) => page.locator('.list-content .list-item')

const selectCharacterByIndex = async (page, index) => {
  const listItems = characterListItems(page)
  await expect(listItems.first()).toBeVisible()
  const count = await listItems.count()
  expect(count).toBeGreaterThan(0)
  const targetIndex = Math.min(Math.max(index, 0), count - 1)
  const target = listItems.nth(targetIndex)
  const targetName = (await target.innerText()).trim()
  await target.click()
  await expect(page.locator('.shared-title')).toContainText(targetName)
  return targetName
}

const selectCharacterForProject = async (page, testInfo) => {
  const items = characterListItems(page)
  const count = await items.count()
  expect(count).toBeGreaterThan(0)
  const projectName = testInfo?.project?.name || 'chromium'
  if (projectName === 'webkit') {
    return selectCharacterByIndex(page, count - 1)
  }
  if (projectName === 'firefox') {
    return selectCharacterByIndex(page, Math.floor(count / 2))
  }
  return selectCharacterByIndex(page, 0)
}

const selectFirstCharacterWithVoice = async (page) => {
  const items = characterListItems(page)
  const count = await items.count()
  expect(count).toBeGreaterThan(0)

  for (let index = 0; index < count; index++) {
    await selectCharacterByIndex(page, index)
    if ((await page.getByTitle('Play voice sample').count()) > 0) {
      return
    }
  }

  throw new Error('No character with voice sample button found.')
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
  await gotoCharactersPage(page)
  await selectCharacterByIndex(page, 0)

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

test('CHARACTERS-EDIT-TEXT-01 edits and saves core text fields', async ({ page }, testInfo) => {
  await gotoCharactersPage(page)
  await selectCharacterForProject(page, testInfo)

  await page.getByRole('button', { name: 'Edit' }).click()
  const baselineName = (await page.getByPlaceholder('Character name').inputValue()).trim()
  const baselineProfession = (await page.getByPlaceholder('Profession').inputValue()).trim()
  const baselineBackground = (
    await page.getByPlaceholder(/Character background \(max \d+ characters\)/).inputValue()
  ).trim()
  const baselineMotivation = (
    await page.getByPlaceholder(/Character motivation \(max \d+ characters\)/).inputValue()
  ).trim()

  const shortSuffix = `${Date.now().toString().slice(-6)}-${testInfo.project.name === 'webkit' ? 'w' : 'c'}`
  const newName = `Auto Character ${shortSuffix}`
  const newProfession = `Auto Profession ${shortSuffix}`
  const newBackground = `Auto background ${shortSuffix} for persistence coverage.`
  const newMotivation = `Auto motivation ${shortSuffix} for save verification.`

  try {
    await page.getByPlaceholder('Character name').fill(newName)
    await page.getByPlaceholder('Profession').fill(newProfession)
    await page.getByPlaceholder(/Character background \(max \d+ characters\)/).fill(newBackground)
    await page.getByPlaceholder(/Character motivation \(max \d+ characters\)/).fill(newMotivation)

    const saveResponsePromise = waitForApiResponse(page, {
      method: 'PUT',
      pathRegex: /\/api\/characters\/\d+$/,
      expectedStatus: 200,
    })

    await page.getByRole('button', { name: 'Save' }).click()

    const saveResponse = await saveResponsePromise
    const responseJson = await saveResponse.json()
    expect(responseJson.name).toBe(newName)
    expect(responseJson.name).toMatch(/^[\p{L}\p{N}\s'-]+$/u)
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

    const reloadCharactersResponsePromise = waitForCharactersGet(page)
    await page.reload()
    await reloadCharactersResponsePromise

    await characterListItems(page).filter({ hasText: newName }).first().click()
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
  } finally {
    const editedRows = characterListItems(page).filter({ hasText: newName })
    if ((await editedRows.count()) > 0) {
      try {
        await editedRows.first().click()
        await page.getByRole('button', { name: 'Edit' }).click()
        await page.getByPlaceholder('Character name').fill(baselineName)
        await page.getByPlaceholder('Profession').fill(baselineProfession)
        await page
          .getByPlaceholder(/Character background \(max \d+ characters\)/)
          .fill(baselineBackground)
        await page
          .getByPlaceholder(/Character motivation \(max \d+ characters\)/)
          .fill(baselineMotivation)
        const restoreResponsePromise = waitForApiResponse(page, {
          method: 'PUT',
          pathRegex: /\/api\/characters\/\d+$/,
          expectedStatus: 200,
        })
        await page.getByRole('button', { name: 'Save' }).click()
        await restoreResponsePromise
      } catch {
        // Best-effort cleanup only; assertion coverage for the test has already completed.
      }
    }
  }
})

test('CHARACTERS-VOICE-TEST-01 voice test button triggers sample request and loading state', async ({
  page,
}) => {
  await gotoCharactersPage(page)
  await selectFirstCharacterWithVoice(page)

  const voiceButton = page.getByTitle('Play voice sample').first()
  const voiceButtonCount = await page.getByTitle('Play voice sample').count()
  expect(voiceButtonCount).toBeGreaterThan(0)

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
