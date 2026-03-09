import { describe, expect, it } from 'vitest'
import { DEVICE_WARNING_MIN_WIDTH, shouldShowDeviceWarning } from '../../src/utils/deviceWarning'

describe('shouldShowDeviceWarning', () => {
  it('returns true for iPhone 12 width when not already shown', () => {
    expect(shouldShowDeviceWarning(390, false)).toBe(true)
  })

  it('returns false for iPhone 12 width when already shown', () => {
    expect(shouldShowDeviceWarning(390, true)).toBe(false)
  })

  it('returns false at or above the minimum width', () => {
    expect(shouldShowDeviceWarning(DEVICE_WARNING_MIN_WIDTH, false)).toBe(false)
    expect(shouldShowDeviceWarning(1200, false)).toBe(false)
  })
})
