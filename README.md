# PYGRID

A local-first cockpit for an 8-week Python curriculum. Claude Code is the tutor in
your terminal; the browser app holds the tracker, lessons, editor, terminal and quizzes.

```sh
uv run pygrid
```

Requires `uv` and `pnpm`. The first run builds the web UI.

## Security
PYGRID runs learner code as **you**, with no sandbox. It binds to `127.0.0.1` only
(never `0.0.0.0`), rejects requests from other hosts and origins, and requires a
per-launch token (in the URL it opens) to use the API. Don't expose its port.
