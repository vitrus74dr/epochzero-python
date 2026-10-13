import { useCallback, useEffect, useState } from 'react'
import { getTracker } from './api'
import type { TrackerData } from './types'

export type ServerEvent = { type: string; paths: string[] }

/** Subscribe to /api/events. Returns whether the stream is connected. */
export function useServerEvents(enabled: boolean, onEvent: (e: ServerEvent) => void): boolean {
  const [live, setLive] = useState(false)
  useEffect(() => {
    if (!enabled) return
    const es = new EventSource('/api/events')
    es.onopen = () => setLive(true)
    es.onerror = () => setLive(false) // EventSource retries on its own
    es.onmessage = (m) => {
      try {
        onEvent(JSON.parse(m.data))
      } catch {
        // ignore malformed events
      }
    }
    return () => es.close()
  }, [enabled, onEvent])
  return live
}

/** Tracker state, refetched whenever the tracker or verification log changes on disk. */
export function useTracker(enabled: boolean) {
  const [data, setData] = useState<TrackerData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const r = await getTracker()
    if (r.ok) {
      setData(r.data)
      setError(null)
    } else {
      setError(r.error)
    }
  }, [])

  useEffect(() => {
    if (enabled) refresh()
  }, [enabled, refresh])

  const onEvent = useCallback((e: ServerEvent) => {
    if (e.type === 'tracker' || e.type === 'verifications') refresh()
  }, [refresh])

  const live = useServerEvents(enabled, onEvent)
  return { data, setData, error, live }
}
