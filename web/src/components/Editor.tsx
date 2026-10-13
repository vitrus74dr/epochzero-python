import { useEffect, useRef } from 'react'
import { autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { python } from '@codemirror/lang-python'
import { bracketMatching, indentOnInput, indentUnit } from '@codemirror/language'
import { highlightSelectionMatches, searchKeymap } from '@codemirror/search'
import { Compartment, EditorState, Prec } from '@codemirror/state'
import {
  EditorView, drawSelection, highlightActiveLine, highlightActiveLineGutter,
  highlightSpecialChars, keymap, lineNumbers,
} from '@codemirror/view'
import { codemirrorTheme } from '../theme/editorTheme'
import { onThemeChange } from '../theme/theme'

type Props = {
  path: string
  initial: string
  onChange: (content: string) => void
  onSave: () => void
  onRun: () => void
  onRunTests: () => void
}

/** CodeMirror 6 editor. Remount (via key) to load a different file or a reloaded version. */
export function Editor({ path, initial, onChange, onSave, onRun, onRunTests }: Props) {
  const host = useRef<HTMLDivElement>(null)
  // Callbacks change every render; the editor reads them through refs.
  const cb = useRef({ onChange, onSave, onRun, onRunTests })
  cb.current = { onChange, onSave, onRun, onRunTests }

  useEffect(() => {
    const themeSlot = new Compartment()
    const isPython = path.endsWith('.py')
    const view = new EditorView({
      parent: host.current!,
      state: EditorState.create({
        doc: initial,
        extensions: [
          lineNumbers(),
          highlightActiveLineGutter(),
          highlightSpecialChars(),
          history(),
          drawSelection(),
          indentOnInput(),
          bracketMatching(),
          closeBrackets(),
          autocompletion(),
          highlightActiveLine(),
          highlightSelectionMatches(),
          indentUnit.of('    '), // spaces only: mixed tabs/spaces is a monitored pitfall
          EditorState.tabSize.of(4),
          isPython ? python() : [],
          Prec.highest(keymap.of([
            { key: 'Mod-s', preventDefault: true, run: () => { cb.current.onSave(); return true } },
            { key: 'Mod-Enter', preventDefault: true, run: () => { cb.current.onRun(); return true } },
            { key: 'Mod-Shift-Enter', preventDefault: true, run: () => { cb.current.onRunTests(); return true } },
            { key: 'Mod-Shift-t', preventDefault: true, run: () => { cb.current.onRunTests(); return true } },
          ])),
          keymap.of([...closeBracketsKeymap, ...defaultKeymap, ...searchKeymap,
                     ...historyKeymap, ...completionKeymap, indentWithTab]),
          themeSlot.of(codemirrorTheme()),
          EditorView.updateListener.of((u) => {
            if (u.docChanged) cb.current.onChange(u.state.doc.toString())
          }),
        ],
      }),
    })
    const off = onThemeChange(() => {
      view.dispatch({ effects: themeSlot.reconfigure(codemirrorTheme()) })
    })
    view.focus()
    return () => {
      off()
      view.destroy()
    }
    // `initial` is deliberately read once per mount; reloads remount via key.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path])

  return <div className="editor-host" ref={host} />
}
