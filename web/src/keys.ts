// Global keyboard shortcuts. Chords like `g d` only fire outside text inputs,
// the editor and the terminal; modifier shortcuts work everywhere.

export type Shortcut = { keys: string; label: string }

export const SHORTCUTS: Shortcut[] = [
  { keys: 'g d', label: 'Dashboard' },
  { keys: 'g w', label: 'Workbench' },
  { keys: 'Ctrl/Cmd + Enter', label: 'Save and run current file' },
  { keys: 'Ctrl/Cmd + S', label: 'Save current file' },
  { keys: 'Ctrl/Cmd + Shift + L', label: 'Toggle dark / light' },
  { keys: '?', label: 'This sheet' },
  { keys: 'Esc', label: 'Close this sheet' },
]

export function isTyping(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null
  if (!el) return false
  return el.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName) ||
    !!el.closest?.('.cm-editor, .xterm')
}

export const mod = (e: KeyboardEvent) => e.ctrlKey || e.metaKey
