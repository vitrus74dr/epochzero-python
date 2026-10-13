# HANDOFF — PYGRID: Local-First Python Curriculum Cockpit

> For Claude Code. Read this file, then `CURRICULUM_TRACKER.md` and `workspace/CLAUDE.md`, before writing any code.
> Codename "PYGRID" is a placeholder; rename freely.

---

## 0. TL;DR

Build a **local-first web app** that runs an 8-week Python curriculum (CLI → OOP → APIs → Arcade games → scikit-learn). Claude Code is the **tutor** in the terminal. The web app is the **student cockpit**: the tracker, lessons, a code editor, a real terminal, quizzes and test results, all in one browser tab.

Look and feel: **cyberpunk terminal without neon.** Graphite surfaces, muted teal and amber accents, box-drawing details, chamfered panel corners, excellent readability, and a dark/light toggle.

Everything runs on `127.0.0.1`. There is no cloud, no accounts and no telemetry.

---

## 1. Review of the original master prompt: what changes and why

The original prompt was written for **Google Antigravity / Gemini 3 Pro**. Most of its pedagogy is sound, but the tool names and a few technical claims are wrong for Claude Code. Some are wrong for the libraries themselves.

### 1a. Tool and IDE translation

| Original (Antigravity) | Claude Code equivalent |
|---|---|
| `read_resource`, `write_to_file`, `replace_file_content` | `Read`, `Write`, `Edit` |
| `run_command` | `Bash` |
| "browser subagent" for docs | `WebFetch` / `WebSearch` against official docs |
| `Cmd+I` inline review | The student asks in chat; Claude reviews with `Read` and gives line-referenced feedback |
| `/plan` | Plan mode (Shift+Tab to cycle modes) |
| `/grill-me` | **Custom command** we create: `.claude/commands/grill-me.md` |
| Master prompt pasted each session | `workspace/CLAUDE.md`, which loads automatically |
| `implementation_plan.md` / `walkthrough.md` "artifacts" | Plain files in `workspace/weekN/<project>/` that the cockpit renders |

### 1b. Structural problem: tutor rules vs. building the app

"Never write the full solution" must apply to the **learner's code**, not to this app. Otherwise Claude Code will refuse to build the cockpit.

The fix is two zones with separate `CLAUDE.md` files:
- `/` (repo root): app development. Claude writes complete code normally.
- `/workspace/`: tutor zone. Socratic rules apply.

### 1c. Interactive quizzes can't be driven by Claude Code's Bash

Claude Code's `Bash` is not an interactive TTY. It cannot press arrow keys in an `inquirer` prompt or "ask the student" from inside a running script.

The fix is for quizzes to run in the **cockpit's real PTY terminal** (xterm.js connected to a pty over WebSocket), where `inquirer` and `rich` work properly. Results are written to `progress/quizzes/<id>.json`, which Claude reads to grade and check off.

### 1d. Technical errors in the tracker (fixed in the new tracker)

1. **Week 6: `PhysicsEngineSimple` has no gravity.** It is the top-down engine. Platformers need `arcade.PhysicsEnginePlatformer`.
2. **Week 5: `start_render()` / `finish_render()`** belong to Arcade's static "draw once" style. An *animated* screensaver uses an `arcade.Window` (or `View`) with `self.clear()` in `on_draw` and motion in `on_update(delta_time)`. Arcade 3.x also renamed many drawing functions, so 2.6-era tutorials break. **Claude Code must check the installed Arcade version's docs before writing any lesson code.**
3. **Week 8: `load_diabetes()` has no categorical columns, and its default features are already centered and scaled.** That makes `StandardScaler + OneHotEncoder` meaningless. Use `load_diabetes(scaled=False, as_frame=True)`, treat `sex` (values 1/2) as categorical for `OneHotEncoder`, and scale the rest. A "positive R²" is a very low bar; require beating a `DummyRegressor` baseline on a held-out test set.
4. **Week 6 verification "use /browser subagent to confirm file structures"** is not meaningful. It is replaced with a pytest that asserts every asset path resolves relative to the module (`Path(__file__).parent`).
5. **Week 4 Open Trivia DB:** responses are HTML-entity-encoded (`html.unescape`), the API is rate-limited, and failures are reported via `response_code`. Every `requests` call needs a `timeout=`, and `Timeout` must be handled alongside `ConnectionError`.
6. **Week 3 Leitner:** "hard cards repeat daily" is untestable if code calls `date.today()` internally. Require injecting `today` as a parameter.
7. **Tracker formatting:** the pasted version lost its `- [ ]` list markers and has no stable IDs, so it can't be parsed reliably. The new tracker adds `[W1.1.a]`-style IDs.
8. **Verification protocol:** requiring `implementation_plan.md` for every quiz is overkill. Plans are now required for `[PROJECT]` tasks only.

