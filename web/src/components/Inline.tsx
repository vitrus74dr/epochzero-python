import { Fragment } from 'react'

/** Render the tracker's inline markdown: `code` and **bold**. */
export function Inline({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((p, i) => {
        if (p.startsWith('`') && p.endsWith('`') && p.length > 1) {
          return <code key={i} className="inline-code">{p.slice(1, -1)}</code>
        }
        if (p.startsWith('**') && p.endsWith('**') && p.length > 3) {
          return <strong key={i}>{p.slice(2, -2)}</strong>
        }
        return <Fragment key={i}>{p}</Fragment>
      })}
    </>
  )
}
