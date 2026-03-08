import { expect, test } from '@playwright/test'

test.describe('Landing route', () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test('LANDING-01 unauthenticated root shows landing and login CTA', async ({ page }) => {
    await page.goto('/')

    await expect(page).toHaveURL(/\/$/)
    await expect(page.locator('main .landing-hero h1')).toBeVisible()
    await expect(page.getByRole('link', { name: /^Login$/ })).toBeVisible()

    await page.getByRole('link', { name: /^Login$/ }).click()
    await expect(page).toHaveURL('/login')
    await expect(page.getByRole('button', { name: 'Request Login Link' })).toBeVisible()
  })

  test('LANDING-02 unauthenticated protected route redirects to login', async ({ page }) => {
    await page.goto('/players')
    await expect(page).toHaveURL('/login')
    await expect(page.getByRole('button', { name: 'Request Login Link' })).toBeVisible()
  })
})
