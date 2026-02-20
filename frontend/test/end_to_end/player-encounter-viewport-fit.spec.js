import { devices, expect, test } from '@playwright/test'
import { resolveBaseUrl } from './helpers/baseUrl.js'
import { resolveSeededPlayerEncounterFixture } from './helpers/playerEncounterLogin.js'

const TOLERANCE_PX = 2
const STRICT_TOLERANCE_PX = 1
const CRITICAL_CONTROL_SELECTORS = [
  '.close-btn',
  '.challenge-button',
  '.shared-speak-button',
  '.shared-status-text',
]

const getLoginForEncounterWithPlayersAndCharacters = async (page, browser, testInfo) => {
  const fixture = await resolveSeededPlayerEncounterFixture(page, browser, testInfo)
  const playerId = String(fixture.playerId)
  const loginUrl = fixture.loginUrl
  return { loginUrl, playerId }
}

const loginAsPlayerOnMobile = async (browser, loginUrl, playerId, testInfo) => {
  const mobileContext = await browser.newContext({
    ...devices['iPhone 12'],
    storageState: undefined,
    baseURL: resolveBaseUrl(testInfo),
  })
  const mobilePage = await mobileContext.newPage()

  const consumePromise = mobilePage.waitForResponse((response) => {
    return (
      new RegExp(`/api/players/${playerId}/login\\?token=`).test(response.url()) &&
      response.request().method() === 'GET'
    )
  })
  const encounterPromise = mobilePage.waitForResponse((response) => {
    return (
      response.url().endsWith(`/api/players/${playerId}/encounter`) &&
      response.request().method() === 'GET'
    )
  })

  await mobilePage.goto(loginUrl)

  const consumeResponse = await consumePromise
  expect(consumeResponse.status()).toBe(200)

  const encounterResponse = await encounterPromise
  const encounterStatus = encounterResponse.status()

  if (encounterStatus === 200) {
    await expect(mobilePage).toHaveURL(new RegExp(`/players/${playerId}/encounter$`))
  }

  return { mobileContext, mobilePage, encounterStatus, playerId }
}

const getLoginForPlayerWithEncounter = async (page, browser, testInfo) => {
  const login = await getLoginForEncounterWithPlayersAndCharacters(page, browser, testInfo)
  const { mobileContext, mobilePage, encounterStatus, playerId } = await loginAsPlayerOnMobile(
    browser,
    login.loginUrl,
    login.playerId,
    testInfo
  )
  if (encounterStatus !== 200) {
    await mobileContext.close()
    throw new Error(
      `Player encounter login did not return active encounter for seeded fixture player ${playerId}. Status: ${encounterStatus}`
    )
  }

  return { mobileContext, mobilePage, playerId }
}

const collectViewportDiagnostics = async (page) => {
  return page.evaluate((criticalControlSelectors) => {
    const selectSummary = (element) => {
      if (!element) return null
      const idPart = element.id ? `#${element.id}` : ''
      const className = typeof element.className === 'string' ? element.className.trim() : ''
      const classPart = className
        ? `.${className.split(/\s+/).filter(Boolean).slice(0, 3).join('.')}`
        : ''
      return `${element.tagName.toLowerCase()}${idPart}${classPart}`
    }

    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    const visualViewportHeight = window.visualViewport?.height ?? null
    const visualViewportOffsetTop = window.visualViewport?.offsetTop ?? 0
    const effectiveViewportHeight =
      visualViewportHeight === null
        ? viewportHeight
        : Math.min(viewportHeight, visualViewportHeight)

    const panel = document.querySelector('.interaction-panel')
    const panelRect = panel?.getBoundingClientRect()
    const selectors = criticalControlSelectors
    const controls = selectors.map((selector) => {
      const element = document.querySelector(selector)
      const rect = element?.getBoundingClientRect()
      return {
        selector,
        element: selectSummary(element),
        top: rect?.top ?? null,
        bottom: rect?.bottom ?? null,
        left: rect?.left ?? null,
        right: rect?.right ?? null,
        width: rect?.width ?? null,
        height: rect?.height ?? null,
      }
    })

    return {
      url: window.location.href,
      viewportWidth,
      viewportHeight,
      visualViewportHeight,
      visualViewportOffsetTop,
      effectiveViewportHeight,
      scrollY: window.scrollY,
      docScrollWidth: document.documentElement.scrollWidth,
      docScrollHeight: document.documentElement.scrollHeight,
      bodyScrollWidth: document.body.scrollWidth,
      bodyScrollHeight: document.body.scrollHeight,
      panel: panel
        ? {
            x: panelRect?.x ?? null,
            y: panelRect?.y ?? null,
            width: panelRect?.width ?? null,
            height: panelRect?.height ?? null,
            top: panelRect?.top ?? null,
            bottom: panelRect?.bottom ?? null,
            left: panelRect?.left ?? null,
            right: panelRect?.right ?? null,
            scrollTop: panel.scrollTop,
            scrollHeight: panel.scrollHeight,
            clientHeight: panel.clientHeight,
            scrollWidth: panel.scrollWidth,
            clientWidth: panel.clientWidth,
          }
        : null,
      controls,
    }
  }, CRITICAL_CONTROL_SELECTORS)
}

