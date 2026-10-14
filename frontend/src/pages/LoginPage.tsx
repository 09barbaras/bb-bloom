import { useState, type FormEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api, unwrap } from '../api/client'
import { useAuth } from '../auth-context'

type Mode = 'login' | 'signup'

export function LoginPage() {
  const { logIn } = useAuth()
  const [mode, setMode] = useState<Mode>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const submit = useMutation({
    mutationFn: async () => {
      if (mode === 'signup') {
        return unwrap(await api.POST('/api/auth/signup', { body: { name, email, password } }))
      }
      // The token endpoint uses the OAuth2 form format: username + password.
      return unwrap(
        await api.POST('/api/auth/token', {
          body: { username: email, password, scope: '' },
          bodySerializer: (body) => new URLSearchParams(body as Record<string, string>),
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
      )
    },
    onSuccess: (token) => logIn(token.access_token),
  })

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    submit.mutate()
  }

  return (
    <main className="page page--narrow">
      <header className="brand">
        <img src="/favicon.svg" alt="" width={56} height={56} />
        <h1>BB Bloom</h1>
        <p className="muted">Sleeps, feeds and everything in between.</p>
      </header>

      <form className="card stack" onSubmit={onSubmit}>
        {mode === 'signup' && (
          <label className="field">
            <span>Your name</span>
            <input value={name} onChange={(e) => setName(e.target.value)} required autoComplete="name" />
          </label>
        )}
        <label className="field">
          <span>Email</span>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={mode === 'signup' ? 8 : undefined}
            autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
          />
        </label>

        {submit.error && <p className="error">{submit.error.message}</p>}

        <button className="button button--primary" disabled={submit.isPending}>
          {mode === 'login' ? 'Log in' : 'Create account'}
        </button>
        <button
          type="button"
          className="button button--ghost"
          onClick={() => {
            setMode(mode === 'login' ? 'signup' : 'login')
            submit.reset()
          }}
        >
          {mode === 'login' ? 'New here? Create an account' : 'Already have an account? Log in'}
        </button>
      </form>
    </main>
  )
}
