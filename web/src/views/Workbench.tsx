import { useCallback, useEffect, useRef, useState } from 'react'
import { Group, Panel as Pane, Separator } from 'react-resizable-panels'
import { getTree, readFile, runTests, writeFile, type TreeNode } from '../api'
import { Editor } from '../components/Editor'
import { FileTree } from '../components/FileTree'
import { Panel } from '../components/Panel'
import { Tag } from '../components/Tag'
import { Terminal, type TermStatus } from '../components/Terminal'
import { TestResults, type TestRun } from '../components/TestResults'
import { onServerEvent } from '../events'
import { isRunTests, mod } from '../keys'
import { hrefFor, navigate } from '../router'
import type { Item, TestResult, TrackerData } from '../types'

type OpenFile = { path: string; base: string; version: string; loadId: number }
type Conflict = null | 'disk' | 'save'

type Props = {
  file: string | null
  visible: boolean
  tracker: TrackerData | null
  onTestResult: (r: TestResult | null) => void
}

type Tab = 'shell' | 'run' | 'tests'

/** Items a pytest run may verify: pytest items in unlocked weeks. */
function pytestItems(t: TrackerData | null): Item[] {
  if (!t) return []
  return t.weeks.filter((w) => w.unlocked)
    .flatMap((w) => w.tasks.flatMap((task) => task.items))
    .filter((i) => i.verify === 'pytest')
}

/** The item a test run records by default: the current item if it's a pytest item, else the
 *  first unticked pytest item of the task whose folder is being tested, else none. */
function defaultTestItem(t: TrackerData | null, eligible: Item[], cur: string | null,
                         target: string | null): string {
  if (cur && eligible.some((i) => i.id === cur)) return cur
  if (!t || !target) return ''
  const task = t.weeks.filter((w) => w.unlocked).flatMap((w) => w.tasks)
    .find((task) => task.docs.folder !== null
      && (target === task.docs.folder || target.startsWith(`${task.docs.folder}/`)))
  const items = task?.items.filter((i) => i.verify === 'pytest') ?? []
  return (items.find((i) => !i.checked) ?? items[0])?.id ?? ''
}

const IMAGE_RE = /\.(png|jpe?g|gif|webp)$/i
const imageUrl = (path: string, stamp: number) =>
  `/api/files/image?path=${encodeURIComponent(path)}&t=${stamp}`

const dirOf = (path: string) => path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '.'

