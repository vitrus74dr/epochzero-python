import { useEffect, useState } from 'react'
import { useTheme } from '../theme/useTheme'

type Props = {
  crumbs: string[]
  segments?: { text: string; tone?: 'ok' | 'bad' }[]
}

function clock(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
}

/** tmux-style bar: EPOCHZERO ▸ W1 ▸ T1.2 │ tests 4/5 │ ● dark │ 21:20 */
export function StatusBar({ crumbs, segments = [] }: Props) {
  const [theme, toggle] = useTheme()
  const [now, setNow] = useState(clock)

  useEffect(() => {
    const id = setInterval(() => setNow(clock()), 10_000)
    return () => clearInterval(id)
  }, [])

  return (
    <footer className="statusbar">
      <span className="statusbar-brand">EPOCHZERO</span>
      <span className="statusbar-crumbs">
        {crumbs.map((c) => (
          <span key={c}><span className="statusbar-sep"> ▸ </span>{c}</span>
        ))}
      </span>
      <span className="statusbar-spacer" />
      {segments.map((s) => (
        <span key={s.text}>
          <span className={s.tone ? `statusbar-${s.tone}` : undefined}>{s.text}</span>
          <span className="statusbar-sep"> │</span>
        </span>
      ))}
      <button className="statusbar-toggle" onClick={toggle}
              title="Toggle theme (Ctrl/Cmd+Shift+L)">
        {theme === 'dark' ? '● dark' : '○ light'}
      </button>
      <span className="statusbar-sep">│</span>
      <span>{now}</span>
    </footer>
  )
}
