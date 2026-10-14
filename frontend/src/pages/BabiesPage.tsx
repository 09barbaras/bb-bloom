import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router'
import { api, unwrap } from '../api/client'
import { useAuth } from '../auth-context'
import { ageLabel } from '../lib/time'

export function BabiesPage() {
  const { logOut } = useAuth()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [searchParams] = useSearchParams()
  const showAll = searchParams.has('all')
  const navigate = useNavigate()

  const babies = useQuery({
    queryKey: ['babies'],
    queryFn: async () => unwrap(await api.GET('/api/babies')),
  })

  const addBaby = useMutation({
    mutationFn: async () =>
      unwrap(await api.POST('/api/babies', { body: { name, birth_date: birthDate } })),
    onSuccess: (baby) => {
      queryClient.invalidateQueries({ queryKey: ['babies'] })
      navigate(`/babies/${baby.id}`)
    },
  })

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    addBaby.mutate()
  }

  if (babies.isPending) return <main className="page"><p className="muted">Loading…</p></main>
  if (babies.error) return <main className="page"><p className="error">{babies.error.message}</p></main>

  // With exactly one baby (the usual case) go straight to the tracker,
  // unless we came here on purpose from the "Babies" link (?all=1).
  if (babies.data.length === 1 && !showAll) {
    return <Navigate to={`/babies/${babies.data[0].id}`} replace />
  }

  return (
    <main className="page page--narrow">
      <div className="topbar">
        <h1>Your babies</h1>
        <button className="button button--ghost button--small" onClick={logOut}>Log out</button>
      </div>

      {babies.data.length > 0 && (
        <ul className="list">
          {babies.data.map((baby) => (
            <li key={baby.id}>
              <Link className="card card--link" to={`/babies/${baby.id}`}>
                <strong>{baby.name}</strong>
                <span className="muted">{ageLabel(baby.birth_date)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <form className="card stack" onSubmit={onSubmit}>
        <h2>{babies.data.length === 0 ? 'Add your baby to get started' : 'Add another baby'}</h2>
        <label className="field">
          <span>Name</span>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label className="field">
          <span>Birth date</span>
          <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} required />
        </label>
        {addBaby.error && <p className="error">{addBaby.error.message}</p>}
        <button className="button button--primary" disabled={addBaby.isPending}>Add baby</button>
      </form>
    </main>
  )
}
