# PYGRID: app development rules

This repo root is the **app-dev zone**: write complete, working code normally.
`workspace/` is the **tutor zone** and has its own `workspace/CLAUDE.md` (Socratic rules);
those rules apply only to the learner's code there.

Read `HANDOFF.md` for the spec and build phases. `CURRICULUM_TRACKER.md` is the
source of truth for learner progress; never renumber or reword its item IDs.

## Commands
- `uv run pygrid` builds `web/dist` if missing, serves on 127.0.0.1:8765, opens the browser
- `uv run pygrid --rebuild` rebuilds the UI first
- Dev: `uv run pygrid --dev` (API only) + `pnpm -C web dev` (UI on :5173, proxies /api)
- Tests: `capped -m 8G -- uv run pytest -q`; UI typecheck + build: `pnpm -C web build`

## Invariants
- Bind 127.0.0.1 only. Every /api route (HTTP, SSE, WebSocket) goes through
  `GuardMiddleware` in `server/main.py`: Host/Origin allow-list + session cookie.
- Colours come from `web/src/theme/tokens.css` only. `tests/test_contrast.py` enforces
  WCAG AA on every text/surface pair; if you change a token, the test must still pass.
- xterm.js and CodeMirror can't read CSS variables: build their themes from
  `readTokens()` and rebuild them in `onThemeChange` (`web/src/theme/theme.ts`).
- Style: no glows, no neon, no text gradients. Motion 120–160ms, `steps()` or linear,
  disabled under `prefers-reduced-motion`.