export function Workbench({ file: routeFile, visible, tracker, onTestResult }: Props) {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [open, setOpen] = useState<OpenFile | null>(null)
  const [draft, setDraft] = useState('')
  const [conflict, setConflict] = useState<Conflict>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('shell')
  const [shellKey, setShellKey] = useState(0)
  const [run, setRun] = useState<{ key: number; file: string } | null>(null)
  const [termStatus, setTermStatus] = useState<Record<string, string>>({})
  const [testRun, setTestRun] = useState<TestRun | null>(null)
  // An image open for preview instead of a text file; `stamp` reloads it after changes on disk.
  const [image, setImage] = useState<{ path: string; stamp: number } | null>(null)
  // null = follow the tracker's current item (if it's a pytest item).
  const [testItem, setTestItem] = useState<string | null>(null)

  const eligible = pytestItems(tracker)
  const curWeek = tracker?.weeks.find((w) => w.n === tracker.current?.week)
  const curFolder = curWeek?.tasks.find((t) => t.id === tracker?.current?.task)?.docs.folder ?? null
  // The open file's folder, else the current task's folder.
  const testTarget = open ? dirOf(open.path) : curFolder
  const cur = tracker?.current?.item
  const chosenItem = testItem ?? defaultTestItem(tracker, eligible, cur?.id ?? null, testTarget)

  const dirty = open !== null && draft !== open.base
  // Event handlers registered once need the latest state.
  const state = useRef({ open, dirty, draft, testTarget, chosenItem, testRun })
  state.current = { open, dirty, draft, testTarget, chosenItem, testRun }

  const refreshTree = useCallback(async () => {
    const r = await getTree()
    if (r.ok) setTree(r.data.children)
  }, [])

  const load = useCallback(async (path: string) => {
    if (IMAGE_RE.test(path)) {
      setImage({ path, stamp: Date.now() })
      setOpen(null)
      setConflict(null)
      setNotice(null)
      return
    }
    setImage(null)
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
      setImage((img) => img && e.paths.includes(`workspace/${img.path}`)
        ? { ...img, stamp: Date.now() } : img)
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

  const runTestsNow = useCallback(async () => {
    const { testTarget: target, chosenItem: item, testRun: prev } = state.current
    if (!target || prev?.running) return
    if (state.current.dirty && !(await save())) return
    setTab('tests')
    const run: TestRun = { target, item: item || null, running: true, output: '', result: null, error: null }
    setTestRun(run)
    onTestResult(null)
    const r = await runTests(target, item || null, (e) => {
      if (e.type === 'output') run.output += e.data
      else if (e.type === 'result') {
        run.result = e
        onTestResult(e)
      }
      setTestRun({ ...run })
    })
    setTestRun({ ...run, running: false, error: r.ok ? (run.result ? null : 'no result') : r.error })
  }, [save, onTestResult])

  // Ctrl/Cmd+S, Ctrl/Cmd+Enter and run-tests outside the editor (the editor handles its own).
  useEffect(() => {
    if (!visible) return
    const on = (e: KeyboardEvent) => {
      if (e.defaultPrevented || !mod(e)) return
      if (isRunTests(e)) { e.preventDefault(); runTestsNow() }
      else if (e.key === 'Enter') { e.preventDefault(); runCurrent() }
      else if (e.key.toLowerCase() === 's' && !e.shiftKey) { e.preventDefault(); save() }
    }
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  }, [visible, runCurrent, runTestsNow, save])

  const newFile = async () => {
    const path = window.prompt('New file (path inside workspace/):', 'week1/')
    if (!path || path.endsWith('/')) return
    const r = await writeFile(path, '', null)
    if (r.ok) navigate('workbench', path)
    else setNotice(r.error)
  }

  const status = (key: string) => (s: TermStatus, detail?: string) =>
    setTermStatus((prev) => ({ ...prev, [key]: s === 'exited' ? `exit ${detail}` : s }))

  const editorMeta = open ? `${open.path}${dirty ? ' ●' : ''}` : image ? image.path : 'no file'

  return (
    <div className="workbench" hidden={!visible}>
      <Group orientation="horizontal" className="wb-group">
        <Pane defaultSize="20" minSize={140} className="wb-pane">
          <Panel title="Files" meta="workspace/" className="wb-panel"
                 actions={<button className="hdr-btn" onClick={newFile} title="New file">[ + new ]</button>}>
            <FileTree nodes={tree} current={open?.path ?? image?.path ?? null}
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
                         {open.path.endsWith('.md') && (
                           <a className="hdr-btn" href={hrefFor('doc', open.path)}
                              title="Rendered view (save first to see your edits)">[ preview ]</a>
                         )}
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
                          onChange={setDraft} onSave={() => save()} onRun={runCurrent}
                          onRunTests={runTestsNow} />
                ) : image ? (
                  <div className="wb-image">
                    <img src={imageUrl(image.path, image.stamp)} alt={image.path}
                         onError={() => setNotice(`${image.path}: can't show this image`)} />
                  </div>
                ) : (
                  <p className="muted wb-empty">Pick a file on the left, or [ + new ].</p>
                )}
              </Panel>
            </Pane>
            <Separator className="wb-sep wb-sep-h" />
            <Pane minSize={80} className="wb-pane">
              <Panel title={tab === 'tests' ? 'Tests' : 'Terminal'} className="wb-panel wb-term"
                     meta={tab === 'tests'
                       ? testRun?.result?.summary ?? (testRun?.running ? 'running' : undefined)
                       : termStatus[tab === 'shell' ? `shell${shellKey}` : `run${run?.key}`]}
                     actions={
                       <>
                         <button className={`hdr-tab ${tab === 'shell' ? 'is-on' : ''}`}
                                 onClick={() => setTab('shell')}>shell</button>
                         <button className={`hdr-tab ${tab === 'run' ? 'is-on' : ''}`}
                                 onClick={() => setTab('run')} disabled={!run}>
                           run{run ? `: ${run.file.split('/').pop()}` : ''}
                         </button>
                         <button className={`hdr-tab ${tab === 'tests' ? 'is-on' : ''}`}
                                 onClick={() => setTab('tests')}>
                           tests{testRun?.result ? ` ${testRun.result.counts.passed}/${testRun.result.tests.length}` : ''}
                         </button>
                         {tab !== 'tests' && (
                           <button className="hdr-btn" title="Restart this terminal"
                                   onClick={() => tab === 'shell'
                                     ? setShellKey((k) => k + 1)
                                     : runCurrent()}>[ restart ]</button>
                         )}
                       </>
                     }>
                <Terminal key={`shell${shellKey}`} mode="shell" active={tab === 'shell' && visible}
                          onStatus={status(`shell${shellKey}`)} />
                {run && (
                  <Terminal key={`run${run.key}`} mode="run" file={run.file}
                            active={tab === 'run' && visible} onStatus={status(`run${run.key}`)} />
                )}
                {tab === 'tests' && (
                  <TestResults target={testTarget} items={eligible} item={chosenItem}
                               onItem={setTestItem} run={testRun} onRun={runTestsNow} />
                )}
              </Panel>
            </Pane>
          </Group>
        </Pane>
      </Group>
    </div>
  )
}
