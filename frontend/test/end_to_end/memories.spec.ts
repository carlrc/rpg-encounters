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

const waitForMemoriesGet = (page) => {
  return page.waitForResponse((response) => {
    return response.url().endsWith('/api/memories') && response.request().method() === 'GET'
  })
}

const waitForCharactersGet = (page) => {
  return page.waitForResponse((response) => {
    return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
  })
}

const selectFirstMemory = async (page) => {
  const memoryListItems = page.locator('.list-content .list-item')
  await expect(memoryListItems.first()).toBeVisible()
  const itemCount = await memoryListItems.count()
  expect(itemCount).toBeGreaterThan(0)
  await memoryListItems.first().click()
}

const fieldByLabel = (page, label) => {
  return page
    .locator('.shared-field')
    .filter({ has: page.locator('.shared-field-label', { hasText: label }) })
    .first()
}

const sortedNumbers = (values) => [...values].map(Number).sort((a, b) => a - b)

const assertCharacterSelectionNotNested = async (scope) => {
  await expect(scope.locator('.character-filters .filter-row')).toHaveCount(1)
  await expect(scope.locator('.character-selection .option-item').first()).toBeVisible()
  await expect(scope.locator('.character-selection .dropdown-header .header-btn')).toHaveCount(0)
  await expect(scope.locator('.character-selection .multiselect-trigger')).toHaveCount(0)
}

