// Theme state. index.html sets data-theme before first paint; this module
// owns changes after that. Keep STORAGE_KEY in sync with index.html.

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'pygrid.theme'
const listeners = new Set<(t: Theme) => void>()

export function getTheme(): Theme {
  return document.documentElement.dataset.theme === 'light' ? 'light' : 'dark'
}

export function setTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme
  try {
    localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // Storage blocked: the choice just won't persist.
  }
  listeners.forEach((fn) => fn(theme))
}

export function toggleTheme(): void {
  setTheme(getTheme() === 'dark' ? 'light' : 'dark')
}

/** Subscribe to theme changes; returns an unsubscribe function. */
export function onThemeChange(fn: (t: Theme) => void): () => void {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export const TOKEN_NAMES = [
  'bg', 'surface', 'surface-2', 'border', 'grid', 'text', 'text-muted',
  'accent', 'accent-2', 'success', 'danger', 'info', 'selection',
] as const
export type TokenName = (typeof TOKEN_NAMES)[number]

/** Resolved token values for the current theme. xterm.js and CodeMirror
 *  can't read CSS variables, so their themes are built from this. */
export function readTokens(): Record<TokenName, string> {
  const style = getComputedStyle(document.documentElement)
  return Object.fromEntries(
    TOKEN_NAMES.map((n) => [n, style.getPropertyValue(`--${n}`).trim()]),
  ) as Record<TokenName, string>
}
