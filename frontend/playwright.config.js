import { defineConfig } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  globalSetup: path.resolve(__dirname, 'e2e/global-setup.js'),
  use: {
    baseURL: 'http://localhost:3001',
    storageState: path.resolve(__dirname, 'e2e/.auth/dm.json'),
    trace: 'retain-on-failure',
  },
})
