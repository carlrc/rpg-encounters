import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { createEntityStore } from '../../src/composables/useEntityStore'
import { useNotificationStore } from '../../src/stores/notifications'
import { useWorldStore } from '../../src/stores/world'

describe('createEntityStore world switch and errors', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('reloads entities on world changes and clears when world is unset', async () => {
    const apiMethods = {
      getAll: vi
        .fn()
        .mockResolvedValueOnce([{ id: 1, name: 'First' }])
        .mockResolvedValueOnce([{ id: 2, name: 'Second' }]),
      getOne: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    }

    const useTestStore = createEntityStore<
      { id: number; name: string },
      { name: string },
      { name: string }
    >('TestEntity', apiMethods)

    const worldStore = useWorldStore()
    const store = useTestStore()

    worldStore.setCurrentWorldId(1)
    await nextTick()
    await Promise.resolve()

    expect(apiMethods.getAll).toHaveBeenCalledTimes(1)
    expect(store.entities).toEqual([{ id: 1, name: 'First' }])

    worldStore.setCurrentWorldId(null)
    await nextTick()

    expect(store.entities).toEqual([])

    worldStore.setCurrentWorldId(2)
    await nextTick()
    await Promise.resolve()

    expect(apiMethods.getAll).toHaveBeenCalledTimes(2)
    expect(store.entities).toEqual([{ id: 2, name: 'Second' }])
  })

  it('sets error and shows notification when create fails', async () => {
    const apiMethods = {
      getAll: vi.fn().mockResolvedValue([]),
      getOne: vi.fn(),
      create: vi.fn().mockRejectedValue(new Error('boom')),
      update: vi.fn(),
      delete: vi.fn(),
    }

    const useTestStore = createEntityStore<
      { id: number; name: string },
      { name: string },
      { name: string }
    >('TestEntity', apiMethods)

    const store = useTestStore()
    const notifications = useNotificationStore()

    await expect(store.createEntity({ name: 'Broken' })).rejects.toThrow('boom')

    expect(store.error).toContain('Failed to create testentity. Please check your input.')
    expect(notifications.notifications.length).toBeGreaterThan(0)
    expect(notifications.notifications[0].type).toBe('error')
  })
})
