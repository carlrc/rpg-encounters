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
