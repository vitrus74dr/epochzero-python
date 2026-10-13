import type { ReactNode } from 'react'

type Props = {
  title: string
  meta?: string
  className?: string
  children: ReactNode
}

const RULE = '─'.repeat(240)

/** ┌─ TITLE ── meta ──────── chamfered panel. */
export function Panel({ title, meta, className, children }: Props) {
  return (
    <section className={`panel ${className ?? ''}`} aria-label={title}>
      <div className="panel-inner">
        <header className="panel-header" aria-hidden="true">
          <span>┌─</span>
          <span className="panel-title">{title}</span>
          {meta && <><span>──</span><span>{meta}</span></>}
          <span className="panel-rule">{RULE}</span>
        </header>
        <div className="panel-body">{children}</div>
      </div>
    </section>
  )
}
