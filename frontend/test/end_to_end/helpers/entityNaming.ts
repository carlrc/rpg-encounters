const sanitize = (value) => {
  return String(value || 'unknown')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export const makeScopedSuffix = (testInfo) => {
  const projectName = sanitize(testInfo?.project?.name)
  return `${projectName}-${Date.now()}`
}

export const makeScopedName = (testInfo, prefix) => {
  return `${prefix} ${makeScopedSuffix(testInfo)}`
}
