import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const BACKEND_ROOT = path.resolve(__dirname, '..', '..', '..', 'backend')

const toRequiredInt = (name, value) => {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    throw new Error(`Expected ${name} to be a finite number, got: ${value}`)
  }
  return String(parsed)
}

export const setUserBillingState = ({
  email = null,
  userId = null,
  availableTokens,
  lastUsedTokens,
  totalUsedTokens = null,
}) => {
  const hasEmail = typeof email === 'string' && email.trim().length > 0
  const hasUserId = userId !== null && userId !== undefined
  if ((hasEmail && hasUserId) || (!hasEmail && !hasUserId)) {
    throw new Error('setUserBillingState requires exactly one target: email or userId')
  }

  const command = [
    'run',
    'python',
    'tests/scripts/set_billing_state.py',
    '--available',
    toRequiredInt('availableTokens', availableTokens),
    '--last-used',
    toRequiredInt('lastUsedTokens', lastUsedTokens),
  ]
  if (hasEmail) {
    command.push('--email', email.trim())
  } else {
    command.push('--user-id', toRequiredInt('userId', userId))
  }
  if (totalUsedTokens !== null && totalUsedTokens !== undefined) {
    command.push('--total-used', toRequiredInt('totalUsedTokens', totalUsedTokens))
  }

  const stdout = execFileSync('uv', command, {
    cwd: BACKEND_ROOT,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379/0',
    },
  })
  const payload = JSON.parse(stdout.trim())
  if (!payload?.user_id) {
    throw new Error('set_billing_state.py returned invalid response: missing user_id')
  }
  return payload
}

export const setSeededDmBilling = ({ availableTokens, lastUsedTokens, totalUsedTokens = null }) => {
  return setUserBillingState({
    email: process.env.PLAYWRIGHT_SEEDED_DM_EMAIL || 'test1@example.com',
    availableTokens,
    lastUsedTokens,
    totalUsedTokens,
  })
}
