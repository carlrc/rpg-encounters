import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { v4 as uuidv4 } from 'uuid'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BACKEND_ROOT = path.resolve(__dirname, '..', '..', '..', '..', 'backend')
const BACKEND_PYTHON = path.resolve(BACKEND_ROOT, '.venv', 'bin', 'python')
const requiredFields = ['cookie_name', 'cookie_value', 'world_id', 'user_id', 'email']

export type DmSession = {
  email: string
  cookie_name: string
  cookie_value: string
  world_id: number
  user_id: number
}

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

export const bootstrapDmSession = (): DmSession => {
  const email = `test+${uuidv4()}@example.com`
  let stdout
  try {
    stdout = execFileSync(
      BACKEND_PYTHON,
      ['tests/scripts/get_seeded_dm_session.py', '--email', email],
      {
        cwd: BACKEND_ROOT,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'],
        env: {
          ...process.env,
          REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379/0',
        },
      }
    )
  } catch (error) {
    const stderr = error?.stderr?.toString()?.trim()
    const output = stderr || error.message
    throw new Error(`DM auth bootstrap failed:\n${output}`)
  }

  const payload = parseBootstrapJson(stdout)
  if (payload.email !== email) {
    throw new Error(`Bootstrap email mismatch: expected ${email}, got ${payload.email}`)
  }

  return {
    email,
    cookie_name: payload.cookie_name,
    cookie_value: payload.cookie_value,
    world_id: payload.world_id,
    user_id: payload.user_id,
  }
}

export const applyDmSession = async (page, dmSession: DmSession) => {
  await page.context().addCookies([
    {
      name: dmSession.cookie_name,
      value: dmSession.cookie_value,
      domain: 'localhost',
      path: '/',
      expires: -1,
      httpOnly: false,
      secure: false,
      sameSite: 'Lax',
    },
  ])
}