test('MEMORIES-SMOKE-01 loads memories page, selects memory, renders detail panel', async ({
  page,
}) => {
  const memoriesResponsePromise = waitForMemoriesGet(page)
  const charactersResponsePromise = waitForCharactersGet(page)
  await page.goto('/memories')
  const memoriesResponse = await memoriesResponsePromise
  const charactersResponse = await charactersResponsePromise
  expect(memoriesResponse.status()).toBe(200)
  expect(charactersResponse.status()).toBe(200)
  await expect(page).toHaveURL(/\/memories$/)

  await selectFirstMemory(page)

  await expect(page.locator('.shared-title')).toBeVisible()
  await expect(page.locator('.shared-field-label', { hasText: 'Content' }).first()).toBeVisible()
  await expect(
    page.locator('.shared-field-label', { hasText: 'Assigned Characters' }).first()
  ).toBeVisible()
  await expect(page.locator('.shared-text-display').first()).toBeVisible()
  await expect(page.locator('.shared-tags-display').first()).toBeVisible()

  await expect(page.getByRole('button', { name: 'Edit' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Delete' })).toBeVisible()
})

test('MEMORIES-EDIT-01 edits and saves title/content/assigned characters', async ({ page }) => {
  const memoriesResponsePromise = waitForMemoriesGet(page)
  const charactersResponsePromise = waitForCharactersGet(page)
  await page.goto('/memories')
  const memoriesResponse = await memoriesResponsePromise
  const charactersResponse = await charactersResponsePromise
  expect(memoriesResponse.status()).toBe(200)
  expect(charactersResponse.status()).toBe(200)
  await expect(page).toHaveURL(/\/memories$/)

  await selectFirstMemory(page)

  const baselineTitle = (await page.locator('.shared-title').innerText()).trim()
  const baselineContent = (
    await fieldByLabel(page, 'Content').locator('.shared-text-display').innerText()
  ).trim()
  const baselineAssignedTags = page.locator('.shared-tags-display .shared-tag-bubble')
  const baselineAssignedTagCount = await baselineAssignedTags.count()

  const uniqueSuffix = Date.now().toString().slice(-6)
  const newTitle = `Auto Memory ${uniqueSuffix}`
  const newContent = `Auto memory content ${uniqueSuffix} verifying edit and persistence behavior.`

  expect(baselineTitle).not.toBe(newTitle)
  expect(baselineContent).not.toBe(newContent)

  await page.getByRole('button', { name: 'Edit' }).click()
  const editScope = page.locator('.shared-form').first()
  await expect(editScope).toBeVisible()
  await assertCharacterSelectionNotNested(editScope)

  await page.getByPlaceholder('Memory title').fill(newTitle)
  await page.getByPlaceholder(/Memory content \(max \d+ characters\)/).fill(newContent)

  const characterSelection = page.locator('.shared-form .character-selection').first()
  const allCharacterOptions = characterSelection.locator('.option-item')
  const totalOptions = await allCharacterOptions.count()
  expect(totalOptions).toBeGreaterThan(0)

  const selectedOptions = characterSelection.locator('input[type="checkbox"]:checked')
  const selectedCount = await selectedOptions.count()
  expect(selectedCount).toBeGreaterThan(0)

  if (totalOptions > 1) {
    await selectedOptions.first().setChecked(false)

    let currentlyChecked = await characterSelection
      .locator('input[type="checkbox"]:checked')
      .count()
    if (currentlyChecked === 0) {
      await characterSelection.locator('input[type="checkbox"]').first().setChecked(true)
      currentlyChecked = await characterSelection.locator('input[type="checkbox"]:checked').count()
    }

    if (currentlyChecked === totalOptions) {
      await characterSelection.locator('input[type="checkbox"]').last().setChecked(false)
    } else {
      const uncheckedOptions = characterSelection.locator('input[type="checkbox"]:not(:checked)')
      const uncheckedCount = await uncheckedOptions.count()
      if (uncheckedCount > 0) {
        await uncheckedOptions.first().setChecked(true)
      }
    }
  }
  // Fallback path when only one character option exists: keep assignment unchanged so form stays valid.

  const expectedCharacterIds = await characterSelection
    .locator('input[type="checkbox"]:checked')
    .evaluateAll((nodes) =>
      nodes.map((node) => Number(node.value)).filter((value) => !Number.isNaN(value))
    )
  expect(expectedCharacterIds.length).toBeGreaterThan(0)

  const saveResponsePromise = page.waitForResponse((response) => {
    return /\/api\/memories\/\d+$/.test(response.url()) && response.request().method() === 'PUT'
  })

  await page.getByRole('button', { name: 'Save' }).click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
  const responseJson = await saveResponse.json()
  expect(responseJson.title).toBe(newTitle)
  expect(responseJson.content).toBe(newContent)
  expect(sortedNumbers(responseJson.character_ids)).toEqual(sortedNumbers(expectedCharacterIds))

  await expect(page.getByText('Memory updated successfully!')).toBeVisible()
  await expect(page.locator('.shared-title')).toHaveText(newTitle)
  await expect(fieldByLabel(page, 'Content').locator('.shared-text-display')).toHaveText(newContent)

  const updatedAssignedTags = page.locator('.shared-tags-display .shared-tag-bubble')
  const updatedAssignedTagCount = await updatedAssignedTags.count()
  const updatedAssignedNames = (
    await Promise.all(
      Array.from({ length: updatedAssignedTagCount }, (_, index) =>
        updatedAssignedTags.nth(index).innerText()
      )
    )
  )
    .map((name) => name.trim())
    .sort()

  expect(updatedAssignedTagCount).toBeGreaterThan(0)

  const reloadMemoriesResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/memories') && response.request().method() === 'GET'
  })
  const reloadCharactersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
  })
  await page.reload()
  const reloadMemoriesResponse = await reloadMemoriesResponsePromise
  const reloadCharactersResponse = await reloadCharactersResponsePromise
  expect(reloadMemoriesResponse.status()).toBe(200)
  expect(reloadCharactersResponse.status()).toBe(200)

  await page.locator('.list-content .list-item', { hasText: newTitle }).first().click()
  await expect(page.locator('.shared-title')).toHaveText(newTitle)
  await expect(fieldByLabel(page, 'Content').locator('.shared-text-display')).toHaveText(newContent)

  const persistedAssignedTags = page.locator('.shared-tags-display .shared-tag-bubble')
  await expect(persistedAssignedTags.first()).toBeVisible()

  await page.getByRole('button', { name: 'Edit' }).click()
  const persistedCharacterIds = await page
    .locator('.shared-form .character-selection input[type="checkbox"]:checked')
    .evaluateAll((nodes) =>
      nodes.map((node) => Number(node.value)).filter((value) => !Number.isNaN(value))
    )
  expect(sortedNumbers(persistedCharacterIds)).toEqual(sortedNumbers(expectedCharacterIds))
  await expect(page).toHaveURL(/\/memories$/)
})
