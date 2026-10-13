// Global keyboard shortcuts. Chords like `g d` only fire outside text inputs,
// the editor and the terminal; modifier shortcuts work everywhere.

export type Shortcut = { keys: string; label: string }

export const SHORTCUTS: Shortcut[] = [
  { keys: 'g d', label: 'Dashboard' },
  { keys: 'g w', label: 'Workbench' },
  { keys: 'g q', label: 'Quizzes' },
  { keys: 'Ctrl/Cmd + Enter', label: 'Save and run current file' },
  { keys: 'Ctrl/Cmd + Shift + Enter', label: 'Run tests for the current folder' },
  { keys: 'Ctrl/Cmd + Shift + T', label: 'Same, where the browser allows it' },
  { keys: '1-9 · Enter · Backspace', label: 'Quiz: choose · next / submit · back' },
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

/** Run-tests shortcut. Ctrl+Shift+T (the spec's binding) is reserved by most
 *  browsers for "reopen closed tab", so Ctrl+Shift+Enter is the reliable one. */
export const isRunTests = (e: KeyboardEvent) =>
  mod(e) && e.shiftKey && (e.key === 'Enter' || e.key.toLowerCase() === 't')
