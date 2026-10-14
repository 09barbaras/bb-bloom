import { useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api, unwrap, type EventCreate, type EventType, type Schemas } from '../api/client'
import { EVENT_LABELS } from '../lib/events'
import { fromLocalInputValue, toLocalInputValue } from '../lib/time'

type Props = {
  babyId: number
  eventType: EventType
  onClose: () => void
}

type FeedingType = Schemas['FeedingMetadata']['type']
type DiaperType = Schemas['DiaperMetadata']['type']
type Severity = NonNullable<Schemas['SymptomMetadata']['severity']>
type Side = NonNullable<Schemas['FeedingMetadata']['side']>

// A bottom sheet with the form for one event type. Every type shares the
// "when" fields; each has its own metadata fields below.
export function LogSheet({ babyId, eventType, onClose }: Props) {
  const queryClient = useQueryClient()
  const isDuration = eventType === 'sleep' || eventType === 'feeding'

  const [startedAt, setStartedAt] = useState(() => toLocalInputValue(new Date()))
  const [endedAt, setEndedAt] = useState('') // empty = still going (timer)

  const [feedingType, setFeedingType] = useState<FeedingType>('breast')
  const [side, setSide] = useState<Side>('left')
  const [quantityMl, setQuantityMl] = useState('')
  const [symptom, setSymptom] = useState('fever')
  const [temperature, setTemperature] = useState('')
  const [severity, setSeverity] = useState<Severity | ''>('')
  const [medName, setMedName] = useState('')
  const [dose, setDose] = useState('')

  const save = useMutation({
    mutationFn: async (body: EventCreate) =>
      unwrap(
        await api.POST('/api/babies/{baby_id}/events', {
          params: { path: { baby_id: babyId } },
          body,
        }),
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events', babyId] })
      onClose()
    },
  })

  function times() {
    return {
      started_at: fromLocalInputValue(startedAt),
      ended_at: isDuration && endedAt ? fromLocalInputValue(endedAt) : null,
    }
  }

  function buildBody(diaperType?: DiaperType): EventCreate {
    switch (eventType) {
      case 'sleep':
        return { event_type: 'sleep', ...times(), metadata: {} }
      case 'feeding':
        return {
          event_type: 'feeding',
          ...times(),
          metadata: {
            type: feedingType,
            side: feedingType === 'breast' ? side : null,
            quantity_ml: feedingType !== 'breast' && quantityMl ? Number(quantityMl) : null,
          },
        }
      case 'diaper':
        return { event_type: 'diaper', ...times(), metadata: { type: diaperType ?? 'wet' } }
      case 'symptom':
        return {
          event_type: 'symptom',
          ...times(),
          metadata: {
            symptom,
            temperature: temperature ? Number(temperature) : null,
            severity: severity || null,
          },
        }
      case 'medication':
        return { event_type: 'medication', ...times(), metadata: { name: medName, dose } }
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    save.mutate(buildBody())
  }

  const { icon, label } = EVENT_LABELS[eventType]

  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <form className="sheet stack" onSubmit={onSubmit} onClick={(e) => e.stopPropagation()}>
        <div className="topbar">
          <h2>{icon} {label}</h2>
          <button type="button" className="button button--ghost button--small" onClick={onClose}>
            Cancel
          </button>
        </div>

        <label className="field">
          <span>{isDuration ? 'Started' : 'When'}</span>
          <input type="datetime-local" value={startedAt} onChange={(e) => setStartedAt(e.target.value)} required />
        </label>

        {isDuration && (
          <label className="field">
            <span>Ended <small className="muted">(leave empty to start a timer)</small></span>
            <input type="datetime-local" value={endedAt} onChange={(e) => setEndedAt(e.target.value)} />
          </label>
        )}

        {eventType === 'feeding' && (
          <>
            <Choice
              label="Type"
              options={['breast', 'milk', 'formula', 'solids'] as const}
              value={feedingType}
              onChange={setFeedingType}
            />
            {feedingType === 'breast' ? (
              <Choice label="Side" options={['left', 'right', 'both'] as const} value={side} onChange={setSide} />
            ) : (
              <label className="field">
                <span>Amount (ml)</span>
                <input type="number" inputMode="numeric" min={0} max={1000} value={quantityMl} onChange={(e) => setQuantityMl(e.target.value)} />
              </label>
            )}
          </>
        )}

        {eventType === 'symptom' && (
          <>
            <label className="field">
              <span>Symptom</span>
              <input value={symptom} onChange={(e) => setSymptom(e.target.value)} required />
            </label>
            <label className="field">
              <span>Temperature (°C)</span>
              <input type="number" inputMode="decimal" step="0.1" min={30} max={45} value={temperature} onChange={(e) => setTemperature(e.target.value)} />
            </label>
            <Choice
              label="Severity"
              options={['mild', 'moderate', 'severe'] as const}
              value={severity}
              onChange={setSeverity}
            />
          </>
        )}

        {eventType === 'medication' && (
          <>
            <label className="field">
              <span>Medicine</span>
              <input value={medName} onChange={(e) => setMedName(e.target.value)} placeholder="paracetamol" required />
            </label>
            <label className="field">
              <span>Dose</span>
              <input value={dose} onChange={(e) => setDose(e.target.value)} placeholder="2.5 ml" required />
            </label>
          </>
        )}

        {save.error && <p className="error">{save.error.message}</p>}

        {eventType === 'diaper' ? (
          // One tap saves: no extra "Save" step for the most frequent event.
          <div className="grid grid--3">
            {(['wet', 'poop', 'mixed'] as const).map((type) => (
              <button
                key={type}
                type="button"
                className="button button--primary"
                disabled={save.isPending}
                onClick={() => save.mutate(buildBody(type))}
              >
                {type[0].toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        ) : (
          <button className="button button--primary" disabled={save.isPending}>
            {isDuration && !endedAt ? 'Start timer' : 'Save'}
          </button>
        )}
      </form>
    </div>
  )
}

function Choice<T extends string>({
  label,
  options,
  value,
  onChange,
}: {
  label: string
  options: readonly T[]
  value: T | ''
  onChange: (value: T) => void
}) {
  return (
    <fieldset className="field">
      <legend>{label}</legend>
      <div className="segmented">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            className={option === value ? 'is-selected' : ''}
            aria-pressed={option === value}
            onClick={() => onChange(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </fieldset>
  )
}
