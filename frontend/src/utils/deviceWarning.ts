export const shouldShowDeviceWarning = (width, alreadyShown, minWidth = 1000) => {
  if (alreadyShown) return false
  return width < minWidth
}
