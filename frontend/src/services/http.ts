import { useWorldStore } from '../stores/world'
import { useAuthStore } from '../stores/auth'

type RequestOpts = {
  signal?: AbortSignal
}

const request = async <T>(
  method: string,
  url: string,
  body?: unknown,
  { signal }: RequestOpts = {}
): Promise<T> => {
  const worldStore = useWorldStore()
  const authStore = useAuthStore()

  const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}${url}`, {
    method,
    signal,
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
      'X-World-Id': String(worldStore.currentWorldId),
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

  if (res.status === 204) return null as T
  return (await res.json()) as T
}

export const http = {
  get: <T>(url: string, opts?: RequestOpts) => request<T>('GET', url, undefined, opts),
  post: <T>(url: string, body?: unknown, opts?: RequestOpts) => request<T>('POST', url, body, opts),
  put: <T>(url: string, body?: unknown, opts?: RequestOpts) => request<T>('PUT', url, body, opts),
  delete: <T>(url: string, opts?: RequestOpts) => request<T>('DELETE', url, undefined, opts),
}
