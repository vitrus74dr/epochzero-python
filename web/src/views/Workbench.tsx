import { useCallback, useEffect, useRef, useState } from 'react'
import { Group, Panel as Pane, Separator } from 'react-resizable-panels'
import { getTree, readFile, writeFile, type TreeNode } from '../api'
import { Editor } from '../components/Editor'
import { FileTree } from '../components/FileTree'
import { Panel } from '../components/Panel'
import { Tag } from '../components/Tag'
import { Terminal, type TermStatus } from '../components/Terminal'
import { onServerEvent } from '../events'
import { mod } from '../keys'
import { navigate } from '../router'

type OpenFile = { path: string; base: string; version: string; loadId: number }
type Conflict = null | 'disk' | 'save'

type Props = { file: string | null; visible: boolean }

export function Workbench({ file: routeFile, visible }: Props) {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [open, setOpen] = useState<OpenFile | null>(null)
  const [draft, setDraft] = useState('')
  const [conflict, setConflict] = useState<Conflict>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [tab, setTab] = useState<'shell' | 'run'>('shell')
  const [shellKey, setShellKey] = useState(0)
  const [run, setRun] = useState<{ key: number; file: string } | null>(null)
  const [termStatus, setTermStatus] = useState<Record<string, string>>({})

  const dirty = open !== null && draft !== open.base
  // Event handlers registered once need the latest state.
  const state = useRef({ open, dirty, draft })
  state.current = { open, dirty, draft }

  const refreshTree = useCallback(async () => {
    const r = await getTree()
    if (r.ok) setTree(r.data.children)
  }, [])

  const load = useCallback(async (path: string) => {
    const r = await readFile(path)
    if (!r.ok) {
      setNotice(`${path}: ${r.error}`)
      return
    }
    setOpen((prev) => ({ path, base: r.data.content, version: r.data.version,
                         loadId: (prev?.loadId ?? 0) + 1 }))
    setDraft(r.data.content)
    setConflict(null)
    setNotice(null)
  }, [])

  // Follow the route (#/workbench/<path>).
  useEffect(() => {
    if (!routeFile || routeFile === state.current.open?.path) return
    if (state.current.dirty && !window.confirm(`Discard unsaved changes to ${state.current.open?.path}?`)) {
      navigate('workbench', state.current.open?.path)
      return
    }
    load(routeFile)
  }, [routeFile, load])

  // Live updates from disk (Claude Code editing files in the terminal).
  useEffect(() => {
    refreshTree()
    return onServerEvent(async (e) => {
      if (e.type !== 'workspace') return
      refreshTree()
      const cur = state.current.open
      if (!cur || !e.paths.includes(`workspace/${cur.path}`)) return
      const r = await readFile(cur.path)
      if (!r.ok || r.data.version === cur.version) return // our own save, or gone
      if (state.current.dirty) setConflict('disk')
      else load(cur.path)
    })
  }, [refreshTree, load])

  const save = useCallback(async (force = false): Promise<boolean> => {
    const cur = state.current.open
    if (!cur) return false
    const content = state.current.draft
    const r = await writeFile(cur.path, content, cur.version, force)
    if (r.ok) {
      setOpen({ ...cur, base: content, version: r.data.version })
      setConflict(null)
      setNotice(null)
      return true
    }
    if (r.status === 409) setConflict('save')
    else setNotice(r.error)
    return false
  }, [])

  const runCurrent = useCallback(async () => {
    const cur = state.current.open
    if (!cur) return
    if (!cur.path.endsWith('.py')) {
      setNotice('Only .py files can be run.')
      return
    }
    if (state.current.dirty && !(await save())) return
    setRun((prev) => ({ key: (prev?.key ?? 0) + 1, file: cur.path }))
    setTab('run')
  }, [save])

  // Ctrl/Cmd+S and Ctrl/Cmd+Enter outside the editor (the editor handles its own).
  useEffect(() => {
    if (!visible) return
    const on = (e: KeyboardEvent) => {
      if (e.defaultPrevented || !mod(e)) return
      if (e.key === 'Enter') { e.preventDefault(); runCurrent() }
      else if (e.key.toLowerCase() === 's' && !e.shiftKey) { e.preventDefault(); save() }
    }
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  }, [visible, runCurrent, save])

  const newFile = async () => {
    const path = window.prompt('New file (path inside workspace/):', 'week1/')
    if (!path || path.endsWith('/')) return
    const r = await writeFile(path, '', null)
    if (r.ok) navigate('workbench', path)
    else setNotice(r.error)
  }

  const status = (key: string) => (s: TermStatus, detail?: string) =>
    setTermStatus((prev) => ({ ...prev, [key]: s === 'exited' ? `exit ${detail}` : s }))

  const editorMeta = open ? `${open.path}${dirty ? ' ●' : ''}` : 'no file'

  return (
    <div className="workbench" hidden={!visible}>
      <Group orientation="horizontal" className="wb-group">
        <Pane defaultSize="20" minSize={140} className="wb-pane">
          <Panel title="Files" meta="workspace/" className="wb-panel"
                 actions={<button className="hdr-btn" onClick={newFile} title="New file">[ + new ]</button>}>
            <FileTree nodes={tree} current={open?.path ?? null}
                      onOpen={(p) => navigate('workbench', p)} />
          </Panel>
        </Pane>
        <Separator className="wb-sep wb-sep-v" />
        <Pane minSize={300} className="wb-pane">
          <Group orientation="vertical" className="wb-group">
            <Pane defaultSize="62" minSize={120} className="wb-pane">
              <Panel title="Editor" meta={editorMeta} className="wb-panel"
                     actions={open && (
                       <>
                         <button className="hdr-btn" onClick={() => save()} disabled={!dirty}
                                 title="Save (Ctrl/Cmd+S)">[ save ]</button>
                         <button className="hdr-btn hdr-run" onClick={runCurrent}
                                 title="Save and run (Ctrl/Cmd+Enter)">[ run ▸ ]</button>
                       </>
                     )}>
                {conflict && (
                  <div className="wb-banner" role="alert">
                    <Tag kind="fail">conflict</Tag>{' '}
                    {conflict === 'disk'
                      ? 'This file changed on disk while you had unsaved edits.'
                      : 'The file changed on disk since you opened it; your save was not written.'}{' '}
                    <button className="hdr-btn" onClick={() => open && load(open.path)}>[ load disk version ]</button>{' '}
                    <button className="hdr-btn" onClick={() => save(true)}>[ overwrite with mine ]</button>
                  </div>
                )}
                {notice && <div className="wb-banner muted">{notice}</div>}
                {open ? (
                  <Editor key={`${open.path}:${open.loadId}`} path={open.path} initial={open.base}
                          onChange={setDraft} onSave={() => save()} onRun={runCurrent} />
                ) : (
                  <p className="muted wb-empty">Pick a file on the left, or [ + new ].</p>
                )}
              </Panel>
            </Pane>
            <Separator className="wb-sep wb-sep-h" />
            <Pane minSize={80} className="wb-pane">
              <Panel title="Terminal" className="wb-panel wb-term"
                     meta={termStatus[tab === 'shell' ? `shell${shellKey}` : `run${run?.key}`]}
                     actions={
                       <>
                         <button className={`hdr-tab ${tab === 'shell' ? 'is-on' : ''}`}
                                 onClick={() => setTab('shell')}>shell</button>
                         <button className={`hdr-tab ${tab === 'run' ? 'is-on' : ''}`}
                                 onClick={() => setTab('run')} disabled={!run}>
                           run{run ? `: ${run.file.split('/').pop()}` : ''}
                         </button>
                         <button className="hdr-btn" title="Restart this terminal"
                                 onClick={() => tab === 'shell'
                                   ? setShellKey((k) => k + 1)
                                   : runCurrent()}>[ restart ]</button>
                       </>
                     }>
                <Terminal key={`shell${shellKey}`} mode="shell" active={tab === 'shell' && visible}
                          onStatus={status(`shell${shellKey}`)} />
                {run && (
                  <Terminal key={`run${run.key}`} mode="run" file={run.file}
                            active={tab === 'run' && visible} onStatus={status(`run${run.key}`)} />
                )}
              </Panel>
            </Pane>
          </Group>
        </Pane>
      </Group>
    </div>
  )
}
