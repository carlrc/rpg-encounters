export const getMicrophoneErrorMessage = (error: unknown): string => {
  const name = (error as { name?: string })?.name
  if (name === 'NotAllowedError' || name === 'SecurityError') {
    return 'Microphone blocked. Enable it in site settings.'
  }
  if (name === 'NotFoundError') {
    return 'No microphone detected.'
  }
  if (name === 'NotReadableError' || name === 'AbortError') {
    return 'Microphone busy. Close other apps and retry.'
  }
  return 'Could not start audio. Refresh the page and try again.'
}
