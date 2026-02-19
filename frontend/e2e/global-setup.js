import { execFileSync } from 'node:child_process'
import { mkdirSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FRONTEND_ROOT = path.resolve(__dirname, '..')
const BACKEND_ROOT = path.resolve(FRONTEND_ROOT, '..', 'backend')
const AUTH_DIR = path.resolve(__dirname, '.auth')
const AUTH_STATE_PATH = path.resolve(AUTH_DIR, 'dm.json')
const BACKEND_HEALTH_URL = 'http://localhost:8000/internal/health'
const FRONTEND_HEALTH_URL = 'http://localhost:3001'

const requiredFields = ['cookie_name', 'cookie_value', 'world_id', 'user_id', 'email']

const parseBootstrapJson = (stdout) => {
  const trimmed = stdout.trim()
  if (!trimmed) {
    throw new Error('Bootstrap script returned empty stdout.')
  }

  let payload
  try {
    payload = JSON.parse(trimmed)
  } catch (error) {
    throw new Error(`Bootstrap script returned non-JSON stdout:\n${trimmed}`)
  }

  for (const field of requiredFields) {
    if (!(field in payload) || payload[field] === '' || payload[field] === null) {
      throw new Error(`Bootstrap payload missing required field '${field}'.`)
    }
  }

  return payload
}

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

  let stdout
  try {
    stdout = execFileSync('uv', ['run', 'python', 'scripts/get_seeded_dm_session.py'], {
      cwd: BACKEND_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    })
  } catch (error) {
    const stderr = error?.stderr?.toString()?.trim()
    const output = stderr || error.message
    throw new Error(`DM auth bootstrap failed:\n${output}`)
  }

  const payload = parseBootstrapJson(stdout)

  const storageState = {
    cookies: [
      {
        name: payload.cookie_name,
        value: payload.cookie_value,
        domain: 'localhost',
        path: '/',
        expires: -1,
        httpOnly: false,
        secure: false,
        sameSite: 'Lax',
      },
    ],
    origins: [],
  }

  mkdirSync(AUTH_DIR, { recursive: true })
  writeFileSync(AUTH_STATE_PATH, JSON.stringify(storageState, null, 2), 'utf8')
}
