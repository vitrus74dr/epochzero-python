import { useEffect, useState } from 'react'

export type View = 'dashboard' | 'workbench'
export type Route = { view: View; file: string | null }

// #/            -> dashboard
// #/workbench   -> workbench
// #/workbench/week1/calc.py -> workbench with a file open
export function parseHash(hash: string): Route {
  const h = hash.replace(/^#\/?/, '')
  if (h === 'workbench' || h.startsWith('workbench/')) {
    const file = h.slice('workbench/'.length)
    return { view: 'workbench', file: h.includes('/') && file ? decodeURIComponent(file) : null }
  }
  return { view: 'dashboard', file: null }
}

export function hrefFor(view: View, file?: string | null): string {
  if (view === 'dashboard') return '#/'
  return file ? `#/workbench/${file.split('/').map(encodeURIComponent).join('/')}` : '#/workbench'
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
