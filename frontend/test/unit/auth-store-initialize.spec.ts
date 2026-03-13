import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../../src/stores/auth'
import { useWorldStore } from '../../src/stores/world'

// `vi.mock(...)` is hoisted by Vitest, so these mock refs must also be created
// in hoisted scope and then configured per test with `mockResolvedValue(...)`.
const { checkAuthMock, getWorldsMock } = vi.hoisted(() => {
  return {
    checkAuthMock: vi.fn(),
    getWorldsMock: vi.fn(),
  }
})

vi.mock('../../src/services/api', () => {
  return {
    checkAuth: checkAuthMock,
    getWorlds: getWorldsMock,
  }
})

describe('auth store initializeAuth', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    checkAuthMock.mockReset()
    getWorldsMock.mockReset()
  })

  it('sets authenticated and loads first world on happy path', async () => {
    checkAuthMock.mockResolvedValue(true)
    getWorldsMock.mockResolvedValue([{ id: 7 }, { id: 11 }])

    const authStore = useAuthStore()
    const worldStore = useWorldStore()

    await authStore.initializeAuth()

    expect(authStore.isInitialized).toBe(true)
    expect(authStore.isAuthenticated).toBe(true)
    expect(worldStore.currentWorldId).toBe(7)
  })

  it('sets authenticated false when auth is true but no worlds are returned', async () => {
    checkAuthMock.mockResolvedValue(true)
    getWorldsMock.mockResolvedValue([])

    const authStore = useAuthStore()

    await authStore.initializeAuth()

    expect(authStore.isInitialized).toBe(true)
    expect(authStore.isAuthenticated).toBe(false)
  })

  it('keeps unauthenticated state when checkAuth returns false', async () => {
    checkAuthMock.mockResolvedValue(false)

    const authStore = useAuthStore()
    const worldStore = useWorldStore()

    await authStore.initializeAuth()

    expect(authStore.isInitialized).toBe(true)
    expect(authStore.isAuthenticated).toBe(false)
    expect(worldStore.currentWorldId).toBe(null)
    expect(getWorldsMock).not.toHaveBeenCalled()
  })
})
