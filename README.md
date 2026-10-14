# EpochZero Python

Learn Python by building real things: a 12-week course that takes you from `print()` to a
working **Pac-Man** with ghost AI. You'll also build a calculator, a terminal menu app, a
flashcard engine, a desktop habit tracker, a file organizer, a data report, a web API,
a digit recogniser, and Pong, Breakout, Snake, Tetris, Space Invaders and Asteroids.

Everything runs on your own computer, in one browser tab: the lessons, a code editor, a
real terminal, tests, quizzes and your progress. **Claude Code** is your tutor in that
terminal. It reviews your code, asks the questions that get you unstuck, and records what
you've achieved. It won't write your solutions for you.

A companion to [epochzero.org](https://epochzero.org).

## What you need

- **Linux or macOS.** (Windows isn't supported.)
- **git** and **[uv](https://docs.astral.sh/uv/getting-started/installation/)**, a Python
  tool that installs Python 3.12 for you. You don't need Python installed already.
- **[Claude Code](https://claude.com/claude-code)** for the tutor. This needs a Claude
  account. Without it you can still read every lesson, run tests and take quizzes, but the
  checks that need a tutor (and the `/grill-me` design interviews) won't be available.

## Get started

```sh
git clone https://github.com/vitrus74dr/epochzero-python.git
cd epochzero-python
uv run epochzero
```

The first run downloads Python and the app's libraries, then opens the course in your
browser. Next time, `uv run epochzero` is all you need.

Then, in the app:

1. Press **`g l`** (or click *lesson*) to read the first lesson.
2. Open the **workbench** (`g w`) and its **shell** tab: a terminal in your `workspace/` folder.
3. Run **`claude`** there. Accept the *trust this folder* prompt the first time, then say hi.
   The tutor looks at your progress and tells you where you are and what's next.

Press **`?`** anywhere in the app for the keyboard shortcuts.

## How the course works

- **12 weeks, 39 tasks.** Weeks unlock in order: finish every item in a week to open the next.
  Weeks 1–4 cover the foundations; 5–6 graphics and a platformer; 7–8 machine learning
  and a web app; 9–12 the arcade classics, ending with Pac-Man.
- **Every item needs proof** before you can tick it: a passing test run, a quiz score of
  4/5 or better, a design document, or a check by the tutor.
- **Projects start with a design interview** (`/grill-me`): you make the decisions, the
  tutor writes them up as a plan and turns it into tests, and then you write the code.
- **Your code lives in `workspace/`**, one folder per task (e.g. `workspace/week1/t1.3-calculator/`).

## Getting updates

```sh
git pull
```

Your work and progress are safe. Your code (`workspace/`) and your progress (`progress/`)
are never part of the course files, so updates can't overwrite or conflict with them.

## Troubleshooting

| Problem | Fix |
|---|---|
| *"127.0.0.1:8765 is in use"* | It's already running in another terminal; or start another copy with `uv run epochzero --port 8770`. |
| *"session expired"* in the browser | Each launch prints a new link with a fresh key. Use the latest one from the terminal. |
| The tutor can't run `epochzero-tutor` | Start `claude` from the app's own terminal (workbench ▸ shell), which sets it up. |
| A game window doesn't appear | Arcade games open a real window on your desktop; check behind the browser. |
| Week 1 setup changed this repo's `pyproject.toml` | You ran `uv init` without `--no-workspace` (see lesson 1.1). Ask the tutor; it knows the fix. |

## Safety

The app runs the code you write as **you**, with no sandbox, as any terminal does. It only
listens on `127.0.0.1` (your own machine), refuses requests from other websites, and needs the
per-launch key from the link it opens. Don't expose its port to a network.

## For maintainers

- Run in development: `uv run epochzero --dev` (API only) and `pnpm -C web dev` (UI on :5173).
- The built UI in `web/dist/` is committed so students need only uv. Rebuild with
  `pnpm -C web build` after UI changes, and commit the result.
- **Checks:** `tools/check_all.sh` runs the app tests, rebuilds the UI (and fails if the
  committed build is stale), runs every code example in every lesson in a learner-like
  environment (Arcade programs headless), confirms each starter-test folder fails cleanly on
  its stubs, and checks the platformer levels are playable. Run it after any change under `curriculum/`.
- Course content: `curriculum/weekN/` (`lesson_N_M.md`, `quiz_N_M.json`, `stubs/`), with the
  curriculum structure in `CURRICULUM_TRACKER.md`. Never renumber or reword a tracker item;
  `tests/fixtures/tracker_items.txt` pins them.
- App development notes: `CLAUDE.md`. The original design spec: `HANDOFF.md`.

## Licence

MIT; see [LICENSE](LICENSE).
