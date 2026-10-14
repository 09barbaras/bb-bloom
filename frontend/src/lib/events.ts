import type { EventRead, EventType } from '../api/client'

export const EVENT_LABELS: Record<EventType, { label: string; icon: string }> = {
  sleep: { label: 'Sleep', icon: '🌙' },
  feeding: { label: 'Feeding', icon: '🍼' },
  diaper: { label: 'Diaper', icon: '🧷' },
  symptom: { label: 'Symptom', icon: '🌡️' },
  medication: { label: 'Medication', icon: '💊' },
}

// One short line describing an event's metadata, for the timeline.
export function describeEvent(event: EventRead): string {
  const m = event.metadata as Record<string, string | number | undefined>
  switch (event.event_type) {
    case 'sleep':
      return m.quality ? `Slept ${m.quality}` : ''
    case 'feeding':
      return [m.type, m.side, m.quantity_ml != null ? `${m.quantity_ml} ml` : null]
        .filter(Boolean)
        .join(' · ')
    case 'diaper':
      return String(m.type ?? '')
    case 'symptom':
      return [m.symptom, m.temperature != null ? `${m.temperature} °C` : null, m.severity]
        .filter(Boolean)
        .join(' · ')
    case 'medication':
      return [m.name, m.dose].filter(Boolean).join(' · ')
  }
}
