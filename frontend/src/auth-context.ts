import { createContext, use } from 'react'

export type AuthContextValue = {
  isLoggedIn: boolean
  logIn: (token: string) => void
  logOut: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const value = use(AuthContext)
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>')
  return value
}
