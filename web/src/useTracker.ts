import { useCallback, useEffect, useState } from 'react'
import { getTracker } from './api'
import { onServerEvent } from './events'
import type { TrackerData } from './types'

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
    if (!enabled) return
    refresh()
    return onServerEvent((e) => {
      if (e.type === 'tracker' || e.type === 'verifications') refresh()
    })
  }, [enabled, refresh])

  return { data, setData, error }
}
