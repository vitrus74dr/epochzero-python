import { useEffect } from 'react'
import { SHORTCUTS } from '../keys'
import { Panel } from './Panel'

export function ShortcutSheet({ onClose }: { onClose: () => void }) {
  useEffect(() => {
    const on = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  }, [onClose])
  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts"
         onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()}>
        <Panel title="Shortcuts" meta="esc to close" className="sheet">
          <dl className="shortcuts">
            {SHORTCUTS.map((s) => (
              <div key={s.keys}><dt>{s.keys}</dt><dd>{s.label}</dd></div>
            ))}
          </dl>
        </Panel>
      </div>
    </div>
  )
}
