import { expect } from '@playwright/test'

export const runSpeakStopLifecycle = async (
  page,
  {
    speakLabel = 'Speak',
    stopLabel = 'Stop',
    listeningText = 'Listening',
    processingText = 'Processing',
    captureMs = 1200,
    clickWithEvaluate = false,
  } = {}
) => {
  const speakButton = page.getByRole('button', { name: speakLabel })
  await expect(speakButton).toBeEnabled()

  if (clickWithEvaluate) {
    await speakButton.evaluate((element) => element.click())
  } else {
    await speakButton.click()
  }

  const stopButton = page.getByRole('button', { name: stopLabel })
  await expect(stopButton).toBeVisible()
  await expect(page.locator('.shared-status-text')).toContainText(listeningText)
  await page.waitForTimeout(captureMs)

  if (clickWithEvaluate) {
    await stopButton.evaluate((element) => element.click())
  } else {
    await stopButton.click()
  }
  await expect(page.locator('.shared-speak-button')).toContainText(processingText)
}

export const assertReturnedToReadyState = async (
  page,
  { speakLabel = 'Speak', readyTextPattern = /Tap Speak|Click Speak/, timeoutMs = 60_000 } = {}
) => {
  await expect(page.getByRole('button', { name: speakLabel })).toBeVisible({ timeout: timeoutMs })
  await expect(page.locator('.shared-status-text')).toContainText(readyTextPattern, {
    timeout: timeoutMs,
  })
}
