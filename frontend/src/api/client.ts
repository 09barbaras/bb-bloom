// Every request goes to a relative `/api/...` URL. In development Vite proxies it to the
// backend (see vite.config.ts), so there is no base URL and no CORS to configure.

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function errorMessage(response: Response): Promise<string> {
  try {
    // FastAPI sends errors as { "detail": "..." }
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
  } catch {
    // the body wasn't JSON; fall through
  }
  return response.statusText || `HTTP ${response.status}`
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // fetch only rejects on network failures; HTTP errors (4xx/5xx) are turned into ApiError here.
  const response = await fetch(path, { ...init, headers })
  if (!response.ok) throw new ApiError(response.status, await errorMessage(response))
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, {
      method: 'POST',
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
}