---

## 2. Repo layout

```
pygrid/
├── HANDOFF.md
├── CLAUDE.md                     # app-dev rules (normal coding)
├── CURRICULUM_TRACKER.md         # source of truth for progress
├── pyproject.toml                # uv-managed; Python 3.12
├── .claude/
│   └── commands/
│       ├── grill-me.md           # architecture interview before projects
│       ├── quiz.md               # generate a quiz spec + CLI runner for current task
│       ├── verify.md             # run pytest for a task, record result
│       └── checkoff.md           # tick tracker box only if verification passed
├── server/                       # FastAPI backend
│   ├── main.py                   # app factory, static serving, 127.0.0.1 bind
│   ├── tracker.py                # parse/serialize CURRICULUM_TRACKER.md
│   ├── fs.py                     # sandboxed file API (workspace/ only)
│   ├── pty_ws.py                 # WebSocket <-> pty bridge
│   ├── tests_runner.py           # pytest subprocess + result parsing
│   ├── quizzes.py                # load/grade quiz specs
│   └── watch.py                  # watchfiles -> SSE push to UI
├── web/                          # Vite + React + TypeScript
│   ├── index.html                # inline no-flash theme script
│   └── src/
│       ├── theme/tokens.css
│       ├── components/           # Panel, StatusBar, Tag, Checklist, ...
│       └── views/                # Dashboard, Lesson, Workbench, Quiz
├── curriculum/
│   ├── week1/ ... week8/         # lesson .md files + quiz specs (.json)
├── workspace/                    # learner's code lives here
│   ├── CLAUDE.md                 # TUTOR RULES (Socratic)
│   └── week1/ ...
└── progress/
    ├── verifications.json        # append-only log of passing checks
    └── quizzes/                  # quiz attempt results
```

---

## 3. Architecture

### Backend: FastAPI + uvicorn (Python 3.12, managed with `uv`)

| Endpoint | Purpose |
|---|---|
| `GET /api/tracker` | Parsed tracker: weeks → tasks → items with IDs and states |
| `POST /api/tracker/check` | Tick an item. **Refused unless** `progress/verifications.json` has a passing record for that ID |
| `GET /api/files/tree`, `GET/PUT /api/files?path=` | Read/write inside `workspace/` only (resolve and reject path traversal) |
| `POST /api/tests/run` | Run `pytest` on a task folder; stream output; parse JUnit XML for the pass/fail summary |
| `WS /api/pty` | Spawn a shell or `python <file>` in a real pty; bidirectional stream to xterm.js; handle resize |
| `GET /api/lessons/{week}` | Lesson markdown |
| `GET /api/quizzes/{id}`, `POST /api/quizzes/{id}/submit` | Quiz spec (without answers) and server-side grading |
| `GET /api/events` (SSE) | Push changes when Claude Code edits the tracker or workspace files |

- **PTY:** use `ptyprocess` on macOS/Linux and `pywinpty` on Windows. Arcade programs open their own native window from the subprocess, which is fine because this runs locally.
- **Single writer for the tracker:** both the app and Claude Code may tick boxes, but both go through the same rule: no passing verification record, no tick. Serialize writes with a file lock.
- **Launch:** `uv run pygrid` builds or serves `web/dist`, binds `127.0.0.1:8765`, and opens the browser. In dev, Vite proxies `/api` to the backend.

### Frontend: React + TypeScript + Vite

- **Editor:** CodeMirror 6 with Python language support and a custom theme built from the tokens below.
- **Terminal:** xterm.js with the fit addon. Its theme object must be generated from the same tokens and updated on theme toggle, because xterm doesn't read CSS variables.
- **Markdown:** react-markdown with code highlighting, used for lessons, `implementation_plan.md` and `walkthrough.md`.

### Views

1. **Dashboard:** 8-week grid with progress per week, the current task, a "next action" line, and recent verifications. Locked weeks show as dimmed with a `[LOCKED]` tag.
2. **Lesson:** lesson markdown on the left, with the task's acceptance criteria pinned at top.
3. **Workbench:** file tree, editor, and terminal in resizable splits. A test results panel shows pass/fail per test.
4. **Quiz:** questions render in the browser (keyboard-first: `1–4` to choose, `Enter` to submit). A "Run in terminal" button launches the `rich`/`inquirer` CLI version of the same quiz in the pty.

