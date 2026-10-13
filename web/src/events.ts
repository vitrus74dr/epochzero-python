import { useEffect, useState } from 'react'

export type ServerEvent = { type: string; paths: string[] }

// One EventSource for the whole app, fanned out to subscribers.
let source: EventSource | null = null
let live = false
const handlers = new Set<(e: ServerEvent) => void>()
const liveListeners = new Set<(live: boolean) => void>()

function setLive(v: boolean) {
  live = v
  liveListeners.forEach((fn) => fn(v))
}

export function startEvents(): void {
  if (source) return
  source = new EventSource('/api/events')
  source.onopen = () => setLive(true)
  source.onerror = () => setLive(false) // EventSource reconnects on its own
  source.onmessage = (m) => {
    let e: ServerEvent
    try {
      e = JSON.parse(m.data)
    } catch {
      return
    }
    handlers.forEach((fn) => fn(e))
  }
}

export function onServerEvent(fn: (e: ServerEvent) => void): () => void {
  handlers.add(fn)
  return () => handlers.delete(fn)
}

export function useLive(): boolean {
  const [v, setV] = useState(live)
  useEffect(() => {
    liveListeners.add(setV)
    return () => { liveListeners.delete(setV) }
  }, [])
  return v
}