const assertViewportHeightFits = async (page, stageLabel) => {
  const diagnostics = await collectViewportDiagnostics(page)
  const failures = []

  if (diagnostics.panel) {
    if (diagnostics.panel.top < diagnostics.visualViewportOffsetTop - STRICT_TOLERANCE_PX) {
      failures.push('interaction panel starts above viewport')
    }
    if (diagnostics.panel.bottom > diagnostics.effectiveViewportHeight + STRICT_TOLERANCE_PX) {
      failures.push('interaction panel extends below viewport')
    }
    if (diagnostics.panel.scrollHeight <= 0 || diagnostics.panel.clientHeight <= 0) {
      failures.push('interaction panel has invalid height metrics')
    }
    if (diagnostics.panel.scrollTop > STRICT_TOLERANCE_PX) {
      failures.push('interaction panel is vertically scrolled')
    }
    if (diagnostics.scrollY > STRICT_TOLERANCE_PX) {
      failures.push('page is vertically scrolled')
    }
  }

  if (failures.length > 0) {
    throw new Error(
      `${stageLabel} viewport-fit assertion failed: ${failures.join('; ')}. Diagnostics: ${JSON.stringify(
        diagnostics
      )}`
    )
  }
}

const assertCriticalControlsFitWithoutScroll = async (page, stageLabel) => {
  const diagnostics = await collectViewportDiagnostics(page)
  const missingControls = diagnostics.controls.filter((control) => control.top === null)
  if (missingControls.length > 0) {
    throw new Error(
      `${stageLabel} missing critical controls: ${JSON.stringify({
        missing: missingControls.map((control) => control.selector),
        diagnostics,
      })}`
    )
  }

  const outOfViewportControls = diagnostics.controls.filter((control) => {
    return (
      control.top < diagnostics.visualViewportOffsetTop - STRICT_TOLERANCE_PX ||
      control.bottom > diagnostics.effectiveViewportHeight + STRICT_TOLERANCE_PX
    )
  })
  if (outOfViewportControls.length > 0) {
    throw new Error(
      `${stageLabel} critical controls exceed viewport height: ${JSON.stringify({
        controls: outOfViewportControls,
        diagnostics,
      })}`
    )
  }

  if (
    diagnostics.panel?.scrollTop > STRICT_TOLERANCE_PX ||
    diagnostics.scrollY > STRICT_TOLERANCE_PX
  ) {
    throw new Error(
      `${stageLabel} required scrolling to expose critical controls: ${JSON.stringify({
        panelScrollTop: diagnostics.panel?.scrollTop ?? null,
        pageScrollY: diagnostics.scrollY,
        diagnostics,
      })}`
    )
  }
}

test('PLAYER-MOBILE-VIEWPORT-FIT-01 player encounter fits iPhone 12 viewport height with and without interaction panel', async ({
  page,
  browser,
}, testInfo) => {
  let mobileContext
  let mobilePage

  try {
    const loginResult = await getLoginForPlayerWithEncounter(page, browser, testInfo)
    mobileContext = loginResult.mobileContext
    mobilePage = loginResult.mobilePage

    await expect(mobilePage.locator('.encounter-title')).toBeVisible()
    const characterTile = mobilePage.locator('.character-tile').first()
    await expect(characterTile).toBeVisible()

    await assertViewportHeightFits(mobilePage, 'Initial encounter view')

    await characterTile.click()
    await expect(mobilePage.locator('.interaction-panel')).toBeVisible()

    await assertViewportHeightFits(mobilePage, 'Encounter view with interaction panel')
    await assertCriticalControlsFitWithoutScroll(
      mobilePage,
      'Encounter view with interaction panel'
    )
  } catch (error) {
    if (mobilePage) {
      const screenshotPath = testInfo.outputPath('player-encounter-viewport-fit-failure.png')
      await mobilePage.screenshot({ path: screenshotPath, fullPage: true })
      await testInfo.attach('viewport-fit-failure', {
        path: screenshotPath,
        contentType: 'image/png',
      })
    }
    throw error
  } finally {
    if (mobileContext) {
      await mobileContext.close()
    }
  }
})
