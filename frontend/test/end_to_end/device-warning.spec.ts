import { expect, test } from '@playwright/test'
import { applyDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'
import { mobileDevices, shouldSkipMobileDevice } from './helpers/mobileDevices'

let dmSession: DmSession

test.beforeAll(async ({}, testInfo) => {
  dmSession = getSpecDmSession(testInfo)
})

test.beforeEach(async ({ page }) => {
  await applyDmSession(page, dmSession)
})

for (const mobileDevice of mobileDevices) {
  test.describe(`Device warning popup (${mobileDevice.name})`, () => {
    test.use({ ...mobileDevice.device })

    test.beforeEach(({}, testInfo) => {
      test.skip(
        shouldSkipMobileDevice(mobileDevice, testInfo),
        'Android device emulation runs in Chromium only.'
      )
    })

    test('DEVICE-WARNING-01 shows on mobile players page', async ({ page }) => {
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
}
