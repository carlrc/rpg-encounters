export const resolveBaseUrl = (testInfo) => {
  const baseUrl = testInfo?.project?.use?.baseURL
  if (!baseUrl) {
    throw new Error(
      `Playwright baseURL is not configured for project '${testInfo?.project?.name || 'unknown'}'.`
    )
  }
  return baseUrl
}

export const toAbsoluteUrl = (pathOrUrl, testInfo) => {
  return new URL(pathOrUrl, resolveBaseUrl(testInfo)).toString()
}
