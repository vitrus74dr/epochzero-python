// CodeMirror and xterm.js themes built from the CSS tokens, because neither
// can read CSS variables. Rebuild on every theme change.

import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { EditorView } from '@codemirror/view'
import type { Extension } from '@codemirror/state'
import { tags as t } from '@lezer/highlight'
import type { ITheme } from '@xterm/xterm'
import { getTheme, readTokens } from './theme'

export function codemirrorTheme(): Extension {
  const k = readTokens()
  const dark = getTheme() === 'dark'
  const base = EditorView.theme({
    '&': { color: k.text, backgroundColor: k.bg, height: '100%' },
    '.cm-scroller': {
      fontFamily: 'var(--font-mono)',
      fontSize: '14px',
      lineHeight: '1.55',
      fontVariantLigatures: 'normal', // ligatures in the editor only
    },
    '.cm-content': { caretColor: k.accent },
    '.cm-cursor, .cm-dropCursor': { borderLeft: `2px solid ${k.accent}` },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection': {
      backgroundColor: `${k.selection} !important`,
    },
    '.cm-activeLine': { backgroundColor: k.surface },
    '.cm-gutters': { backgroundColor: k.bg, color: k['text-muted'], border: 'none',
                     borderRight: `1px solid ${k.border}` },
    '.cm-activeLineGutter': { backgroundColor: k.surface, color: k.text },
    '.cm-matchingBracket, &.cm-focused .cm-matchingBracket': {
      backgroundColor: k['surface-2'], outline: `1px solid ${k.border}`,
    },
    '.cm-searchMatch': { backgroundColor: k['surface-2'], outline: `1px solid ${k['accent-2']}` },
    '.cm-panels': { backgroundColor: k.surface, color: k.text, borderColor: k.border },
    '.cm-tooltip': { backgroundColor: k.surface, color: k.text, border: `1px solid ${k.border}` },
    '.cm-tooltip-autocomplete > ul > li[aria-selected]': {
      backgroundColor: k.selection, color: k.text,
    },
  }, { dark })

  const highlight = HighlightStyle.define([
    { tag: [t.keyword, t.controlKeyword, t.operatorKeyword, t.moduleKeyword], color: k.accent },
    { tag: [t.string, t.special(t.string)], color: k.success },
    { tag: [t.number, t.bool, t.null, t.atom], color: k['accent-2'] },
    { tag: [t.comment, t.lineComment, t.blockComment], color: k['text-muted'], fontStyle: 'italic' },
    { tag: [t.function(t.definition(t.variableName)), t.function(t.variableName)], color: k.info },
    { tag: [t.className, t.definition(t.className), t.typeName], color: k['accent-2'] },
    { tag: [t.self, t.special(t.variableName)], color: k.magenta },
    { tag: t.invalid, color: k.danger },
  ])

  return [base, syntaxHighlighting(highlight)]
}

export function xtermTheme(): ITheme {
  const k = readTokens()
  return {
    background: k.bg,
    foreground: k.text,
    cursor: k.accent,
    cursorAccent: k.bg,
    selectionBackground: k.selection,
    black: k['surface-2'],
    red: k.danger,
    green: k.success,
    yellow: k['accent-2'],
    blue: k.info,
    magenta: k.magenta,
    cyan: k.accent,
    white: k.text,
    brightBlack: k['text-muted'],
    brightRed: k.danger,
    brightGreen: k.success,
    brightYellow: k['accent-2'],
    brightBlue: k.info,
    brightMagenta: k.magenta,
    brightCyan: k.accent,
    brightWhite: k.text,
  }
}
