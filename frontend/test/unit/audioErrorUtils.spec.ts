import { describe, expect, it } from 'vitest'
import { getMicrophoneErrorMessage } from '../../src/composables/audio/audioErrorUtils'

describe('getMicrophoneErrorMessage', () => {
  it('handles NotAllowedError', () => {
    expect(getMicrophoneErrorMessage({ name: 'NotAllowedError' })).toBe(
      'Microphone blocked. Enable it in site settings.'
    )
  })

  it('handles SecurityError', () => {
    expect(getMicrophoneErrorMessage({ name: 'SecurityError' })).toBe(
      'Microphone blocked. Enable it in site settings.'
    )
  })

  it('handles NotFoundError', () => {
    expect(getMicrophoneErrorMessage({ name: 'NotFoundError' })).toBe('No microphone detected.')
  })

  it('handles NotReadableError', () => {
    expect(getMicrophoneErrorMessage({ name: 'NotReadableError' })).toBe(
      'Microphone busy. Close other apps and retry.'
    )
  })

  it('handles AbortError', () => {
    expect(getMicrophoneErrorMessage({ name: 'AbortError' })).toBe(
      'Microphone busy. Close other apps and retry.'
    )
  })

  it('handles unknown errors', () => {
    expect(getMicrophoneErrorMessage({ name: 'OtherError' })).toBe(
      'Could not start audio. Refresh the page and try again.'
    )
    expect(getMicrophoneErrorMessage(null)).toBe(
      'Could not start audio. Refresh the page and try again.'
    )
  })
})
