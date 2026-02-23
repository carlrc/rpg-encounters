import { expect, test } from '@playwright/test'

const LIST_ITEM_SELECTOR = '.list-content .list-item'

const SCREENS_WITH_SEARCH = [
  { route: '/players', endpointRegex: /\/api\/players$/ },
  { route: '/characters', endpointRegex: /\/api\/characters$/ },
  { route: '/memories', endpointRegex: /\/api\/memories$/ },
  { route: '/reveals', endpointRegex: /\/api\/reveals$/ },
]

const SCREENS_WITH_ALIGNMENT = [
  { route: '/characters', endpoint: '/api/characters', type: 'characters' },
  { route: '/memories', endpoint: '/api/memories', type: 'memories' },
  { route: '/reveals', endpoint: '/api/reveals', type: 'reveals' },
]

const normalizeWhitespace = (text) => text.replace(/\s+/g, ' ').trim()

const readVisibleListTexts = async (page) => {
  const items = page.locator(LIST_ITEM_SELECTOR)
  const count = await items.count()
  const texts = []
  for (let i = 0; i < count; i += 1) {
    const text = normalizeWhitespace((await items.nth(i).innerText()) || '')
    if (text) texts.push(text)
  }
  return { count: texts.length, texts }
}

const pickDynamicSearchQuery = (texts) => {
  if (!texts.length) {
    throw new Error('Cannot derive search query from an empty list.')
  }

  const tokenFrequency = new Map()
  for (const text of texts) {
    const tokens = text
      .toLowerCase()
      .split(/[^a-z0-9']+/)
      .map((token) => token.trim())
      .filter((token) => token.length >= 3)
    for (const token of tokens) {
      tokenFrequency.set(token, (tokenFrequency.get(token) || 0) + 1)
    }
  }

  const total = texts.length
  let selectedToken = ''
  let selectedFrequency = Number.MAX_SAFE_INTEGER

  for (const [token, frequency] of tokenFrequency.entries()) {
    if (frequency > 0 && frequency < total && frequency < selectedFrequency) {
      selectedToken = token
      selectedFrequency = frequency
    }
  }

  return selectedToken || texts[0]
}

const waitForEntityListResponse = async (page, endpointRegex) => {
  const response = await page.waitForResponse((candidate) => {
    return endpointRegex.test(candidate.url()) && candidate.request().method() === 'GET'
  })
  expect(response.status()).toBe(200)
}

const gotoAndWaitForEntityList = async (page, route, endpointRegex) => {
  const responsePromise = waitForEntityListResponse(page, endpointRegex)
  await page.goto(route)
  await responsePromise
}

const openFilterPanel = async (page) => {
  await page.locator('.filter-toggle-btn').click()
  await expect(page.locator('.attribute-filter-panel')).toBeVisible()
}

const selectFilterTab = async (page, tabName) => {
  await page.locator('.tab-button', { hasText: tabName }).click()
  await expect(
    page.locator('.filter-section h4', { hasText: `Filter by ${tabName}` })
  ).toBeVisible()
}

const toggleFilterOption = async (page, optionLabel) => {
  const option = page.locator('.filter-section .option-item', { hasText: optionLabel }).first()
  await expect(option).toBeVisible()
  await option.locator('input[type="checkbox"]').click()
}

const clearExpandedMultiselect = async (page) => {
  const clearButton = page
    .locator('.filter-section .dropdown-header .header-btn', { hasText: 'Clear' })
    .first()
  await clearButton.click()
}

test('FILTER-SEARCH-01 dynamic search filter works across Players/Characters/Memories/Reveals', async ({
  page,
}) => {
  for (const screen of SCREENS_WITH_SEARCH) {
    await gotoAndWaitForEntityList(page, screen.route, screen.endpointRegex)

    const baseline = await readVisibleListTexts(page)
    expect(baseline.count).toBeGreaterThan(0)

    const query = pickDynamicSearchQuery(baseline.texts)
    await page.locator('.search-input').fill(query)

    await expect.poll(async () => (await readVisibleListTexts(page)).count).toBeGreaterThan(0)

    const filtered = await readVisibleListTexts(page)
    expect(filtered.count).toBeGreaterThan(0)
    expect(filtered.count).toBeLessThanOrEqual(baseline.count)
    for (const text of filtered.texts) {
      expect(text.toLowerCase()).toContain(query.toLowerCase())
    }

    await page.getByTitle('Clear search').click()
    await expect.poll(async () => (await readVisibleListTexts(page)).count).toBe(baseline.count)
  }
})

test('FILTER-ALIGNMENT-01 dynamic alignment filter works across Characters/Memories/Reveals', async ({
  browser,
}) => {
  for (const screen of SCREENS_WITH_ALIGNMENT) {
    const context = await browser.newContext({
      baseURL: 'http://localhost:3001',
      storageState: 'test/end_to_end/.auth/dm.json',
    })
    const page = await context.newPage()

    await gotoAndWaitForEntityList(page, screen.route, new RegExp(`${screen.endpoint}$`))

    const baseline = await readVisibleListTexts(page)
    expect(baseline.count).toBeGreaterThan(0)

    await openFilterPanel(page)
    await selectFilterTab(page, 'Alignment')

    const alignmentOptionTexts = await page
      .locator('.filter-section .option-item .option-text')
      .allInnerTexts()
    const alignments = alignmentOptionTexts.map((text) => normalizeWhitespace(text)).filter(Boolean)
    expect(alignments.length).toBeGreaterThan(0)

    let selectedAlignment = ''
    let filtered = baseline
    for (const alignment of alignments) {
      await toggleFilterOption(page, alignment)
      const candidate = await readVisibleListTexts(page)
      if (candidate.count === 0) {
        await clearExpandedMultiselect(page)
        await expect.poll(async () => (await readVisibleListTexts(page)).count).toBe(baseline.count)
        continue
      }

      // Prefer an option that visibly narrows results.
      if (candidate.count < baseline.count) {
        selectedAlignment = alignment
        filtered = candidate
        break
      }

      // Keep first valid non-empty fallback in case all alignments map to full list.
      if (!selectedAlignment && candidate.count > 0) {
        selectedAlignment = alignment
        filtered = candidate
      }

      await clearExpandedMultiselect(page)
      await expect.poll(async () => (await readVisibleListTexts(page)).count).toBe(baseline.count)
    }
    expect(selectedAlignment.length).toBeGreaterThan(0)

    await expect(
      page.locator('.tab-button', { hasText: 'Alignment' }).locator('.filter-badge')
    ).toBeVisible()
    expect(filtered.count).toBeGreaterThan(0)
    expect(filtered.count).toBeLessThanOrEqual(baseline.count)
    for (const text of filtered.texts) {
      expect(baseline.texts.includes(text)).toBe(true)
    }

    await clearExpandedMultiselect(page)
    await expect.poll(async () => (await readVisibleListTexts(page)).count).toBe(baseline.count)

    await context.close()
  }
})
