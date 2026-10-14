// The API stores and returns UTC. Everything here converts to the
// browser's local time for display, and back to ISO (UTC) when sending.

import { useEffect, useState } from 'react'

export function startOfToday(): Date {
  const date = new Date()
  date.setHours(0, 0, 0, 0)
  return date
}

export function formatClock(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function formatDuration(fromIso: string, to: Date | string): string {
  const end = typeof to === 'string' ? new Date(to) : to
  const totalMinutes = Math.max(0, Math.floor((end.getTime() - new Date(fromIso).getTime()) / 60000))
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return hours > 0 ? `${hours}h ${minutes.toString().padStart(2, '0')}m` : `${minutes}m`
}

// Running timer: "4:05" under an hour, "1:04:05" over.
export function formatTimer(fromIso: string, now: Date): string {
  const total = Math.max(0, Math.floor((now.getTime() - new Date(fromIso).getTime()) / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = (total % 60).toString().padStart(2, '0')
  return h > 0 ? `${h}:${m.toString().padStart(2, '0')}:${s}` : `${m}:${s}`
}

export function timeAgo(iso: string, now: Date): string {
  return `${formatDuration(iso, now)} ago`
}

// <input type="datetime-local"> works with "YYYY-MM-DDTHH:mm" in local time.
export function toLocalInputValue(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16)
}

export function fromLocalInputValue(value: string): string {
  return new Date(value).toISOString()
}

// Re-renders the component every `intervalMs`, for running timers.
export function useNow(intervalMs = 1000): Date {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs])
  return now
}

export function ageLabel(birthDate: string): string {
  const born = new Date(`${birthDate}T00:00:00`)
  const days = Math.floor((startOfToday().getTime() - born.getTime()) / 86400000)
  if (days < 14) return `${days} day${days === 1 ? '' : 's'} old`
  if (days < 7 * 13) return `${Math.floor(days / 7)} weeks old`
  const months = Math.floor(days / 30.44)
  return months < 24 ? `${months} months old` : `${Math.floor(months / 12)} years old`
}
