import { useEffect, useState } from 'react'
import { initSession, type SessionState } from './api'
import { StatusBar } from './components/StatusBar'
import { Tag } from './components/Tag'
import { toggleTheme } from './theme/theme'
import { useTracker } from './useTracker'
import { Dashboard } from './views/Dashboard'

const SESSION_TEXT: Record<SessionState, { text: string; tone: 'ok' | 'bad' }> = {
  ok: { text: 'api ok', tone: 'ok' },
  expired: { text: 'session expired', tone: 'bad' },
  offline: { text: 'api offline', tone: 'bad' },
}

export default function App() {
  const [session, setSession] = useState<SessionState | null>(null)
  const { data, setData, error, live } = useTracker(session === 'ok')

  useEffect(() => {
    initSession().then(setSession)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'l') {
        e.preventDefault()
        toggleTheme()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const cur = data?.current
  const crumbs = cur
    ? [cur.week ? `W${cur.week}` : 'DONE', ...(cur.task ? [`T${cur.task}`] : []), cur.task_title]
    : []
  const segments = session === 'ok'
    ? [live ? { text: '● live', tone: 'ok' as const } : { text: '○ reconnecting', tone: 'bad' as const }]
    : session ? [SESSION_TEXT[session]] : []

  return (
    <div className="app">
      <main className="app-main">
        <h1>PYGRID <span className="muted">· dashboard</span></h1>

        {session === 'expired' && (
          <p className="banner"><Tag kind="fail">session</Tag> Expired. Open the URL printed by `uv run pygrid`.</p>
        )}
        {session === 'offline' && (
          <p className="banner"><Tag kind="fail">offline</Tag> Can't reach the PYGRID server.</p>
        )}
        {error && (
          <p className="banner" role="alert"><Tag kind="fail">tracker</Tag> {error}</p>
        )}

        {data && <Dashboard data={data} onUpdate={setData} />}
      </main>

      <StatusBar crumbs={crumbs} segments={segments} />
    </div>
  )
}
