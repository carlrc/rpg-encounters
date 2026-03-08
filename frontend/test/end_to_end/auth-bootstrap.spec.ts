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

test('AUTH-BOOTSTRAP-01 CLI returns valid JSON contract', async () => {
  for (const key of ['cookie_name', 'cookie_value', 'world_id', 'user_id', 'email']) {
    expect(dmSession).toHaveProperty(key)
  }
  expect(String(dmSession.cookie_name).length).toBeGreaterThan(0)
  expect(String(dmSession.cookie_value).length).toBeGreaterThan(0)
  expect(Number(dmSession.world_id)).toBeGreaterThan(0)
  expect(Number(dmSession.user_id)).toBeGreaterThan(0)
  expect(dmSession.email).toMatch(/^test\+.+@example\.com$/)
})

test('AUTH-BOOTSTRAP-02 generated cookie is accepted by route guard', async ({ page }) => {
  await page.goto('/players')
  await expect(page).toHaveURL(/\/players$/)
  await expect(page.getByRole('button', { name: 'Add Player' })).toBeVisible()
  await expect(page).not.toHaveURL(/\/login$/)
})

test('AUTH-BOOTSTRAP-03 /api/players request succeeds after bootstrap', async ({ page }) => {
  const playersResponsePromise = page.waitForResponse((response) => {
    return response.url().endsWith('/api/players') && response.request().method() === 'GET'
  })

  await page.goto('/players')
  const playersResponse = await playersResponsePromise
  expect(playersResponse.status()).toBe(200)
})

test('AUTH-BOOTSTRAP-04 bootstrap generates distinct email per test', async () => {
  const secondSession = bootstrapDmSession()
  expect(secondSession.email).not.toBe(dmSession.email)
})
