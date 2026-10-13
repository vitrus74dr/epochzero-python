import { useEffect, useRef, useState } from 'react'
import { initSession, type SessionState } from './api'
import { ShortcutSheet } from './components/ShortcutSheet'
import { StatusBar } from './components/StatusBar'
import { Tag } from './components/Tag'
import { startEvents, useLive } from './events'
import { isTyping, mod } from './keys'
import { hrefFor, navigate, useRoute } from './router'
import { toggleTheme } from './theme/theme'
import { useTracker } from './useTracker'
import { Dashboard } from './views/Dashboard'
import { Workbench } from './views/Workbench'

const SESSION_TEXT: Record<SessionState, { text: string; tone: 'ok' | 'bad' }> = {
  ok: { text: 'api ok', tone: 'ok' },
  expired: { text: 'session expired', tone: 'bad' },
  offline: { text: 'api offline', tone: 'bad' },
}

export default function App() {
  const [session, setSession] = useState<SessionState | null>(null)
  const ready = session === 'ok'
  const { data, setData, error } = useTracker(ready)
  const live = useLive()
  const route = useRoute()
  const [sheet, setSheet] = useState(false)
  // Keep the workbench (and its shell) alive once visited.
  const [workbenchMounted, setWorkbenchMounted] = useState(false)
  if (route.view === 'workbench' && !workbenchMounted && ready) setWorkbenchMounted(true)

  useEffect(() => {
    initSession().then((s) => {
      setSession(s)
      if (s === 'ok') startEvents()
    })
  }, [])

  const chord = useRef<number | null>(null)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (mod(e) && e.shiftKey && e.key.toLowerCase() === 'l') {
        e.preventDefault()
        toggleTheme()
        return
      }
      if (mod(e) || e.altKey || isTyping(e.target)) return
      if (chord.current !== null) {
        window.clearTimeout(chord.current)
        chord.current = null
        if (e.key === 'd') navigate('dashboard')
        else if (e.key === 'w') navigate('workbench', route.file)
        return
      }
      if (e.key === 'g') {
        chord.current = window.setTimeout(() => { chord.current = null }, 1000)
      } else if (e.key === '?') {
        setSheet(true)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [route.file])

  const cur = data?.current
  const crumbs = cur
    ? [cur.week ? `W${cur.week}` : 'DONE', ...(cur.task ? [`T${cur.task}`] : []), cur.task_title]
    : []
  const segments = ready
    ? [live ? { text: '● live', tone: 'ok' as const } : { text: '○ reconnecting', tone: 'bad' as const }]
    : session ? [SESSION_TEXT[session]] : []
  const onWorkbench = route.view === 'workbench'

  return (
    <div className="app">
      <main className={`app-main ${onWorkbench ? 'is-workbench' : ''}`}>
        <header className="topbar">
          <h1>PYGRID</h1>
          <nav className="nav" aria-label="Views">
            <a href={hrefFor('dashboard')} className={!onWorkbench ? 'is-on' : ''}
               title="g d">dashboard</a>
            <a href={hrefFor('workbench', route.file)} className={onWorkbench ? 'is-on' : ''}
               title="g w">workbench</a>
          </nav>
          <button className="link" onClick={() => setSheet(true)} title="Keyboard shortcuts">?</button>
        </header>

        {session === 'expired' && (
          <p className="banner"><Tag kind="fail">session</Tag> Expired. Open the URL printed by `uv run pygrid`.</p>
        )}
        {session === 'offline' && (
          <p className="banner"><Tag kind="fail">offline</Tag> Can't reach the PYGRID server.</p>
        )}
        {error && !onWorkbench && (
          <p className="banner" role="alert"><Tag kind="fail">tracker</Tag> {error}</p>
        )}

        {!onWorkbench && data && <Dashboard data={data} onUpdate={setData} />}
        {workbenchMounted && <Workbench file={route.file} visible={onWorkbench} />}
      </main>

      <StatusBar crumbs={crumbs} segments={segments} />
      {sheet && <ShortcutSheet onClose={() => setSheet(false)} />}
    </div>
  )
}
