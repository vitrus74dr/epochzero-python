import { useCallback, useEffect, useState } from 'react'
import { readFile } from '../api'
import { Markdown } from '../components/Markdown'
import { Panel } from '../components/Panel'
import { Tag } from '../components/Tag'
import { onServerEvent } from '../events'
import { hrefFor } from '../router'

/** Read-only rendering of a workspace markdown file (implementation_plan.md,
 *  walkthrough.md), live-reloaded when the tutor rewrites it. */
export function DocView({ path }: { path: string | null }) {
  const [text, setText] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!path) return
    const r = await readFile(path)
    if (r.ok) {
      setText(r.data.content)
      setError(null)
    } else {
      setError(r.error)
    }
  }, [path])

  useEffect(() => {
    load()
    return onServerEvent((e) => {
      if (e.type === 'workspace' && path && e.paths.includes(`workspace/${path}`)) load()
    })
  }, [load, path])

  return (
    <div className="doc-view">
      <Panel title={path?.split('/').pop() ?? 'Document'} meta={path ?? undefined}
             actions={path && <a className="hdr-btn" href={hrefFor('workbench', path)}>[ edit ]</a>}>
        {!path && <p className="muted">No document selected.</p>}
        {error && <p role="alert"><Tag kind="fail">error</Tag> {error}</p>}
        {text !== null && !error && <Markdown text={text} />}
      </Panel>
    </div>
  )
}
