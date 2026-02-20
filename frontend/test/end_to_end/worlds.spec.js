import { expect, test } from '@playwright/test'

import { fillCharacterFormAndSubmit } from './helpers/characterForm.js'

const worldTabs = (page) => page.locator('.world-tab')
const activeWorldTab = (page) => page.locator('.world-tab.active')

const getWorldTabNumber = async (tab) => {
  const text = ((await tab.textContent()) || '').trim()
  const match = text.match(/\d+/)
  if (!match) {
    throw new Error(`Could not read world number from tab text: '${text}'`)
  }
  return Number(match[0])
}

test('WORLDS-CREATE-CHARACTER-DELETE-01 creates non-default world, saves character, then deletes world', async ({
  page,
}, testInfo) => {
  let createdWorldId = null
  let deletedWorld = false

  try {
    const initialWorldsResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/worlds') && response.request().method() === 'GET'
    })
    const initialCharactersResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
    })

    await page.goto('/characters')

    const initialWorldsResponse = await initialWorldsResponsePromise
    expect(initialWorldsResponse.status()).toBe(200)
    const initialCharactersResponse = await initialCharactersResponsePromise
    expect(initialCharactersResponse.status()).toBe(200)

    const baselineWorldTabCount = await worldTabs(page).count()
    expect(baselineWorldTabCount).toBeGreaterThan(0)

    const baselineActiveWorldNumber = await getWorldTabNumber(activeWorldTab(page))
    expect(baselineActiveWorldNumber).toBeGreaterThan(0)

    const createWorldResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/worlds') && response.request().method() === 'POST'
    })
    const postCreateCharactersResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
    })

    await page.locator('.add-world-tab').click()

    const createWorldResponse = await createWorldResponsePromise
    expect(createWorldResponse.status()).toBe(200)
    const createWorldJson = await createWorldResponse.json()
    createdWorldId = createWorldJson.id
    expect(Number(createdWorldId)).toBeGreaterThan(0)

    await expect(worldTabs(page)).toHaveCount(baselineWorldTabCount + 1)

    const newActiveWorldNumber = await getWorldTabNumber(activeWorldTab(page))
    expect(newActiveWorldNumber).toBe(baselineWorldTabCount + 1)
    expect(newActiveWorldNumber).not.toBe(1)

    const postCreateCharactersResponse = await postCreateCharactersResponsePromise
    expect(postCreateCharactersResponse.status()).toBe(200)

    await page.getByRole('button', { name: 'Add Character' }).click()

    const uniqueSuffix = `${Date.now().toString().slice(-6)}-${testInfo.project.name === 'webkit' ? 'w' : 'c'}`
    const characterName = `Auto World Char ${uniqueSuffix}`
    const characterData = {
      name: characterName,
      profession: `Auto Profession ${uniqueSuffix}`,
      background: `Auto background ${uniqueSuffix} in non-default world.`,
      motivation: `Auto motivation ${uniqueSuffix} for save verification.`,
      voiceId: 'en-US-Chirp3-HD-Charon',
      voiceDisplayName: 'Manual Voice (en-US-Chirp3-HD-Charon)',
    }

    const createCharacterResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/characters') && response.request().method() === 'POST'
    })

    await fillCharacterFormAndSubmit(page, { mode: 'create', data: characterData })

    const createCharacterResponse = await createCharacterResponsePromise
    expect(createCharacterResponse.status()).toBe(200)
    const createdCharacterJson = await createCharacterResponse.json()
    expect(createdCharacterJson.name).toBe(characterName)

    await expect(page.getByText('Character created successfully!')).toBeVisible()
    await expect(
      page.locator('.list-content .list-item', { hasText: characterName }).first()
    ).toBeVisible()

    const reloadWorldsResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/worlds') && response.request().method() === 'GET'
    })
    const reloadCharactersResponsePromise = page.waitForResponse((response) => {
      return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
    })
    await page.reload()
    const reloadWorldsResponse = await reloadWorldsResponsePromise
    expect(reloadWorldsResponse.status()).toBe(200)
    const reloadCharactersResponse = await reloadCharactersResponsePromise
    expect(reloadCharactersResponse.status()).toBe(200)

    await expect(worldTabs(page)).toHaveCount(baselineWorldTabCount + 1)
    const reloadedNewWorldTab = worldTabs(page).last()
    const isNewWorldActiveAfterReload = await reloadedNewWorldTab.evaluate((element) =>
      element.classList.contains('active')
    )
    if (!isNewWorldActiveAfterReload) {
      const switchToNewWorldCharactersResponsePromise = page.waitForResponse((response) => {
        return response.url().endsWith('/api/characters') && response.request().method() === 'GET'
      })
      await reloadedNewWorldTab.click()
      const switchToNewWorldCharactersResponse = await switchToNewWorldCharactersResponsePromise
      expect(switchToNewWorldCharactersResponse.status()).toBe(200)
    }

    await expect(
      page.locator('.list-content .list-item', { hasText: characterName }).first()
    ).toBeVisible()

    page.once('dialog', (dialog) => dialog.accept())

    const deleteWorldResponsePromise = page.waitForResponse((response) => {
      return (
        response.url().endsWith(`/api/worlds/${createdWorldId}`) &&
        response.request().method() === 'DELETE'
      )
    })

    await activeWorldTab(page).locator('.delete-btn').click()

    const deleteWorldResponse = await deleteWorldResponsePromise
    expect(deleteWorldResponse.status()).toBe(204)
    deletedWorld = true

    await expect(worldTabs(page)).toHaveCount(baselineWorldTabCount)

    if ((await activeWorldTab(page).count()) > 0) {
      const activeAfterDelete = await getWorldTabNumber(activeWorldTab(page))
      expect(activeAfterDelete).not.toBe(newActiveWorldNumber)
    }
  } finally {
    if (createdWorldId && !deletedWorld) {
      const cleanupResponse = await page.request.delete(`/api/worlds/${createdWorldId}`, {
        headers: {
          'X-World-Id': String(createdWorldId),
        },
      })

      if (![204, 404].includes(cleanupResponse.status())) {
        throw new Error(
          `World cleanup failed for world ${createdWorldId} with status ${cleanupResponse.status()}`
        )
      }
    }
  }
})
