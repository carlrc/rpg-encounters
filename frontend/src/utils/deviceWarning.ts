export const DEVICE_WARNING_MIN_WIDTH = 768

export const shouldShowDeviceWarning = (
  width,
  alreadyShown,
  minWidth = DEVICE_WARNING_MIN_WIDTH
) => {
  if (alreadyShown) return false
  return width < minWidth
}
