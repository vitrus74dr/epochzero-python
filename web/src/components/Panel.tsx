import type { ReactNode } from 'react'

type Props = {
  title: string
  meta?: string
  className?: string
  actions?: ReactNode
  children: ReactNode
}

const RULE = '─'.repeat(240)

/** ┌─ TITLE ── meta ──────── chamfered panel. */
export function Panel({ title, meta, className, actions, children }: Props) {
  return (
    <section className={`panel ${className ?? ''}`} aria-label={title}>
      <div className="panel-inner">
        <header className="panel-header">
          <span aria-hidden="true">┌─</span>
          <span className="panel-title">{title}</span>
          {meta && <><span aria-hidden="true">──</span><span className="panel-meta">{meta}</span></>}
          <span className="panel-rule" aria-hidden="true">{RULE}</span>
          {actions && <span className="panel-actions">{actions}</span>}
        </header>
        <div className="panel-body">{children}</div>
      </div>
    </section>
  )
}
