import { useEffect, useRef } from 'react'
import { FitAddon } from '@xterm/addon-fit'
import { Terminal as XTerm } from '@xterm/xterm'
import '@xterm/xterm/css/xterm.css'
import { xtermTheme } from '../theme/editorTheme'
import { isRunTests } from '../keys'
import { onThemeChange } from '../theme/theme'

export type TermStatus = 'connecting' | 'running' | 'exited' | 'error'

type Props = {
  mode: 'shell' | 'run' | 'quiz'
  /** Workspace path for 'run', quiz id for 'quiz'. */
  file?: string
  onStatus?: (s: TermStatus, detail?: string) => void
  active: boolean
}

const DIM = '\x1b[90m'
const RESET = '\x1b[0m'

/** xterm.js wired to a pty over WS /api/pty. Remount (via key) to restart. */
export function Terminal({ mode, file, onStatus, active }: Props) {
  const host = useRef<HTMLDivElement>(null)
  const fitRef = useRef<FitAddon | null>(null)
  const termRef = useRef<XTerm | null>(null)
  const mounted = useRef(false)
  const statusRef = useRef(onStatus)
  statusRef.current = onStatus

  useEffect(() => {
    const term = new XTerm({
      fontFamily: "'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace",
      fontSize: 13,
      lineHeight: 1.2,
      cursorBlink: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      cursorStyle: 'block',
      scrollback: 5000,
      theme: xtermTheme(),
      allowProposedApi: false,
    })
    const fit = new FitAddon()
    fitRef.current = fit
    term.loadAddon(fit)
    term.open(host.current!)
    termRef.current = term
    // Let app-level shortcuts through instead of sending them to the pty.
    term.attachCustomKeyEventHandler((e) => {
      const mod = e.ctrlKey || e.metaKey
      if (isRunTests(e)) return false
      if (mod && e.key === 'Enter') return false
      if (mod && e.shiftKey && e.key.toLowerCase() === 'l') return false
      return true
    })
    try { fit.fit() } catch { /* host not laid out yet */ }

    const params = new URLSearchParams({ mode, cols: String(term.cols), rows: String(term.rows) })
    if (file) params.set('file', file)
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${window.location.host}/api/pty?${params}`)
    ws.binaryType = 'arraybuffer'
    statusRef.current?.('connecting')

    const send = (msg: object) => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg))
    }
    let exited = false

    ws.onmessage = (m) => {
      if (m.data instanceof ArrayBuffer) {
        term.write(new Uint8Array(m.data))
        return
      }
      const msg = JSON.parse(m.data)
      if (msg.type === 'started') {
        statusRef.current?.('running')
        send({ type: 'resize', cols: term.cols, rows: term.rows })
      } else if (msg.type === 'exit') {
        exited = true
        term.write(`\r\n${DIM}[process exited with code ${msg.code}]${RESET}\r\n`)
        statusRef.current?.('exited', String(msg.code))
      } else if (msg.type === 'error') {
        exited = true
        term.write(`${DIM}[${msg.message}]${RESET}\r\n`)
        statusRef.current?.('error', msg.message)
      }
    }
    ws.onclose = () => {
      if (!exited) {
        term.write(`\r\n${DIM}[disconnected]${RESET}\r\n`)
        statusRef.current?.('error', 'disconnected')
      }
    }

    const dataSub = term.onData((data) => send({ type: 'input', data }))
    const resizeSub = term.onResize(({ cols, rows }) => send({ type: 'resize', cols, rows }))
    const ro = new ResizeObserver(() => {
      try { fit.fit() } catch { /* hidden */ }
    })
    ro.observe(host.current!)
    const offTheme = onThemeChange(() => { term.options.theme = xtermTheme() })

    return () => {
      offTheme()
      ro.disconnect()
      dataSub.dispose()
      resizeSub.dispose()
      ws.close()
      term.dispose()
    }
  }, [mode, file])

  // A program just started (run, quiz) or the learner switched to this tab: keys should go
  // to it, not stay in the editor. A shell mounting with the page doesn't take focus.
  useEffect(() => {
    const first = !mounted.current
    mounted.current = true
    if (!active) return
    try { fitRef.current?.fit() } catch { /* ignore */ }
    if (!first || mode !== 'shell') termRef.current?.focus()
  }, [active, mode])

  return <div className="terminal-host" ref={host} hidden={!active} />
}
