import { expect, test } from '@playwright/test'
import { applyDmSession, bootstrapDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'

let dmSession: DmSession

test.beforeAll(async ({}, testInfo) => {
  dmSession = getSpecDmSession(testInfo)
})

test.beforeEach(async ({ page }) => {
  await applyDmSession(page, dmSession)
})

test('PROFILE-BILLING-POPUP-01 opens profile popup and shows billing tokens', async ({ page }) => {
  await page.goto('/characters')

  const profileButton = page.getByRole('button', { name: 'Profile' })
  await expect(profileButton).toBeVisible()

  const profileResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/profile') && response.request().method() === 'GET'
  })

  await profileButton.click()

  const profileResponse = await profileResponsePromise
  expect(profileResponse.status()).toBe(200)

  const popup = page.locator('.encounter-popup').first()
  await expect(popup).toBeVisible()
  await expect(popup.locator('.list-content .list-item', { hasText: 'Billing' })).toHaveCount(1)
  await expect(popup.locator('.shared-title', { hasText: 'Billing' })).toHaveCount(1)
  await expect(popup.locator('.filter-controls')).toHaveCount(0)
  await expect(popup.locator('.shared-field-label', { hasText: 'Available Tokens' })).toHaveCount(1)
  await expect(popup.getByRole('button', { name: 'Logout' })).toBeVisible()
})

test('PROFILE-SETTINGS-POPUP-01 shows danger zone delete account action', async ({ page }) => {
  await page.goto('/characters')

  const profileButton = page.getByRole('button', { name: 'Profile' })
  await expect(profileButton).toBeVisible()

  await profileButton.click()

  const popup = page.locator('.encounter-popup').first()
  await expect(popup).toBeVisible()

  await popup.locator('.list-content .list-item', { hasText: 'Settings' }).click()

  await expect(popup.locator('.shared-title', { hasText: 'Settings' })).toHaveCount(1)
  await expect(popup.locator('.shared-field-label', { hasText: 'Danger Zone' })).toHaveCount(1)
  await expect(popup.getByRole('button', { name: 'Delete Account' })).toBeVisible()
})

test('PROFILE-LOGOUT-01 logs out from profile modal and redirects to login', async ({ page }) => {
  await page.goto('/characters')

  await page.getByRole('button', { name: 'Profile' }).click()
  const popup = page.locator('.encounter-popup').first()
  await expect(popup).toBeVisible()

  const logoutResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/auth/logout') && response.request().method() === 'POST'
  })

  await popup.getByRole('button', { name: 'Logout' }).click()

  const logoutResponse = await logoutResponsePromise
  expect(logoutResponse.status()).toBe(204)
  await expect(page).toHaveURL('/login')
  await expect(page.getByRole('button', { name: 'Request Login Link' })).toBeVisible()
})

test('PROFILE-DELETE-ACCOUNT-FAIL-01 shows error and stays on page when delete fails', async ({
  page,
}) => {
  await page.route('**/api/profile', async (route) => {
    if (route.request().method() === 'DELETE') {
      await route.fulfill({ status: 500, body: 'server error' })
      return
    }
    await route.continue()
  })

  await page.goto('/characters')
  await page.getByRole('button', { name: 'Profile' }).click()

  const popup = page.locator('.encounter-popup').first()
  await expect(popup).toBeVisible()
  await popup.locator('.list-content .list-item', { hasText: 'Settings' }).click()
  await expect(popup.getByRole('button', { name: 'Delete Account' })).toBeVisible()

  const dialogMessages: string[] = []
  page.on('dialog', async (dialog) => {
    dialogMessages.push(dialog.message())
    await dialog.accept()
  })

  const deleteResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/profile') && response.request().method() === 'DELETE'
  })

  await popup.getByRole('button', { name: 'Delete Account' }).click()
  const deleteResponse = await deleteResponsePromise
  expect(deleteResponse.status()).toBe(500)

  await expect(page).toHaveURL(/\/characters$/)
  await expect(popup).toBeVisible()
  expect(
    dialogMessages.some((message) =>
      message.includes('Are you sure you want to delete your account?')
    )
  ).toBe(true)
  expect(
    dialogMessages.some((message) =>
      message.includes('Failed to delete account. Please try again.')
    )
  ).toBe(true)
})

test('PROFILE-DELETE-ACCOUNT-01 deletes account and returns to login', async ({ page }) => {
  const isolatedSession = bootstrapDmSession()
  await applyDmSession(page, isolatedSession)

  await page.goto('/characters')
  await page.getByRole('button', { name: 'Profile' }).click()

  const popup = page.locator('.encounter-popup').first()
  await expect(popup).toBeVisible()
  await popup.locator('.list-content .list-item', { hasText: 'Settings' }).click()

  page.once('dialog', async (dialog) => {
    await dialog.accept()
  })

  const deleteResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/profile') && response.request().method() === 'DELETE'
  })

  await popup.getByRole('button', { name: 'Delete Account' }).click()

  const deleteResponse = await deleteResponsePromise
  expect(deleteResponse.status()).toBe(204)
  await expect(page).toHaveURL('/login')
  await expect(page.getByRole('button', { name: 'Request Login Link' })).toBeVisible()
})
