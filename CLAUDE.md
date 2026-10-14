# EpochZero Python: app development rules

This repo root is the **app-dev zone**: write complete, working code normally.
`workspace/` is the **tutor zone** and has its own `workspace/CLAUDE.md` (Socratic rules);
those rules apply only to the learner's code there.

Read `HANDOFF.md` for the original spec and build phases. `CURRICULUM_TRACKER.md` is the
curriculum (weeks, tasks, item IDs and wording); never renumber or reword an item
(`tests/fixtures/tracker_items.txt` pins them). A learner's ticks are NOT in that file: they
live in `progress/checked.json` (`server/progress.py`), so students can `git pull` updates.

## Commands
- `uv run epochzero` builds `web/dist` if missing, serves on 127.0.0.1:8765, opens the browser
- `uv run epochzero --rebuild` rebuilds the UI first
- Dev: `uv run epochzero --dev` (API only) + `pnpm -C web dev` (UI on :5173, proxies /api)
- Tests: `capped -m 8G -- uv run pytest -q`; UI typecheck + build: `pnpm -C web build`
- `web/dist/` is committed (students need only uv). After any UI change, rebuild and commit
  it; `tools/check_all.sh` fails if it's stale (Vite builds are reproducible)
- Content checks: `tools/check_all.sh` (app tests, UI build, every lesson snippet run in a
  learner env with Arcade headless, stub tests fail cleanly, platformer levels reachable).
  `tools/learner_env.sh` creates `.learner-env/` with the course's libraries; the parts run
  separately too (`tools/check_md.py`, `tools/check_stubs.sh`, `tools/check_levels.py`).
  `tools/check_solutions.sh` runs every stub's tests against the private reference solutions
  in `$EPOCHZERO_SOLUTIONS` (default `../pygrid-solutions`, outside this public repo; skipped
  if absent). Solutions must never be committed here. After changing a stub's tests, update
  its solution there.
  Run it after any change under `curriculum/`.
- Terminal quiz: `uv run epochzero-quiz <quiz id>` (needs a real TTY; the cockpit runs it in its pty)
- Tutor CLI: `uv run epochzero-tutor status|verify|record|checkoff|quiz-add|quiz-results`; the
  slash commands in `workspace/.claude/commands/` call it via the `bin/` shim

## Invariants
- Bind 127.0.0.1 only. Every /api route (HTTP, SSE, WebSocket) goes through
  `GuardMiddleware` in `server/main.py`: Host/Origin allow-list + session cookie.
- Ticking goes through `check_item()` in `server/tracker_api.py` (tracker lock + verification
  gate + week lock), which writes `progress/checked.json`. Every reader uses
  `progress.load_state(paths)`, never `tracker.load()` directly. The tracker file is never written.
- Which kind of record may verify an item is decided by `verify_kind()` in
  `server/verifications.py`: a pytest run only records "pytest" items, a quiz only its
  task's "Quiz:" item. Answers and explanations for missed questions never reach the browser.
- Tutor commands must call plain `epochzero-tutor ...`: Claude Code's permission check refuses
  commands with shell variable expansion, and the tutor session can only touch `workspace/`,
  so anything outside it (tracker, progress/, curriculum/) needs a `epochzero-tutor` subcommand.
- Linux, macOS and Windows: platform differences live only in `server/compat.py` (locks,
  process-tree kill, shell, venv dir, UTF-8 stdio) and `server/terminal.py` (ptyprocess vs
  pywinpty). Read/write text with `encoding="utf-8"`. `.github/workflows/tests.yml` runs the
  app tests, `tools/smoke_launch.py` and the tutor shims on all three; keep it green.
- Task folders are `workspace/weekN/tN.M-<slug>/` (`server/tasks.py`).
- Curriculum content: `curriculum/weekN/lesson_N_M.md`, `quiz_N_M.json`, `stubs/tN.M-<slug>/`.
  Stubs hold tests plus signature-only code, never solutions; `tests/test_lessons.py` checks
  every stub test fails cleanly (fails, doesn't error) until implemented.
- Colours come from `web/src/theme/tokens.css` only. `tests/test_contrast.py` enforces
  WCAG AA on every text/surface pair; if you change a token, the test must still pass.
- xterm.js and CodeMirror can't read CSS variables: build their themes from
  `readTokens()` and rebuild them in `onThemeChange` (`web/src/theme/theme.ts`).
- Style: no glows, no neon, no text gradients. Motion 120–160ms, `steps()` or linear,
  disabled under `prefers-reduced-motion`.
