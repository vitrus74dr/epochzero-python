import { useEffect, useState } from 'react'
import { initSession, type SessionState } from './api'
import { Cursor } from './components/Cursor'
import { Panel } from './components/Panel'
import { Progress } from './components/Progress'
import { StatusBar } from './components/StatusBar'
import { Tag } from './components/Tag'
import { toggleTheme } from './theme/theme'

const SESSION_TEXT: Record<SessionState, { text: string; tone: 'ok' | 'bad' }> = {
  ok: { text: 'api ok', tone: 'ok' },
  expired: { text: 'session expired', tone: 'bad' },
  offline: { text: 'api offline', tone: 'bad' },
}

export default function App() {
  const [session, setSession] = useState<SessionState | null>(null)

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

  return (
    <div className="app">
      <main className="app-main">
        <h1>PYGRID <span className="muted">· curriculum cockpit</span></h1>

        {session === 'expired' && (
          <p className="tag tag--fail">
            Session expired. Open the URL printed by `uv run pygrid`.
          </p>
        )}

        <div className="specimen">
          <Panel title="System" meta="phase 1">
            <p>
              <span className="muted">$</span> uv run pygrid <Cursor />
            </p>
            <p className="muted">
              Bound to 127.0.0.1. Tracker, workbench and quizzes arrive in later phases.
            </p>
          </Panel>

          <Panel title="Components" meta="tags · progress">
            <p className="row">
              <Tag kind="pass" /> <Tag kind="fail" /> <Tag kind="locked" />{' '}
              <Tag kind="quiz" /> <Tag kind="project" />
            </p>
            <p><span className="muted">W1</span> <Progress value={0.5} /></p>
            <p><span className="muted">W2</span> <Progress value={0.125} /></p>
            <p><span className="muted">W3</span> <Progress value={0} /> <Tag kind="locked" /></p>
            <p>
              <span style={{ color: 'var(--accent)' }}>[x]</span> [W1.1.a] Set up the environment
              <br />
              <span>[ ]</span> <span style={{ color: 'var(--accent-2)' }}>[W1.1.b]</span> Greet the user with an f-string
            </p>
          </Panel>

          <Panel title="Lesson" meta="prose specimen" className="span-2">
            <h2>Control flow</h2>
            <div className="prose">
              <p>
                An <code>if</code> statement runs its block only when the condition is
                truthy. Python treats <code>0</code>, <code>""</code>, <code>[]</code> and{' '}
                <code>None</code> as falsy, so <code>if items:</code> reads as
                "if there is anything in the list".
              </p>
            </div>
          </Panel>
        </div>
      </main>

      <StatusBar
        crumbs={['W1', 'T1.1', 'environment']}
        segments={session ? [SESSION_TEXT[session]] : []}
      />
    </div>
  )
}