### Status bar (tmux-style, always visible)

`PYGRID ▸ W1 ▸ T1.2 ▸ control-flow │ tests 4/5 │ ● dark │ 21:20`

---

## 4. Design system: "cyberpunk terminal, no neon"

**Principles:** restraint over glow. No `text-shadow` glows, no saturated magenta or cyan, and no gradients on text. The cyberpunk feel comes from **structure**: monospace UI chrome, box-drawing characters, bracketed tags, chamfered corners, a thin grid, and a blinking block cursor.

### Fonts (self-hosted via `@fontsource`; no CDN calls)

| Role | Font | Notes |
|---|---|---|
| UI chrome, code, terminal, headings | **JetBrains Mono** | 400/500/700; enable ligatures in the editor only |
| Lesson prose | **IBM Plex Sans** | 400/600; 17px, line-height 1.65, max ~72ch |
| Fallback | `ui-monospace, Menlo, Consolas` / `system-ui` | |

Headings use mono, uppercase, letter-spacing `0.08em`, at a modest size with a `// ` prefix glyph in the muted color.

### Color tokens (WCAG AA ≥ 4.5:1 for all text)

```css
:root, :root[data-theme="dark"] {
  --bg:        #0E1114;  /* deep graphite */
  --surface:   #151A1F;
  --surface-2: #1C2329;
  --border:    #2A323A;
  --grid:      #1A2026;  /* faint background grid lines */
  --text:      #C9D1D9;
  --text-muted:#7D8590;
  --accent:    #5FB3A8;  /* muted teal: primary actions, focus, cursor */
  --accent-2:  #D4A35A;  /* dim amber: current task, warnings */
  --success:   #7FB07F;
  --danger:    #C96A6A;
  --info:      #7A9CC6;
  --selection: #2B3E3B;
}
:root[data-theme="light"] {
  --bg:        #F3F1EC;  /* warm paper */
  --surface:   #FBFAF7;
  --surface-2: #ECE9E2;
  --border:    #D3CFC6;
  --grid:      #E7E4DD;
  --text:      #1C2226;
  --text-muted:#5B6570;
  --accent:    #2F7D72;
  --accent-2:  #9A6A1F;
  --success:   #3F7A3F;
  --danger:    #A84444;
  --info:      #3D628F;
  --selection: #CFE3DF;
}
```

**Verify every pair with a contrast checker in a unit test** (a small script that asserts ratios ≥ 4.5).

### Signature components

- **Panel:** 1px `--border`, chamfered top-right corner via `clip-path: polygon(...)` (8px cut), and a header strip like `┌─ EDITOR ── main.py ─┐` in muted mono.
- **Tag:** `[ PASS ]` `[ FAIL ]` `[ LOCKED ]` `[ QUIZ ]` `[ PROJECT ]`, mono, using the semantic colors on `--surface-2`.
- **Checklist:** `[x]` / `[ ]` rendered literally in mono, with the accent color on checked items.
- **Progress:** block characters `▰▰▰▰▱▱▱▱ 50%` rather than a smooth bar.
- **Cursor:** a 1-character block in `--accent` that blinks at 1s steps (no easing).
- **Background:** a faint 24px grid on `--bg` at `--grid`.
- **Optional scanlines:** off by default; a toggle in settings; very subtle (≤ 3% opacity).
- **Motion:** 120–160ms, `steps()` or linear. Respect `prefers-reduced-motion` (no blink, no scanlines).

### Dark/light toggle

- `data-theme` on `<html>`. The default comes from `prefers-color-scheme`. The user's choice persists in `localStorage` (wrapped in try/catch).
- An **inline script in `index.html`** sets the attribute before first paint to prevent a flash of the wrong theme.
- The toggle lives in the status bar as `● dark` / `○ light`, with keyboard shortcut `Ctrl/Cmd+Shift+L`.
- On toggle, rebuild the xterm and CodeMirror themes from the tokens.

### Keyboard-first

`g d` dashboard · `g l` lesson · `g w` workbench · `Ctrl/Cmd+Enter` run current file · `Ctrl/Cmd+Shift+T` run tests · `?` shortcut sheet.

---

## 5. Data contracts

### Tracker grammar (see `CURRICULUM_TRACKER.md`)

