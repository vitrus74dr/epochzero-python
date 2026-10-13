import { useCallback, useEffect, useState } from 'react'
import { checkItem, getLessons } from '../api'
import { Checklist } from '../components/Checklist'
import { Markdown } from '../components/Markdown'
import { Panel } from '../components/Panel'
import { Tag } from '../components/Tag'
import { onServerEvent } from '../events'
import { hrefFor } from '../router'
import type { Item, TrackerData, WeekLessons } from '../types'

type Props = {
  /** Task id like "1.3"; null means the current task. */
  taskId: string | null
  data: TrackerData
  onUpdate: (d: TrackerData) => void
}

/** Lesson markdown with the task's acceptance criteria pinned above it (HANDOFF §3). */
export function LessonView({ taskId, data, onUpdate }: Props) {
  const fallback = data.current?.task ?? data.weeks[0]?.tasks[0]?.id ?? '1.1'
  const task = taskId ?? fallback
  const weekN = Number(task.split('.')[0])
  const week = data.weeks.find((w) => w.n === weekN)
  const trackerTask = week?.tasks.find((t) => t.id === task)

  const [lessons, setLessons] = useState<WeekLessons | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [refusal, setRefusal] = useState<string | null>(null)

  const load = useCallback(async () => {
    const r = await getLessons(weekN)
    if (r.ok) {
      setLessons(r.data)
      setError(null)
    } else {
      setError(r.error)
    }
  }, [weekN])

  useEffect(() => {
    load()
    return onServerEvent((e) => {
      if (e.type === 'curriculum' || e.type === 'tracker') load()
    })
  }, [load])

  // Each lesson starts at the top.
  useEffect(() => { document.querySelector('.app-main')?.scrollTo(0, 0) }, [task])

  const toggle = async (item: Item) => {
    setRefusal(null)
    const r = await checkItem(item.id, !item.checked)
    if (r.ok) onUpdate(r.data)
    else setRefusal(r.error)
  }

  const lesson = lessons?.week === weekN ? lessons.lessons.find((l) => l.task === task) : undefined
  const docs = trackerTask?.docs

  return (
    <div className="lesson-view">
      <nav className="lesson-nav" aria-label="Lessons">
        <div className="lesson-weeks">
          {data.weeks.map((w) => (
            <a key={w.n} href={hrefFor('lesson', w.tasks[0]?.id)}
               className={`lesson-week ${w.n === weekN ? 'is-on' : ''} ${w.unlocked ? '' : 'is-locked'}`}
               title={`Week ${w.n}: ${w.title}${w.unlocked ? '' : ' (locked)'}`}>{w.n}</a>
          ))}
        </div>
        <p className="lesson-week-title">{week?.title}</p>
        <ul className="lesson-tasks">
          {week?.tasks.map((t) => {
            const done = t.items.length > 0 && t.items.every((i) => i.checked)
            const has = lessons?.week === weekN && lessons.lessons.some((l) => l.task === t.id && l.markdown)
            return (
              <li key={t.id}>
                <a href={hrefFor('lesson', t.id)}
                   className={[t.id === task && 'is-on', !has && 'no-lesson'].filter(Boolean).join(' ')}
                   title={has ? undefined : 'No lesson written yet'}>
                  <span className="lesson-task-mark">{done ? '[x]' : '[ ]'}</span>
                  <span>{t.id} {t.title}</span>
                </a>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="lesson-main">
        {trackerTask ? (
          <Panel title={`Task ${trackerTask.id}: ${trackerTask.title}`} meta="acceptance criteria"
                 className="lesson-criteria"
                 actions={<>
                   {trackerTask.kind === 'QUIZ' && (
                     <a className="hdr-btn" href={hrefFor('quiz', `W${trackerTask.id}.quiz`)}>[ quiz ]</a>
                   )}
                   {docs?.plan && <a className="hdr-btn" href={hrefFor('doc', docs.plan)}>[ plan ]</a>}
                   {docs?.walkthrough && (
                     <a className="hdr-btn" href={hrefFor('doc', docs.walkthrough)}>[ walkthrough ]</a>
                   )}
                 </>}>
            {!week?.unlocked && <p className="muted"><Tag kind="locked" /> Unlocks when week {weekN - 1} is complete.</p>}
            {refusal && <p className="refusal" role="alert"><Tag kind="fail">refused</Tag> {refusal}</p>}
            <Checklist items={trackerTask.items} currentId={data.current?.item.id}
                       locked={!week?.unlocked} onToggle={toggle} />
            {docs?.folder && <p className="muted lesson-folder">▸ workspace/{docs.folder}/</p>}
          </Panel>
        ) : (
          <Panel title="Lesson"><p className="muted">No task {task} in the tracker.</p></Panel>
        )}

        <Panel title="Lesson" meta={trackerTask ? `curriculum/week${weekN}/lesson_${task.replace('.', '_')}.md` : undefined}
               className="lesson-body">
          {error && <p role="alert"><Tag kind="fail">error</Tag> {error}</p>}
          {lesson?.markdown ? (
            <Markdown text={lesson.markdown} />
          ) : lessons && !error ? (
            <p className="muted">
              No lesson for this task yet. Lessons after week 1 are written just-in-time: ask the
              tutor in Claude Code to start the task.
            </p>
          ) : null}
        </Panel>
      </div>
    </div>
  )
}
