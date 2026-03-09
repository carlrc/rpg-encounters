import { expect, test, devices } from '@playwright/test'
import { applyDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'

let dmSession: DmSession

test.use({ ...devices['iPhone 12'] })

test.describe('Device warning popup', () => {
  test.beforeAll(async ({}, testInfo) => {
    dmSession = getSpecDmSession(testInfo)
  })

  test.beforeEach(async ({ page }) => {
    await applyDmSession(page, dmSession)
  })

  test('DEVICE-WARNING-01 shows on iPhone 12 players page', async ({ page }) => {
    await page.goto('/players')
    await expect(page.getByRole('heading', { name: 'Device Warning' })).toBeVisible()
    await expect(
      page.getByText('The application was designed for tablets and desktops.')
    ).toBeVisible()
  })

  test('DEVICE-WARNING-02 stays hidden after close in same session', async ({ page }) => {
    await page.goto('/players')
    await expect(page.getByRole('heading', { name: 'Device Warning' })).toBeVisible()
    await page.getByRole('button', { name: 'Close', exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Device Warning' })).toHaveCount(0)

    await page.reload()
    await expect(page.getByRole('heading', { name: 'Device Warning' })).toHaveCount(0)
  })
})