```
## Week N: Title                     -> week
### Task N.M: Title [PROJECT|QUIZ]?  -> task
- [ ] [WN.M.x] text                  -> checkable item (ID is stable, never renumber)
```

The parser must round-trip: parse → serialize must produce a byte-identical file. Add a test for this.

### Quiz spec: `curriculum/weekN/quiz_<task>.json`

```json
{
  "id": "W1.2.quiz",
  "title": "Boolean logic",
  "pass_mark": 4,
  "questions": [
    { "id": "q1", "prompt": "What does `not (True and False)` evaluate to?",
      "choices": ["True", "False", "None", "SyntaxError"],
      "answer": 0, "explain": "..." }
  ]
}
```

Answers never reach the browser; grading happens server-side. The CLI runner (`rich` + `inquirer`) reads the same spec and writes the same result format.

### Verification record: `progress/verifications.json` (append-only)

```json
{ "item": "W1.3.c", "kind": "pytest", "passed": true, "summary": "6 passed",
  "at": "2026-10-12T21:20:00-04:00", "by": "claude-code|app" }
```

---

## 6. Build phases (each ends with tests passing and a demo)

**Phase 1: Skeleton and theme**
- uv project, FastAPI, and Vite/React wired together. `uv run pygrid` opens the app.
- Token CSS, fonts, Panel, Tag and StatusBar, the theme toggle with no flash, and the contrast test.
- *Accept:* both themes render, the toggle persists, and the contrast test passes.

**Phase 2: Tracker**
- Parser/serializer with the round-trip test, the Dashboard view, and the SSE file watch.
- *Accept:* editing the tracker by hand updates the UI within 1s; the check endpoint refuses items with no verification.

**Phase 3: Workbench**
- Sandboxed file API (with path-traversal tests), CodeMirror, xterm.js and the PTY WebSocket.
- *Accept:* a script using `input()` and an `inquirer` list prompt works with arrow keys in the browser terminal.

**Phase 4: Tests and quizzes**
- The pytest runner with parsed results, the quiz view, the CLI quiz runner, and the verification log.
- *Accept:* a failing test shows `[ FAIL ]` with output; a passing run writes a record and enables the checkbox.

**Phase 5: Claude Code integration**
- `.claude/commands/*` and `workspace/CLAUDE.md`. Rendering for `implementation_plan.md` and `walkthrough.md`.
- *Accept:* `/verify W1.3` then `/checkoff W1.3.c` ticks the box, and the app updates live.

**Phase 6: Week 1 content**
- Lesson markdown, the quiz spec, and test stubs for Week 1 only. Later weeks get authored just-in-time by the tutor.

---

## 7. Security (this app executes arbitrary code)

- Bind **127.0.0.1 only**. Never `0.0.0.0`. Note this in the README.
- Check the `Origin`/`Host` headers on HTTP and WebSocket requests to block DNS-rebinding and cross-site WebSocket attacks from other browser tabs. Use a random per-launch token passed in the opened URL.
- The file API resolves paths and rejects anything outside `workspace/`.
- The PTY's working directory is `workspace/`; the learner's code runs as the user, so no sandbox is claimed. State that plainly.
- Make no outbound network calls from the app itself. Learner code in Week 4 may call APIs; that's fine.

---

## 8. Claude Code commands to create

- **`/grill-me`:** before any `[PROJECT]`, interview the student on 4–6 architecture questions (data model, class boundaries, error strategy, how it will be tested). Don't give answers until the student commits to one. Summarize the agreed decisions into `implementation_plan.md`.
- **`/quiz <task>`:** author `curriculum/weekN/quiz_<task>.json` (5 questions, plausible distractors, explanations). Tell the student to run it from the cockpit, then read `progress/quizzes/` to review missed questions.
- **`/verify <task>`:** run `pytest` for the task folder via Bash, then append a verification record on pass.
- **`/checkoff <item>`:** tick a tracker item only if a passing record exists. Otherwise, explain what's missing.

---

## 9. Open questions to confirm with the user (ask before Phase 3)

1. **Tutor inside the app?** For now Claude Code is the tutor, in a terminal beside the browser. Should the cockpit later get a chat panel pointed at a local OpenAI-compatible endpoint (llama.cpp / LiteLLM)? This is designed for but not built.
2. **OS targets:** macOS/Linux only, or Windows too? Windows support adds `pywinpty` and testing work.
3. **Who is the learner:** the user, or students (e.g. as a companion to a learning site)? This affects multi-profile support and how strictly week locking is enforced.
4. **Name and branding** for the app.
