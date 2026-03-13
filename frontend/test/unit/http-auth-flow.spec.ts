import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../../src/stores/auth'
import { useWorldStore } from '../../src/stores/world'
import { http } from '../../src/services/http'

// `vi.mock(...)` is hoisted by Vitest, so these mock refs must also be created
// in hoisted scope and then configured/reset inside each test lifecycle.
const { pushMock, currentRoute } = vi.hoisted(() => {
  return {
    pushMock: vi.fn(),
    currentRoute: { value: { path: '/players' } },
  }
})

vi.mock('../../src/router', () => {
  return {
    default: {
      push: pushMock,
      currentRoute,
    },
  }
})

describe('http auth flow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    currentRoute.value.path = '/players'
    pushMock.mockReset()
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.clearAllMocks()
  })

  it('sets auth true and returns json payload on successful request', async () => {
    const worldStore = useWorldStore()
    const authStore = useAuthStore()
    worldStore.setCurrentWorldId(42)

    ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ hello: 'world' }),
    })

    const response = await http.get<{ hello: string }>('/players')

    expect(response.hello).toBe('world')
    expect(authStore.isAuthenticated).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/players'),
      expect.objectContaining({
        headers: expect.objectContaining({ 'X-World-Id': '42' }),
      })
    )
  })

  it('clears auth and redirects to /login on 401 from protected route', async () => {
    const authStore = useAuthStore()
    authStore.setAuthenticated(true)

    ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 401,
      json: vi.fn(),
    })

    await expect(http.get('/players')).rejects.toThrow('HTTP error! status: 401')

    expect(authStore.isAuthenticated).toBe(false)
    expect(pushMock).toHaveBeenCalledWith('/login')
  })

  it('does not redirect on 403 when already on /login', async () => {
    currentRoute.value.path = '/login'

    ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 403,
      json: vi.fn(),
    })

    await expect(http.get('/players')).rejects.toThrow('HTTP error! status: 403')
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('throws on 500 without forcing auth false or redirect', async () => {
    const authStore = useAuthStore()
    authStore.setAuthenticated(true)

    ;(global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      status: 500,
      json: vi.fn(),
    })

    await expect(http.get('/players')).rejects.toThrow('HTTP error! status: 500')

    expect(authStore.isAuthenticated).toBe(true)
    expect(pushMock).not.toHaveBeenCalled()
  })
})
