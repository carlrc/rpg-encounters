import type { TestInfo } from '@playwright/test'
import { bootstrapDmSession, type DmSession } from './bootstrapDm'

const specDmCache = new Map<string, DmSession>()

export const getSpecDmSession = (testInfo: TestInfo): DmSession => {
  const key = testInfo.file || 'unknown-spec'
  const cached = specDmCache.get(key)
  if (cached) {
    return cached
  }
  const session = bootstrapDmSession()
  specDmCache.set(key, session)
  return session
}
