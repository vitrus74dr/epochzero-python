# PYGRID

A local-first cockpit for an 8-week Python curriculum. Claude Code is the tutor in
your terminal; the browser app holds the tracker, lessons, editor, terminal and quizzes.

```sh
uv run pygrid
```

Requires `uv` and `pnpm`. The first run builds the web UI.

## Lessons
Each task has a lesson (`g l`, or `[ lesson ]` on the dashboard) with its acceptance
criteria pinned on top. Week 1 ships in `curriculum/week1/` along with the W1.2 quiz and
starter tests (`stubs/`, copied in by `pygrid-tutor scaffold`). Later weeks are written
just-in-time by the tutor (`pygrid-tutor lesson-add`).

## Tests and quizzes
- **Tests:** in the workbench, `Ctrl/Cmd+Shift+Enter` runs pytest on the open file's
  folder, in the nearest workspace `uv` project (add pytest there: `uv add --dev pytest`).
  Pick an item under *verify* and a passing run records it, which lets you tick it.
- **Quizzes:** specs live in `curriculum/weekN/quiz_*.json`. Take them in the quiz view
  (keys `1–9`, `Enter`) or in the cockpit terminal with `pygrid-quiz W1.2.quiz`. Both
  grade server-side and write `progress/quizzes/<id>.json` plus a verification record.

## The tutor (Claude Code)
Open the cockpit's terminal (workbench ▸ shell) and run `claude` there. It starts in
`workspace/`, which loads the tutor rules (`workspace/CLAUDE.md`) and the commands
`/grill-me`, `/quiz`, `/verify` and `/checkoff`. They call `pygrid-tutor`, which the cockpit
terminal puts on PATH; every change to the tracker or `progress/` goes through it and
through the same gates as the app. Outside the cockpit, add `<pygrid>/bin` to your PATH.

Week 1 starts with a uv project in `workspace/` (`uv init --bare`, `uv add --dev pytest`).
Tests run in that project, so they don't depend on whichever `python3` is on PATH.

## Security
PYGRID runs learner code as **you**, with no sandbox. It binds to `127.0.0.1` only
(never `0.0.0.0`), rejects requests from other hosts and origins, and requires a
per-launch token (in the URL it opens) to use the API. Don't expose its port.
