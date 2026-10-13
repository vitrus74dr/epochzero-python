import type { TrackerData } from './types'

export type SessionState = 'ok' | 'expired' | 'offline'

let sessionPromise: Promise<SessionState> | null = null

/** Trade the launch token in the URL for a session cookie, then strip it
 *  from the address bar so it doesn't linger in history. Memoized: a second
 *  caller (e.g. StrictMode's double effect) must wait for the same exchange,
 *  not race it with a cookie-less status check. */
export function initSession(): Promise<SessionState> {
  sessionPromise ??= exchangeToken()
  return sessionPromise
}

async function exchangeToken(): Promise<SessionState> {
  const url = new URL(window.location.href)
  const token = url.searchParams.get('token')
  if (token) {
    url.searchParams.delete('token')
    window.history.replaceState(null, '', url.pathname + url.search + url.hash)
    try {
      await fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })
    } catch {
      return 'offline'
    }
  }
  try {
    const res = await fetch('/api/status')
    if (res.ok) return 'ok'
    return res.status === 401 ? 'expired' : 'offline'
  } catch {
    return 'offline'
  }
}

export type Result<T> = { ok: true; data: T } | { ok: false; status: number; error: string }

async function call<T>(path: string, init?: RequestInit): Promise<Result<T>> {
  try {
    const res = await fetch(path, init)
    const body = await res.json().catch(() => ({}))
    if (res.ok) return { ok: true, data: body as T }
    return { ok: false, status: res.status, error: body.detail ?? res.statusText }
  } catch {
    return { ok: false, status: 0, error: 'API offline' }
  }
}

export const getTracker = () => call<TrackerData>('/api/tracker')

export const checkItem = (item: string, checked: boolean) =>
  call<TrackerData>('/api/tracker/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item, checked }),
  })

export type TreeNode = { name: string; path: string; type: 'file' | 'dir'; children?: TreeNode[] }
export type FileData = { path: string; content: string; version: string }

export const getTree = () => call<{ root: string; children: TreeNode[] }>('/api/files/tree')

export const readFile = (path: string) =>
  call<FileData>(`/api/files?path=${encodeURIComponent(path)}`)

export const writeFile = (path: string, content: string, baseVersion: string | null, force = false) =>
  call<{ path: string; version: string }>(`/api/files?path=${encodeURIComponent(path)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, base_version: baseVersion, force }),
  })
