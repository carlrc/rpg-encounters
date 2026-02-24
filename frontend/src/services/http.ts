import { useWorldStore } from '@/stores/world'
import { useAuthStore } from '@/stores/auth'

const request = async (method, url, body, { signal } = {}) => {
  // Get current world ID from store
  const worldStore = useWorldStore()
  const authStore = useAuthStore()

  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}${url}`, {
    method,
    signal,
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
      'X-World-Id': worldStore.currentWorldId,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.ok) {
    authStore.setAuthenticated(true)
  } else if (res.status === 401 || res.status === 403) {
    authStore.setAuthenticated(false)
    // Use Vue Router for navigation to allow proper component cleanup
    // Lazy load router to avoid circular dependency
    const router = (await import('../router')).default
    const currentRoute = router.currentRoute.value
    if (
      currentRoute.path !== '/' &&
      currentRoute.path !== '/login' &&
      currentRoute.path !== '/auth'
    ) {
      router.push('/login')
    }
  }

  // Other client/server errors - let caller handle
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`)
  }

  if (res.status === 204) return null
  return res.json()
}

export const http = {
  get: (url, opts) => request('GET', url, undefined, opts),
  post: (url, body, opts) => request('POST', url, body, opts),
  put: (url, body, opts) => request('PUT', url, body, opts),
  delete: (url, opts) => request('DELETE', url, undefined, opts),
}
