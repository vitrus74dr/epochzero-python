import { useCallback, useEffect, useState } from 'react'
import { getQuiz, getQuizzes, submitQuiz } from '../api'
import { Inline } from '../components/Inline'
import { Panel } from '../components/Panel'
import { Tag } from '../components/Tag'
import { Terminal } from '../components/Terminal'
import { onServerEvent } from '../events'
import { isTyping, mod } from '../keys'
import { hrefFor, navigate } from '../router'
import type { QuizList, QuizResult, QuizSpec, QuizSummary } from '../types'

type Mode = 'intro' | 'asking' | 'result' | 'terminal'

function QuizRow({ q, selected }: { q: QuizSummary; selected: boolean }) {
  return (
    <li>
      <a href={hrefFor('quiz', q.id)} className={`quiz-row ${selected ? 'is-on' : ''}`}
         aria-current={selected ? 'true' : undefined}>
        <span className="quiz-row-id">{q.id}</span>
        <span className="quiz-row-title">{q.title}</span>
        <span className="quiz-row-state">
          {!q.unlocked ? <Tag kind="locked" />
            : q.last ? <Tag kind={q.last.passed ? 'pass' : 'fail'}>{`${q.last.score}/${q.last.total}`}</Tag>
            : <span className="muted">new</span>}
        </span>
      </a>
    </li>
  )
}

export function QuizView({ quizId }: { quizId: string | null }) {
  const [list, setList] = useState<QuizList | null>(null)

  const refreshList = useCallback(async () => {
    const r = await getQuizzes()
    if (r.ok) setList(r.data)
  }, [])

  useEffect(() => {
    refreshList()
    return onServerEvent((e) => {
      if (['quizzes', 'curriculum', 'tracker'].includes(e.type)) refreshList()
    })
  }, [refreshList])

  return (
    <div className="quiz-view">
      <Panel title="Quizzes" meta={list ? String(list.quizzes.length) : undefined} className="quiz-list">
        {list && list.quizzes.length === 0 && (
          <p className="muted">
            No quizzes yet. The tutor authors them with <code className="inline-code">/quiz</code> into{' '}
            <code className="inline-code">curriculum/weekN/</code>.
          </p>
        )}
        <ul className="quiz-rows">
          {list?.quizzes.map((q) => <QuizRow key={q.id} q={q} selected={q.id === quizId} />)}
        </ul>
        {list?.errors.map((e) => (
          <p key={e.file} className="quiz-spec-error">
            <Tag kind="fail">spec</Tag> {e.file}: <span className="muted">{e.error}</span>
          </p>
        ))}
      </Panel>
      {/* Keyed so switching quizzes starts from a clean slate. */}
      <QuizDetail key={quizId ?? ''} quizId={quizId}
                  summary={list?.quizzes.find((q) => q.id === quizId) ?? null} />
    </div>
  )
}

