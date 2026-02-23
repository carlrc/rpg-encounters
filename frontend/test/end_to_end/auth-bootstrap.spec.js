import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect, test } from '@playwright/test'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BACKEND_ROOT = path.resolve(__dirname, '..', '..', '..', 'backend')
const bootstrapCommand = ['run', 'python', 'scripts/get_seeded_dm_session.py']

test('AUTH-BOOTSTRAP-01 CLI returns valid JSON contract', async () => {
  const stdout = execFileSync('uv', bootstrapCommand, {
    cwd: BACKEND_ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379/0',
    },
  })

  const payload = JSON.parse(stdout.trim())
  for (const key of ['cookie_name', 'cookie_value', 'world_id', 'user_id', 'email']) {
    expect(payload).toHaveProperty(key)
  }
  expect(String(payload.cookie_name).length).toBeGreaterThan(0)
  expect(String(payload.cookie_value).length).toBeGreaterThan(0)
  expect(Number(payload.world_id)).toBeGreaterThan(0)
  expect(Number(payload.user_id)).toBeGreaterThan(0)
  expect(payload.email).toBe('test1@example.com')
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

test('AUTH-BOOTSTRAP-04 missing seeded DM fails clearly', async () => {
  const missingEmail = 'does-not-exist-for-playwright-auth@example.com'

  try {
    execFileSync('uv', bootstrapCommand, {
      cwd: BACKEND_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PLAYWRIGHT_SEEDED_DM_EMAIL: missingEmail,
        REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379/0',
      },
    })
    throw new Error('Expected bootstrap command to fail for missing seeded DM.')
  } catch (error) {
    const stderr = error?.stderr?.toString() || error.message || ''
    expect(stderr).toContain(`Seeded DM account '${missingEmail}' not found`)
    expect(stderr).toContain('python -m tests.fixtures.seed_data')
  }
})
