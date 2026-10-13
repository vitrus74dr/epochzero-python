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
import type { TestResult } from './types'
import { Dashboard } from './views/Dashboard'
import { DocView } from './views/Doc'
import { QuizView } from './views/Quiz'
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
  const [tests, setTests] = useState<TestResult | null>(null)
  // Keep the workbench (and its shell) alive once visited, on its last file.
  const [workbenchMounted, setWorkbenchMounted] = useState(false)
  const [workbenchFile, setWorkbenchFile] = useState<string | null>(null)
  if (route.view === 'workbench' && !workbenchMounted && ready) setWorkbenchMounted(true)
  if (route.view === 'workbench' && route.file && route.file !== workbenchFile) setWorkbenchFile(route.file)

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
        else if (e.key === 'w') navigate('workbench', workbenchFile)
        else if (e.key === 'q') navigate('quiz')
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
  }, [workbenchFile])

  const cur = data?.current
  const crumbs = cur
    ? [cur.week ? `W${cur.week}` : 'DONE', ...(cur.task ? [`T${cur.task}`] : []), cur.task_title]
    : []
  const testsSegment = tests && {
    text: `tests ${tests.counts.passed}/${tests.tests.length}`,
    tone: tests.passed ? 'ok' as const : 'bad' as const,
  }
  const segments = ready
    ? [...(testsSegment ? [testsSegment] : []),
       live ? { text: '● live', tone: 'ok' as const } : { text: '○ reconnecting', tone: 'bad' as const }]
    : session ? [SESSION_TEXT[session]] : []
  const onWorkbench = route.view === 'workbench'

  return (
    <div className="app">
      <main className={`app-main ${onWorkbench ? 'is-workbench' : ''}`}>
        <header className="topbar">
          <h1>PYGRID</h1>
          <nav className="nav" aria-label="Views">
            <a href={hrefFor('dashboard')} className={route.view === 'dashboard' ? 'is-on' : ''}
               title="g d">dashboard</a>
            <a href={hrefFor('workbench', workbenchFile)} className={onWorkbench ? 'is-on' : ''}
               title="g w">workbench</a>
            <a href={hrefFor('quiz')} className={route.view === 'quiz' ? 'is-on' : ''}
               title="g q">quiz</a>
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

        {route.view === 'dashboard' && data && <Dashboard data={data} onUpdate={setData} />}
        {route.view === 'quiz' && ready && <QuizView quizId={route.file} />}
        {route.view === 'doc' && ready && <DocView path={route.file} />}
        {workbenchMounted && <Workbench file={workbenchFile} visible={onWorkbench}
                                        tracker={data} onTestResult={setTests} />}
      </main>

      <StatusBar crumbs={crumbs} segments={segments} />
      {sheet && <ShortcutSheet onClose={() => setSheet(false)} />}
    </div>
  )
}
