import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router'
import { api, unwrap, type EventRead, type EventType } from '../api/client'
import { useAuth } from '../auth-context'
import { LogSheet } from '../components/LogSheet'
import { EVENT_LABELS, describeEvent } from '../lib/events'
import {
  ageLabel,
  formatClock,
  formatDuration,
  formatTimer,
  startOfToday,
  timeAgo,
  useNow,
} from '../lib/time'

const EVENT_TYPES = Object.keys(EVENT_LABELS) as EventType[]
const DURATION_TYPES: EventType[] = ['sleep', 'feeding']

export function BabyPage() {
  const babyId = Number(useParams().babyId)
  const { logOut } = useAuth()
  const queryClient = useQueryClient()
  const now = useNow(1000)
  const [openSheet, setOpenSheet] = useState<EventType | null>(null)

  const baby = useQuery({
    queryKey: ['babies', babyId],
    queryFn: async () =>
      unwrap(await api.GET('/api/babies/{baby_id}', { params: { path: { baby_id: babyId } } })),
  })

  // The last 48 hours covers today's timeline, running timers and "last fed X ago".
  // refetchInterval keeps two caregivers' phones roughly in sync.
  const events = useQuery({
    queryKey: ['events', babyId],
    queryFn: async () =>
      unwrap(
        await api.GET('/api/babies/{baby_id}/events', {
          params: {
            path: { baby_id: babyId },
            query: { since: new Date(Date.now() - 48 * 3600 * 1000).toISOString(), limit: 500 },
          },
        }),
      ),
    refetchInterval: 30_000,
  })

  const stop = useMutation({
    mutationFn: async (event: EventRead) =>
      unwrap(
        await api.PATCH('/api/babies/{baby_id}/events/{event_id}', {
          params: { path: { baby_id: babyId, event_id: event.id } },
          body: { ended_at: new Date().toISOString() },
        }),
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events', babyId] }),
  })

  const remove = useMutation({
    mutationFn: async (event: EventRead) =>
      unwrap(
        await api.DELETE('/api/babies/{baby_id}/events/{event_id}', {
          params: { path: { baby_id: babyId, event_id: event.id } },
        }),
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['events', babyId] }),
  })

  if (baby.error) return <main className="page"><p className="error">{baby.error.message}</p></main>

  const all = events.data ?? []
  const ongoing = all.filter((e) => e.ended_at === null && DURATION_TYPES.includes(e.event_type))
  const today = all.filter((e) => new Date(e.started_at) >= startOfToday())
  // Events arrive newest first, so find() gives the most recent of each type.
  const lastOf = (type: EventType) => all.find((e) => e.event_type === type)

  return (
    <main className="page">
      <div className="topbar">
        <div>
          <h1>{baby.data?.name ?? '…'}</h1>
          {baby.data && <p className="muted">{ageLabel(baby.data.birth_date)}</p>}
        </div>
        <nav className="row">
          <Link className="button button--ghost button--small" to="/?all=1">Babies</Link>
          <button className="button button--ghost button--small" onClick={logOut}>Log out</button>
        </nav>
      </div>

      {ongoing.map((event) => (
        <section key={event.id} className="card card--live">
          <div>
            <p className="muted">{EVENT_LABELS[event.event_type].icon} {EVENT_LABELS[event.event_type].label} since {formatClock(event.started_at)}</p>
            <p className="timer">{formatTimer(event.started_at, now)}</p>
          </div>
          <button className="button button--primary" disabled={stop.isPending} onClick={() => stop.mutate(event)}>
            Stop
          </button>
        </section>
      ))}

      <section className="summary">
        {(['feeding', 'diaper', 'sleep'] as const).map((type) => {
          const last = lastOf(type)
          return (
            <div key={type} className="summary__item">
              <span className="muted">Last {EVENT_LABELS[type].label.toLowerCase()}</span>
              <strong>{last ? timeAgo(last.ended_at ?? last.started_at, now) : '—'}</strong>
            </div>
          )
        })}
      </section>

      <section className="grid grid--quick" aria-label="Log an event">
        {EVENT_TYPES.map((type) => (
          <button key={type} className="quick" onClick={() => setOpenSheet(type)}>
            <span className="quick__icon" aria-hidden>{EVENT_LABELS[type].icon}</span>
            {EVENT_LABELS[type].label}
          </button>
        ))}
      </section>

      <section>
        <h2>Today</h2>
        {events.isPending && <p className="muted">Loading…</p>}
        {events.error && <p className="error">{events.error.message}</p>}
        {!events.isPending && today.length === 0 && <p className="muted">Nothing logged yet today.</p>}
        <ol className="timeline">
          {today.map((event) => (
            <li key={event.id} className="timeline__item">
              <span className="timeline__time">{formatClock(event.started_at)}</span>
              <span className="timeline__body">
                <strong>{EVENT_LABELS[event.event_type].icon} {EVENT_LABELS[event.event_type].label}</strong>
                <span className="muted">
                  {[describeEvent(event), event.ended_at && formatDuration(event.started_at, event.ended_at)]
                    .filter(Boolean)
                    .join(' · ')}
                </span>
              </span>
              <button
                className="icon-button"
                aria-label="Delete event"
                onClick={() => confirm('Delete this event?') && remove.mutate(event)}
              >
                ×
              </button>
            </li>
          ))}
        </ol>
      </section>

      {openSheet && <LogSheet babyId={babyId} eventType={openSheet} onClose={() => setOpenSheet(null)} />}
    </main>
  )
}
