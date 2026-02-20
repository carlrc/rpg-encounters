import { describe, expect, it } from 'vitest'
import { getInitials } from '../../src/utils/avatarUtils.js'

describe('getInitials', () => {
  it('skips symbol prefixes and derives clean initials', () => {
    expect(getInitials('♂ Finnian')).toBe('F')
    expect(getInitials('♀️ Auto Character')).toBe('AC')
  })

  it('returns a fallback for empty or symbol-only names', () => {
    expect(getInitials('⚔️')).toBe('?')
    expect(getInitials('')).toBe('?')
  })
})
