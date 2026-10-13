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
