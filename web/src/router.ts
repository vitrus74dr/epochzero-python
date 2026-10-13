import { useEffect, useState } from 'react'

export type View = 'dashboard' | 'workbench' | 'quiz'
/** `file` is a workspace path for the workbench and a quiz id for the quiz view. */
export type Route = { view: View; file: string | null }

// #/            -> dashboard
// #/workbench   -> workbench
// #/workbench/week1/calc.py -> workbench with a file open
// #/quiz, #/quiz/W1.2.quiz  -> quiz list, or one quiz
export function parseHash(hash: string): Route {
  const h = hash.replace(/^#\/?/, '')
  for (const view of ['workbench', 'quiz'] as const) {
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
