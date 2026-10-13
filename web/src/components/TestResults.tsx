import type { Item, TestCase, TestResult } from '../types'
import { Tag, type TagKind } from './Tag'

export type TestRun = {
  target: string
  item: string | null
  running: boolean
  output: string
  result: TestResult | null
  error: string | null
}

type Props = {
  target: string | null
  items: Item[]
  item: string
  onItem: (id: string) => void
  run: TestRun | null
  onRun: () => void
}

const OUTCOME_TAG: Record<TestCase['outcome'], [TagKind, string]> = {
  passed: ['pass', 'pass'],
  failed: ['fail', 'fail'],
  error: ['fail', 'error'],
  skipped: ['locked', 'skip'],
}

/** Tests tab: what to run, which item a pass verifies, and the parsed results. */
export function TestResults({ target, items, item, onItem, run, onRun }: Props) {
  const result = run?.result
  const failures = result?.tests.filter((t) => t.outcome === 'failed' || t.outcome === 'error') ?? []
  const showRaw = !!run && !run.running && (!result || result.tests.length === 0 || !!result.error)

  return (
    <div className="tests">
      <div className="tests-bar">
        <span className="muted">pytest ▸</span>
        <span className="tests-target">{target ? `${target}/` : 'open a file first'}</span>
        <label className="tests-item">
          <span className="muted">verify</span>
          <select value={item} onChange={(e) => onItem(e.target.value)}
                  title="A passing run records a verification for this item">
            <option value="">(don't record)</option>
            {items.map((i) => (
              <option key={i.id} value={i.id}>{i.id}{i.checked ? ' ✓' : ''}</option>
            ))}
          </select>
        </label>
        <button className="hdr-btn hdr-run" onClick={onRun} disabled={!target || run?.running}
                title="Run tests (Ctrl/Cmd+Shift+Enter)">
          {run?.running ? '[ running… ]' : '[ run tests ▸ ]'}
        </button>
      </div>

      <div className="tests-body">
        {!run && (
          <p className="muted">
            Runs pytest on the open file's folder in your workspace environment.
            Pick an item to record a verification; a passing run lets you tick it.
          </p>
        )}
        {run?.error && <p><Tag kind="fail">refused</Tag> {run.error}</p>}
        {run?.running && <p className="muted">running pytest in {run.target}/ …</p>}

        {result && (
          <>
            <p className="tests-summary">
              <Tag kind={result.passed ? 'pass' : 'fail'} /> {result.summary}
              {result.records.length > 0 && (
                <span className="muted">
                  {' · '}recorded for {result.records.map((r) => r.item).join(', ')}
                  {result.passed ? ': tick it on the dashboard' : ''}
                </span>
              )}
            </p>
            <ul className="tests-list">
              {result.tests.map((t) => {
                const [kind, label] = OUTCOME_TAG[t.outcome]
                return (
                  <li key={t.id}>
                    <Tag kind={kind}>{label}</Tag>{' '}
                    <span className={t.outcome === 'passed' ? undefined : 'tests-name-bad'}>{t.name}</span>
                    {t.classname && <span className="muted"> · {t.classname}</span>}
                    {t.outcome === 'skipped' && t.message && <span className="muted"> · {t.message}</span>}
                  </li>
                )
              })}
            </ul>
            {failures.map((t) => (
              <details key={t.id} className="tests-fail" open={failures.length <= 3}>
                <summary>{t.name}{t.message ? `: ${t.message.split('\n')[0]}` : ''}</summary>
                <pre>{t.detail || t.message}</pre>
              </details>
            ))}
          </>
        )}

        {run && run.output && (
          <details className="tests-raw" open={showRaw}>
            <summary>output</summary>
            <pre>{run.output}</pre>
          </details>
        )}
      </div>
    </div>
  )
}
