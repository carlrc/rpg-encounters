import { expect } from '@playwright/test'

export const waitForApiResponse = async (
  page,
  { method, pathRegex, expectedStatus = 200, timeout = 30_000 }
) => {
  const response = await page.waitForResponse(
    (candidate) => {
      return pathRegex.test(candidate.url()) && candidate.request().method() === method
    },
    { timeout }
  )

  expect(response.status()).toBe(expectedStatus)
  return response
}