function QuizDetail({ quizId, summary }: { quizId: string | null; summary: QuizSummary | null }) {
  const [spec, setSpec] = useState<QuizSpec | null>(null)
  const [mode, setMode] = useState<Mode>('intro')
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<QuizResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [termKey, setTermKey] = useState(0)

  useEffect(() => {
    if (!quizId) return
    getQuiz(quizId).then((r) => {
      if (r.ok) setSpec(r.data)
      else setError(r.error)
    })
  }, [quizId])

  const question = spec?.questions[index]
  const allAnswered = !!spec && spec.questions.every((q) => q.id in answers)

  const start = () => {
    setAnswers({})
    setIndex(0)
    setResult(null)
    setError(null)
    setMode('asking')
  }

  const submit = useCallback(async () => {
    if (!spec || !allAnswered) return
    const r = await submitQuiz(spec.id, answers)
    if (r.ok) {
      setResult(r.data)
      setMode('result')
    } else {
      setError(r.error)
    }
  }, [spec, answers, allAnswered])

  const choose = (choice: number) => {
    if (!question) return
    setAnswers((a) => ({ ...a, [question.id]: choice }))
  }

  const next = () => {
    if (!spec || !question || !(question.id in answers)) return
    if (index < spec.questions.length - 1) setIndex(index + 1)
    else submit()
  }

  // Keyboard-first: 1-9 choose, Enter next/submit, Backspace back.
  useEffect(() => {
    const on = (e: KeyboardEvent) => {
      if (mod(e) || e.altKey || isTyping(e.target) || mode === 'terminal') return
      if (mode === 'asking' && question) {
        const n = Number(e.key)
        if (Number.isInteger(n) && n >= 1 && n <= question.choices.length) {
          e.preventDefault()
          choose(n - 1)
        } else if (e.key === 'Enter') {
          e.preventDefault()
          next()
        } else if (e.key === 'Backspace' && index > 0) {
          e.preventDefault()
          setIndex(index - 1)
        }
      } else if (mode === 'intro' && e.key === 'Enter' && spec && summary?.unlocked &&
                 !(e.target instanceof HTMLButtonElement)) {
        e.preventDefault()
        start()
      }
    }
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  })

  const locked = summary !== null && !summary.unlocked

  return (
    <Panel title={spec ? spec.title : 'Quiz'} className="quiz-detail"
           meta={spec ? `${spec.id}${summary?.item ? ` ▸ ${summary.item}` : ''}` : undefined}
           actions={spec && mode !== 'terminal' && !locked && (
             <button className="hdr-btn" onClick={() => { setTermKey((k) => k + 1); setMode('terminal') }}
                     title="Same quiz with rich + inquirer in a real terminal">[ run in terminal ]</button>
           )}>
      {!quizId && <p className="muted">Pick a quiz on the left.</p>}
      {error && <p role="alert"><Tag kind="fail">error</Tag> {error}</p>}
      {summary?.problem && <p><Tag kind="fail">spec</Tag> {summary.problem}</p>}

      {spec && mode === 'intro' && (
        <div className="quiz-intro">
          <p>{spec.questions.length} questions · pass mark {spec.pass_mark}/{spec.questions.length}</p>
          {summary?.last && (
            <p className="muted">
              last attempt <Tag kind={summary.last.passed ? 'pass' : 'fail'}>
                {`${summary.last.score}/${summary.last.total}`}
              </Tag> via {summary.last.by}
            </p>
          )}
          {locked ? (
            <p className="muted"><Tag kind="locked" /> This quiz's week is locked.</p>
          ) : (
            <p>
              <button className="hdr-btn hdr-run" onClick={start} autoFocus>[ start ▸ ]</button>{' '}
              <span className="muted">or press Enter</span>
            </p>
          )}
        </div>
      )}

      {spec && mode === 'asking' && question && (
        <div className="quiz-q">
          <p className="muted quiz-progress">
            ── {index + 1}/{spec.questions.length}{' '}
            {spec.questions.map((q, i) => (
              <span key={q.id} className={i === index ? 'quiz-dot is-on' : 'quiz-dot'}>
                {q.id in answers ? '▰' : '▱'}
              </span>
            ))}
          </p>
          <p className="quiz-prompt"><Inline text={question.prompt} /></p>
          <ol className="quiz-choices">
            {question.choices.map((c, i) => {
              const on = answers[question.id] === i
              return (
                <li key={i}>
                  <button className={`quiz-choice ${on ? 'is-on' : ''}`} onClick={() => choose(i)}
                          aria-pressed={on}>
                    <span className="quiz-key">{on ? '▸' : ' '}{i + 1}</span>
                    <span><Inline text={c} /></span>
                  </button>
                </li>
              )
            })}
          </ol>
          <p className="quiz-nav">
            <button className="hdr-btn" onClick={() => setIndex(index - 1)} disabled={index === 0}>
              [ ◂ back ]
            </button>{' '}
            <button className="hdr-btn hdr-run" onClick={next} disabled={!(question.id in answers)}>
              {index === spec.questions.length - 1 ? '[ submit ▸ ]' : '[ next ▸ ]'}
            </button>
            <span className="muted"> 1–{question.choices.length} choose · Enter next · Backspace back</span>
          </p>
        </div>
      )}

      {spec && mode === 'result' && result && (
        <div className="quiz-result">
          <p className="quiz-score">
            <Tag kind={result.passed ? 'pass' : 'fail'} /> {result.score}/{result.total}
            <span className="muted"> · pass mark {result.pass_mark} · recorded for {result.item}</span>
          </p>
          <ul className="quiz-review">
            {result.results.map((r, i) => (
              <li key={r.id}>
                <Tag kind={r.correct ? 'pass' : 'fail'} />{' '}
                <Inline text={spec.questions[i].prompt} />
                {r.correct && r.explain && <p className="muted quiz-explain"><Inline text={r.explain} /></p>}
              </li>
            ))}
          </ul>
          <p className="muted">
            {result.passed
              ? `Passed: tick ${result.item} on the dashboard.`
              : `Missed questions aren't explained here. Ask the tutor to walk through them, then retake.`}
          </p>
          <p>
            <button className="hdr-btn hdr-run" onClick={start}>[ retake ]</button>{' '}
            <button className="hdr-btn" onClick={() => navigate('dashboard')}>[ dashboard ]</button>
          </p>
        </div>
      )}

      {spec && mode === 'terminal' && (
        <div className="quiz-term">
          <p className="muted">
            Terminal quiz: ↑/↓ then Enter. It records the same result as the browser.{' '}
            <button className="hdr-btn" onClick={() => setMode('intro')}>[ close ]</button>
          </p>
          <Terminal key={termKey} mode="quiz" file={spec.id} active />
        </div>
      )}
    </Panel>
  )
}
