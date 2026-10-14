// Typed API client.
//
// `schema.d.ts` is generated from FastAPI's OpenAPI description with
// `npm run gen:api`. openapi-fetch uses it so that paths, params, bodies and
// responses are all type-checked: if you rename a field in a Pydantic schema
// and regenerate, TypeScript points at every place in the UI that breaks.
import createClient, { type Middleware } from 'openapi-fetch'
import type { components, paths } from './schema'

export type Schemas = components['schemas']
export type EventRead = Schemas['EventRead']
export type EventType = Schemas['EventType']
export type EventCreate =
  | Schemas['SleepEventCreate']
  | Schemas['FeedingEventCreate']
  | Schemas['DiaperEventCreate']
  | Schemas['SymptomEventCreate']
  | Schemas['MedicationEventCreate']

const TOKEN_KEY = 'bb-bloom-token'
export const LOGOUT_EVENT = 'bb-bloom:logout'

// localStorage can throw (private mode, blocked storage), so guard every access.
export const tokenStorage = {
  get(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch {
      return null
    }
  },
  set(token: string) {
    try {
      localStorage.setItem(TOKEN_KEY, token)
    } catch {
      /* ignore */
    }
  },
  clear() {
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {
      /* ignore */
    }
  },
}

const authMiddleware: Middleware = {
  onRequest({ request }) {
    const token = tokenStorage.get()
    if (token) request.headers.set('Authorization', `Bearer ${token}`)
    return request
  },
  onResponse({ response }) {
    // An expired token anywhere logs the user out.
    if (response.status === 401 && tokenStorage.get()) {
      tokenStorage.clear()
      window.dispatchEvent(new Event(LOGOUT_EVENT))
    }
    return response
  },
}

export const api = createClient<paths>({ baseUrl: window.location.origin })
api.use(authMiddleware)

export class ApiError extends Error {}

// FastAPI errors look like {"detail": "text"} or {"detail": [{"msg": ...}, ...]}.
function errorMessage(error: unknown): string {
  const detail = (error as { detail?: unknown } | undefined)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item: { loc?: unknown[]; msg?: string }) => {
        const field = item.loc?.at(-1)
        return field && field !== 'body' ? `${String(field)}: ${item.msg}` : item.msg
      })
      .join('\n')
  }
  return 'Something went wrong'
}

// openapi-fetch returns { data, error } instead of throwing. TanStack Query wants
// a thrown error, so this turns the error branch into an exception.
export function unwrap<T>(result: { data?: T; error?: unknown }): T {
  if (result.error !== undefined) throw new ApiError(errorMessage(result.error))
  return result.data as T
}
