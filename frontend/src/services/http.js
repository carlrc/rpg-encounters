import { useWorldStore } from '@/stores/world'

const request = async (method, url, body, { signal } = {}) => {
  // Get current world ID from store
  const worldStore = useWorldStore()

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

  // Redirect to login on any 4xx error
  if (res.status >= 400 && res.status < 500) {
    // Don't redirect if already on login page
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    const error = new Error(`HTTP error! status: ${res.status}`)
    throw error
  }

  if (!res.ok) {
    const error = new Error(`HTTP error! status: ${res.status}`)
    throw error
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
