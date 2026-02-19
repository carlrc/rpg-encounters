import { expect, test } from '@playwright/test'

const waitForRevealsGet = async (page) => {
  const revealsResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/reveals') && response.request().method() === 'GET'
  })
  const response = await revealsResponsePromise
  expect(response.status()).toBe(200)
}

const selectFirstReveal = async (page) => {
  const revealListItems = page.locator('.list-content .list-item')
  await expect(revealListItems.first()).toBeVisible()
  const itemCount = await revealListItems.count()
  expect(itemCount).toBeGreaterThan(0)
  await revealListItems.first().click()
}

const fieldByLabel = (page, label) => {
  return page
    .locator('.shared-field')
    .filter({ has: page.locator('.shared-field-label', { hasText: label }) })
    .first()
}

const setSliderValue = async (page, labelPrefix, value) => {
  const sliderContainer = page.locator('.threshold-slider', { hasText: labelPrefix }).first()
  const slider = sliderContainer.locator('input[type="range"]')
  await slider.evaluate((element, nextValue) => {
    element.value = String(nextValue)
    element.dispatchEvent(new Event('input', { bubbles: true }))
    element.dispatchEvent(new Event('change', { bubbles: true }))
  }, value)
}

const sortedNumbers = (values) => [...values].map(Number).sort((a, b) => a - b)

