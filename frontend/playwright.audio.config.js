import { defineConfig } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FAKE_AUDIO_PATH = path.resolve(__dirname, 'test/mocks/fake-input.wav')

export default defineConfig({
  testDir: './test/end_to_end',
  timeout: 90_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  globalSetup: path.resolve(__dirname, 'test/end_to_end/global-setup.js'),
  use: {
    baseURL: 'http://localhost:3001',
    storageState: path.resolve(__dirname, 'test/end_to_end/.auth/dm.json'),
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        launchOptions: {
          args: [
            '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream',
            `--use-file-for-fake-audio-capture=${FAKE_AUDIO_PATH}`,
          ],
        },
      },
    },
    {
      name: 'webkit',
      use: {
        browserName: 'webkit',
      },
    },
  ],
})
