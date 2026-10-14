import { useEffect, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { LOGOUT_EVENT, tokenStorage } from './api/client'
import { AuthContext, type AuthContextValue } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => tokenStorage.get())
  const queryClient = useQueryClient()

  useEffect(() => {
    const onLogout = () => setToken(null)
    window.addEventListener(LOGOUT_EVENT, onLogout)
    return () => window.removeEventListener(LOGOUT_EVENT, onLogout)
  }, [])

  const value: AuthContextValue = {
    isLoggedIn: token !== null,
    logIn(newToken) {
      tokenStorage.set(newToken)
      setToken(newToken)
    },
    logOut() {
      tokenStorage.clear()
      queryClient.clear() // don't leave one user's data cached for the next
      setToken(null)
    },
  }

  return <AuthContext value={value}>{children}</AuthContext>
}
