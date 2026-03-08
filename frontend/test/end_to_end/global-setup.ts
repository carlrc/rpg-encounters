import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FRONTEND_ROOT = path.resolve(__dirname, '..', '..')
const BACKEND_HEALTH_URL = 'http://localhost:8000/internal/health'
const FRONTEND_HEALTH_URL = 'http://localhost:3001'

const assertServiceReachable = async (url, name) => {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Unexpected status ${response.status}`)
    }
  } catch (error) {
    throw new Error(
      `${name} is not reachable at ${url}. Start it before running Playwright. Root error: ${error.message}`
    )
  }
}

export default async function globalSetup() {
  await assertServiceReachable(BACKEND_HEALTH_URL, 'Backend')
  await assertServiceReachable(FRONTEND_HEALTH_URL, 'Frontend')
}
