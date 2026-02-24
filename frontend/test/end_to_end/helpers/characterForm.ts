import { expect } from '@playwright/test'

const selectFirstNonEmptyOption = async (selectLocator) => {
  await expect(selectLocator).toBeVisible()
  const value = await selectLocator.evaluate((element) => {
    const options = Array.from(element.options || [])
    const firstNonEmpty = options.find((option) => option.value && option.value.trim() !== '')
    return firstNonEmpty ? firstNonEmpty.value : null
  })

  if (!value) {
    throw new Error('Could not find a non-empty option in required select field.')
  }

  await selectLocator.selectOption(value)
  return value
}

const getUniqueSelectByPlaceholder = (page, placeholderText) => {
  const locator = page.locator('.shared-form select.shared-select', {
    has: page.locator('option', { hasText: placeholderText }),
  })
  return locator
}

const selectRequiredField = async (page, placeholderText) => {
  const locator = getUniqueSelectByPlaceholder(page, placeholderText)
  await expect(locator).toHaveCount(1)
  await selectFirstNonEmptyOption(locator.first())
}

export const fillCharacterForm = async (page, data) => {
  await page.getByPlaceholder('Character name').fill(data.name)

  await selectRequiredField(page, 'Select Race')
  await selectRequiredField(page, 'Select Alignment')
  await selectRequiredField(page, 'Select Size')
  await selectRequiredField(page, 'Select Gender')

  await page.getByPlaceholder('Profession').fill(data.profession)
  await page.getByPlaceholder(/Character background \(max \d+ characters\)/).fill(data.background)

  const communicationStyleSelect = getUniqueSelectByPlaceholder(page, 'Select Communication Style')
  await expect(communicationStyleSelect).toHaveCount(1)
  await communicationStyleSelect.selectOption({ label: 'Nerdy' })

  await page.getByPlaceholder(/Character motivation \(max \d+ characters\)/).fill(data.motivation)

  await page.locator('.manual-voice-input').fill(data.voiceId)
  await page.getByRole('button', { name: 'Set Voice' }).click()

  await expect(
    page.locator('.communication-style-type', { hasText: data.voiceDisplayName })
  ).toBeVisible()
}

export const submitCharacterForm = async (page, { mode }) => {
  if (mode === 'create') {
    await page.getByRole('button', { name: 'Create' }).click()
    return
  }

  if (mode === 'edit') {
    await page.getByRole('button', { name: 'Save' }).click()
    return
  }

  throw new Error(`Unsupported form submission mode: ${mode}`)
}

export const fillCharacterFormAndSubmit = async (page, { mode, data }) => {
  await fillCharacterForm(page, data)
  await submitCharacterForm(page, { mode })
}