test('REVEALS-SMOKE-01 loads reveals page, selects reveal, renders detail panel', async ({
  page,
}) => {
  await page.goto('/reveals')
  await waitForRevealsGet(page)
  await expect(page).toHaveURL(/\/reveals$/)

  await selectFirstReveal(page)

  await expect(page.locator('.shared-title')).toBeVisible()
  await expect(
    page.locator('.shared-field-label', { hasText: 'Level 1: Standard' }).first()
  ).toBeVisible()
  await expect(page.locator('.shared-text-display').first()).toBeVisible()
  await expect(
    page.locator('.shared-field-label', { hasText: 'Assigned Characters' }).first()
  ).toBeVisible()
  await expect(page.locator('.shared-tags-display').first()).toBeVisible()

  const level2Label = page.locator('.shared-field-label', { hasText: 'Level 2: Privileged' })
  if ((await level2Label.count()) > 0) {
    await expect(level2Label.first()).toBeVisible()
  }
  const level3Label = page.locator('.shared-field-label', { hasText: 'Level 3: Exclusive' })
  if ((await level3Label.count()) > 0) {
    await expect(level3Label.first()).toBeVisible()
  }

  await expect(page.getByRole('button', { name: 'Edit' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Delete' })).toBeVisible()
})

test('REVEALS-EDIT-01 edits and saves reveal text, assigned characters, and thresholds', async ({
  page,
}) => {
  await page.goto('/reveals')
  await waitForRevealsGet(page)
  await expect(page).toHaveURL(/\/reveals$/)

  await selectFirstReveal(page)

  const baselineTitle = (await page.locator('.shared-title').innerText()).trim()
  const baselineLevel1 = (
    await fieldByLabel(page, 'Level 1: Standard').locator('.shared-text-display').innerText()
  ).trim()
  const baselineAssignedTags = page.locator('.shared-tags-display .shared-tag-bubble')
  const baselineAssignedCount = await baselineAssignedTags.count()
  expect(baselineAssignedCount).toBeGreaterThan(0)

  const uniqueSuffix = Date.now().toString().slice(-6)
  const newTitle = `Auto Reveal ${uniqueSuffix}`
  const newLevel1 = `Auto standard content ${uniqueSuffix} for reveal edit persistence.`
  const newLevel2 = `Auto privileged content ${uniqueSuffix} for reveal edit persistence.`
  const newLevel3 = `Auto exclusive content ${uniqueSuffix} for reveal edit persistence.`

  expect(baselineTitle).not.toBe(newTitle)
  expect(baselineLevel1).not.toBe(newLevel1)

  await page.getByRole('button', { name: 'Edit' }).click()

  const editScope = page.locator('.reveal-edit .shared-form')
  await expect(editScope).toBeVisible()

  await editScope.getByPlaceholder('Reveal title').fill(newTitle)
  await editScope.getByPlaceholder('Enter standard content...').fill(newLevel1)

  const level2Toggle = editScope
    .locator('.level-toggle-option')
    .filter({ hasText: 'Add Level 2: Privileged Content' })
    .locator('input[type="checkbox"]')
  if (!(await level2Toggle.isChecked())) {
    await level2Toggle.check()
  }
  await editScope
    .getByPlaceholder('Enter privileged content (high influence required)...')
    .fill(newLevel2)

  const level3Toggle = editScope
    .locator('.level-toggle-option')
    .filter({ hasText: 'Add Level 3: Exclusive Content' })
    .locator('input[type="checkbox"]')
  if (!(await level3Toggle.isChecked())) {
    await level3Toggle.check()
  }
  await editScope
    .getByPlaceholder('Enter exclusive content (maximum influence required)...')
    .fill(newLevel3)

  const characterSelection = editScope.locator('.character-selection').first()
  const totalOptions = await characterSelection.locator('.option-item').count()
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

  const expectedCharacterIds = await characterSelection
    .locator('input[type="checkbox"]:checked')
    .evaluateAll((nodes) =>
      nodes.map((node) => Number(node.value)).filter((value) => !Number.isNaN(value))
    )
  expect(expectedCharacterIds.length).toBeGreaterThan(0)

  const standardSlider = editScope
    .locator('.threshold-slider', { hasText: 'Standard Content:' })
    .locator('input[type="range"]')
    .first()
  const minThreshold = Number((await standardSlider.getAttribute('min')) || 5)
  const maxThreshold = Number((await standardSlider.getAttribute('max')) || 25)
  const thresholdStep = Number((await standardSlider.getAttribute('step')) || 1)

  const targetStandard =
    minThreshold + thresholdStep <= maxThreshold ? minThreshold + thresholdStep : minThreshold
  const targetPrivileged =
    targetStandard + thresholdStep <= maxThreshold ? targetStandard + thresholdStep : targetStandard
  const targetExclusive =
    targetPrivileged + thresholdStep <= maxThreshold
      ? targetPrivileged + thresholdStep
      : targetPrivileged

  await setSliderValue(editScope, 'Standard Content:', targetStandard)
  await setSliderValue(editScope, 'Privileged Content:', targetPrivileged)
  await setSliderValue(editScope, 'Exclusive Content:', targetExclusive)

  const saveResponsePromise = page.waitForResponse((response) => {
    return /\/api\/reveals\/\d+$/.test(response.url()) && response.request().method() === 'PUT'
  })

  await page.getByRole('button', { name: 'Save' }).click()

  const saveResponse = await saveResponsePromise
  expect(saveResponse.status()).toBe(200)
  const responseJson = await saveResponse.json()

  expect(responseJson.title).toBe(newTitle)
  expect(responseJson.level_1_content).toBe(newLevel1)
  expect(responseJson.level_2_content).toBe(newLevel2)
  expect(responseJson.level_3_content).toBe(newLevel3)
  expect(responseJson.standard_threshold).toBe(targetStandard)
  expect(responseJson.privileged_threshold).toBe(targetPrivileged)
  expect(responseJson.exclusive_threshold).toBe(targetExclusive)
  expect(sortedNumbers(responseJson.character_ids)).toEqual(sortedNumbers(expectedCharacterIds))

  await expect(page.getByText('Reveal updated successfully!')).toBeVisible()
  await expect(page.locator('.shared-title')).toHaveText(newTitle)
  await expect(fieldByLabel(page, 'Level 1: Standard').locator('.shared-text-display')).toHaveText(
    newLevel1
  )
  await expect(
    fieldByLabel(page, 'Level 2: Privileged').locator('.shared-text-display')
  ).toHaveText(newLevel2)
  await expect(fieldByLabel(page, 'Level 3: Exclusive').locator('.shared-text-display')).toHaveText(
    newLevel3
  )
  await expect(
    page
      .locator('.shared-field-label', { hasText: `Level 1: Standard (DC ${targetStandard})` })
      .first()
  ).toBeVisible()
  await expect(
    page
      .locator('.shared-field-label', { hasText: `Level 2: Privileged (DC ${targetPrivileged})` })
      .first()
  ).toBeVisible()
  await expect(
    page
      .locator('.shared-field-label', { hasText: `Level 3: Exclusive (DC ${targetExclusive})` })
      .first()
  ).toBeVisible()

  const updatedAssignedNames = await page
    .locator('.shared-tags-display .shared-tag-bubble')
    .evaluateAll((nodes) =>
      nodes
        .map((node) => node.textContent?.trim() || '')
        .filter(Boolean)
        .sort()
    )
  expect(updatedAssignedNames.length).toBeGreaterThan(0)

  const reloadRevealsResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/reveals') && response.request().method() === 'GET'
  })
  await page.reload()
  const reloadRevealsResponse = await reloadRevealsResponsePromise
  expect(reloadRevealsResponse.status()).toBe(200)

  await page.locator('.list-content .list-item', { hasText: newTitle }).first().click()
  await expect(page.locator('.shared-title')).toHaveText(newTitle)
  await expect(fieldByLabel(page, 'Level 1: Standard').locator('.shared-text-display')).toHaveText(
    newLevel1
  )
  await expect(
    fieldByLabel(page, 'Level 2: Privileged').locator('.shared-text-display')
  ).toHaveText(newLevel2)
  await expect(fieldByLabel(page, 'Level 3: Exclusive').locator('.shared-text-display')).toHaveText(
    newLevel3
  )

  const persistedAssignedNames = await page
    .locator('.shared-tags-display .shared-tag-bubble')
    .evaluateAll((nodes) =>
      nodes
        .map((node) => node.textContent?.trim() || '')
        .filter(Boolean)
        .sort()
    )
  expect(persistedAssignedNames).toEqual(updatedAssignedNames)
  await expect(page).toHaveURL(/\/reveals$/)
})
