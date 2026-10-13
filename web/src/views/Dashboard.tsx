import { useState } from 'react'
import { checkItem } from '../api'
import { Checklist } from '../components/Checklist'
import { Cursor } from '../components/Cursor'
import { Inline } from '../components/Inline'
import { Panel } from '../components/Panel'
import { Progress } from '../components/Progress'
import { Tag } from '../components/Tag'
import { hrefFor } from '../router'
import type { Item, Task, TrackerData, Week } from '../types'

type Props = {
  data: TrackerData
  onUpdate: (d: TrackerData) => void
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const sameDay = d.toDateString() === new Date().toDateString()
  return sameDay
    ? d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
    : d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

/** ▸ week1/t1.3-calc/ [ plan ] [ walkthrough ] under a task heading. */
function TaskDocs({ task }: { task: Task }) {
  const { folder, plan, walkthrough } = task.docs
  if (!folder) return null
  return (
    <p className="task-docs muted">
      ▸ {folder}/
      {plan && <> <a className="hdr-btn" href={hrefFor('doc', plan)}>[ plan ]</a></>}
      {walkthrough && <> <a className="hdr-btn" href={hrefFor('doc', walkthrough)}>[ walkthrough ]</a></>}
    </p>
  )
}

function WeekCard({ week, current, selected, onSelect }: {
  week: Week
  current: boolean
  selected: boolean
  onSelect: () => void
}) {
  const complete = week.total > 0 && week.done === week.total
  const cls = ['week-card', !week.unlocked && 'is-locked', current && 'is-current',
    selected && 'is-selected'].filter(Boolean).join(' ')
  return (
    <button className={cls} onClick={onSelect} aria-pressed={selected}>
      <span className="week-card-head">
        <span>WEEK {week.n}</span>
        {!week.unlocked ? <Tag kind="locked" /> : complete ? <Tag kind="pass">done</Tag>
          : current ? <span className="week-card-now">▸ now</span> : null}
      </span>
      <span className="week-card-title">{week.title}</span>
      <Progress value={week.total ? week.done / week.total : 0} />
    </button>
  )
}

export function Dashboard({ data, onUpdate }: Props) {
  const currentWeek = data.current?.week ?? null
  const [selected, setSelected] = useState<number | 'Z'>(currentWeek ?? 'Z')
  const [refusal, setRefusal] = useState<string | null>(null)

  const toggle = async (item: Item) => {
    setRefusal(null)
    const r = await checkItem(item.id, !item.checked)
    if (r.ok) onUpdate(r.data)
    else setRefusal(r.error)
  }

  const week = selected === 'Z' ? null : data.weeks.find((w) => w.n === selected) ?? null
  const totalDone = data.weeks.reduce((s, w) => s + w.done, 0)
  const total = data.weeks.reduce((s, w) => s + w.total, 0)
  const cur = data.current

  return (
    <div className="dashboard">
      <Panel title="Next action" meta={cur?.week ? `week ${cur.week}` : 'complete'}
             className="dash-next">
        {cur ? (
          <>
            <p className="next-line">
              <span className="muted">next ▸ </span>
              <span className="next-id">[{cur.item.id}]</span> <Inline text={cur.item.text} />{' '}
              <Cursor />
            </p>
            <p className="muted">
              {cur.task ? `Task ${cur.task}: ${cur.task_title}` : cur.task_title}
              {cur.item.verified
                ? ' · verified, ready to tick'
                : ' · ask the tutor in Claude Code to start'}
            </p>
          </>
        ) : (
          <p>All items ticked. <Tag kind="pass">complete</Tag></p>
        )}
        <p className="muted overall">
          overall <Progress value={total ? totalDone / total : 0} width={16} /> · {totalDone}/{total} items
        </p>
      </Panel>

      <Panel title="Recent" meta="verifications" className="dash-recent">
        {data.recent.length === 0 ? (
          <p className="muted">No verifications yet. They appear here as the tutor records them.</p>
        ) : (
          <ul className="recent">
            {data.recent.map((r, i) => (
              <li key={`${r.at}-${i}`}>
                <Tag kind={r.passed ? 'pass' : 'fail'} />
                <span className="recent-item">{r.item}</span>
                <span className="muted">{r.kind}{r.summary ? ` · ${r.summary}` : ''}</span>
                <span className="muted recent-at">{formatTime(r.at)}</span>
              </li>
            ))}
          </ul>
        )}
      </Panel>

      <div className="week-grid" role="group" aria-label="Weeks">
        {data.weeks.map((w) => (
          <WeekCard key={w.n} week={w} current={w.n === currentWeek}
                    selected={w.n === selected} onSelect={() => setSelected(w.n)} />
        ))}
      </div>

      <Panel
        title={week ? `Week ${week.n}` : 'Completion'}
        meta={week ? `${week.done}/${week.total}` : undefined}
        className="dash-detail"
      >
        {refusal && <p className="refusal" role="alert"><Tag kind="fail">refused</Tag> {refusal}</p>}
        {week ? (
          <>
            <h2>{week.title}</h2>
            {!week.unlocked && (
              <p className="muted"><Tag kind="locked" /> Unlocks when week {week.n - 1} is complete.</p>
            )}
            {week.focus && <p className="muted">focus ▸ <Inline text={week.focus} /></p>}
            {week.pitfalls && <p className="muted">watch ▸ <Inline text={week.pitfalls} /></p>}
            {week.tasks.map((task) => (
              <section key={task.id} className="task">
                <h3>
                  Task {task.id}: {task.title}{' '}
                  {task.kind && <Tag kind={task.kind === 'QUIZ' ? 'quiz' : 'project'} />}
                </h3>
                <TaskDocs task={task} />
                <Checklist items={task.items} currentId={cur?.item.id}
                           locked={!week.unlocked} onToggle={toggle} />
              </section>
            ))}
          </>
        ) : (
          <>
            <h2>Certificate</h2>
            <Checklist items={data.completion.items} currentId={cur?.item.id}
                       locked={!data.completion.unlocked} onToggle={toggle} />
          </>
        )}
        <p className="detail-foot">
          <button className="link" onClick={() => setSelected('Z')}>completion ▸</button>
        </p>
      </Panel>
    </div>
  )
}
