import { useEffect, useState } from 'react'

export type View = 'dashboard' | 'lesson' | 'workbench' | 'quiz' | 'doc'
/** `file` is a workspace path (workbench, doc), a quiz id (quiz) or a task id (lesson). */
export type Route = { view: View; file: string | null }

// #/            -> dashboard
// #/workbench   -> workbench
// #/workbench/week1/calc.py -> workbench with a file open
// #/quiz, #/quiz/W1.2.quiz  -> quiz list, or one quiz
// #/lesson, #/lesson/1.3 -> current task's lesson, or task 1.3's
// #/doc/week1/t1.3-calc/implementation_plan.md -> rendered markdown
export function parseHash(hash: string): Route {
  const h = hash.replace(/^#\/?/, '')
  for (const view of ['lesson', 'workbench', 'quiz', 'doc'] as const) {
    if (h === view || h.startsWith(`${view}/`)) {
      const file = h.slice(view.length + 1)
      return { view, file: file ? decodeURIComponent(file) : null }
    }
  }
  return { view: 'dashboard', file: null }
}

export function hrefFor(view: View, file?: string | null): string {
  if (view === 'dashboard') return '#/'
  return file ? `#/${view}/${file.split('/').map(encodeURIComponent).join('/')}` : `#/${view}`
}

export function navigate(view: View, file?: string | null): void {
  window.location.hash = hrefFor(view, file)
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parseHash(window.location.hash))
  useEffect(() => {
    const on = () => setRoute(parseHash(window.location.hash))
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return route
}
