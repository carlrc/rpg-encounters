import { expect, test } from '@playwright/test'
import { applyDmSession, type DmSession } from './helpers/bootstrapDm'
import { getSpecDmSession } from './helpers/specDm'

test.describe('Route redirects (unauthenticated)', () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test('REDIRECTS-UNAUTH-01 / stays public', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\/$/)
  })

  test('REDIRECTS-UNAUTH-02 /login stays on login', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveURL('/login')
    await expect(page.getByRole('button', { name: 'Request Login Link' })).toBeVisible()
  })
})

let dmSession: DmSession

test.describe('Route redirects (authenticated)', () => {
  test.beforeAll(async ({}, testInfo) => {
    dmSession = getSpecDmSession(testInfo)
  })

  test.beforeEach(async ({ page }) => {
    await applyDmSession(page, dmSession)
  })

  test('REDIRECTS-AUTH-01 / redirects to /players', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\/players$/)
    await expect(page.getByRole('button', { name: 'Add Player' })).toBeVisible()
  })

  test('REDIRECTS-AUTH-02 /login redirects to /players', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveURL(/\/players$/)
    await expect(page.getByRole('button', { name: 'Add Player' })).toBeVisible()
  })
})
