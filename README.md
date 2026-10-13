# PYGRID

A local-first cockpit for an 8-week Python curriculum. Claude Code is the tutor in
your terminal; the browser app holds the tracker, lessons, editor, terminal and quizzes.

```sh
uv run pygrid
```

Requires `uv` and `pnpm`. The first run builds the web UI.

## Tests and quizzes
- **Tests:** in the workbench, `Ctrl/Cmd+Shift+Enter` runs pytest on the open file's
  folder, in the nearest workspace `uv` project (add pytest there: `uv add --dev pytest`).
  Pick an item under *verify* and a passing run records it, which lets you tick it.
- **Quizzes:** specs live in `curriculum/weekN/quiz_*.json`. Take them in the quiz view
  (keys `1–9`, `Enter`) or in a terminal with `uv run pygrid-quiz W1.2.quiz`. Both
  grade server-side and write `progress/quizzes/<id>.json` plus a verification record.

## Security
PYGRID runs learner code as **you**, with no sandbox. It binds to `127.0.0.1` only
(never `0.0.0.0`), rejects requests from other hosts and origins, and requires a
per-launch token (in the URL it opens) to use the API. Don't expose its port.
