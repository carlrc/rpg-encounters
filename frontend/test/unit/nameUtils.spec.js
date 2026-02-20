import { describe, expect, it } from 'vitest'
import { sanitizeDisplayName } from '../../src/utils/nameUtils.js'

describe('sanitizeDisplayName', () => {
  it('removes gender symbols and emoji while preserving words', () => {
    expect(sanitizeDisplayName('♂ Finnian')).toBe('Finnian')
    expect(sanitizeDisplayName('♀️ Auto Character 123')).toBe('Auto Character 123')
  })

  it('preserves allowed punctuation and collapses whitespace', () => {
    expect(sanitizeDisplayName('  Lady   Seraphina-Valerius  ')).toBe('Lady Seraphina-Valerius')
    expect(sanitizeDisplayName("Finnian 'Finn' Swift")).toBe("Finnian 'Finn' Swift")
  })

  it('returns empty string for invalid or symbol-only input', () => {
    expect(sanitizeDisplayName('⚔️ ♀️ ♂️')).toBe('')
    expect(sanitizeDisplayName(null)).toBe('')
  })
})
