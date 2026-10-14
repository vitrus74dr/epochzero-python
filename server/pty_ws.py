"""WebSocket <-> pty bridge (WS /api/pty) for the browser terminal.

Real pty, so `input()`, `inquirer`/`questionary` arrow-key prompts and `rich`
colour all behave exactly as in a desktop terminal.

Protocol
  client -> server  text  {"type": "input", "data": "..."}
                          {"type": "resize", "cols": 120, "rows": 30}
  server -> client  bytes raw pty output (xterm.js decodes UTF-8 across frames)
                    text  {"type": "started", "pid": 123, "argv": [...]}
                          {"type": "exit", "code": 0}
                          {"type": "error", "message": "..."}

The process runs as the user with cwd inside workspace/. It is NOT sandboxed.
ptyprocess on POSIX, pywinpty (ConPTY) on Windows: see server/terminal.py.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.compat import VENV_BIN, WINDOWS, default_shell
from server.fs import SandboxError, resolve_in
from server.paths import ROOT, Paths
from server.quizzes import QUIZ_ID_RE
from server.terminal import Terminal

MAX_PTYS = 8


class SpawnError(Exception):
    pass


def child_env() -> dict[str, str]:
    """The user's environment minus the app's own virtualenv, so `python`
    and `uv` in the terminal see the learner's setup, not the app's."""
    env = dict(os.environ)
    venv = env.pop("VIRTUAL_ENV", None)
    app_bins = {str(ROOT / ".venv" / VENV_BIN)} | ({str(Path(venv) / VENV_BIN)} if venv else set())
    env["PATH"] = os.pathsep.join(p for p in env.get("PATH", "").split(os.pathsep)
                                  if p not in app_bins)
    for k in ("PYTHONHOME", "PYTHONPATH", "UV_PROJECT_ENVIRONMENT"):
        env.pop(k, None)
    env.update(TERM="xterm-256color", COLORTERM="truecolor", EPOCHZERO="1")
    return env


def terminal_env(paths: Paths) -> dict[str, str]:
    """child_env() plus what `claude` running in this terminal needs: the
    epochzero-tutor/epochzero-quiz shims on PATH (bin/), the app dir, and the data
    root (tracker, progress/) this server is serving."""
    env = child_env()
    env["PATH"] = os.pathsep.join([str(ROOT / "bin"), env.get("PATH", "")])
    return env | {"EPOCHZERO_APP": str(ROOT), "EPOCHZERO_ROOT": str(paths.root)}


def command_for(paths: Paths, mode: str, file: str | None) -> tuple[list[str], Path]:
    """argv and cwd for a terminal session. `file` is a workspace path for
    mode "run" and a quiz id for mode "quiz"."""
    ws = paths.workspace.resolve()
    if mode == "shell":
        return default_shell(), ws
    if mode == "quiz":
        # The quiz runner is part of the app, so it runs on the app's Python.
        if not file or not QUIZ_ID_RE.match(file):
            raise SpawnError("quiz needs a quiz id like W1.2.quiz")
        return [sys.executable, "-m", "server.quiz_cli", file, "--root", str(paths.root)], ws
    if mode != "run":
        raise SpawnError(f"unknown mode {mode!r}")
    if not file:
        raise SpawnError("run needs a file")
    try:
        target = resolve_in(ws, file)
    except SandboxError as e:
        raise SpawnError(str(e)) from None
    if target.suffix != ".py" or not target.is_file():
        raise SpawnError(f"{file} is not a Python file in workspace/")
    return learner_python(ws, target.parent) + [target.name], target.parent


def learner_python(ws: Path, start: Path) -> list[str]:
    """argv prefix for the learner's Python. The nearest uv project between
    `start` and workspace/ (set up by the learner in W1.1.a) wins, so its
    dependencies (rich, inquirer, arcade, pytest...) are available."""
    path = child_env()["PATH"]
    uv = shutil.which("uv", path=path)
    for d in [start, *start.parents]:
        if uv and (d / "pyproject.toml").is_file():
            return [uv, "run", "--project", str(d), "python"]
        if d == ws:
            break
    python = "python" if WINDOWS else "python3"
    return [shutil.which(python, path=path) or python]


def router(paths: Paths) -> APIRouter:
    r = APIRouter()
    active: set[int] = set()

    @r.websocket("/api/pty")
    async def pty_socket(ws: WebSocket, mode: str = "shell", file: str | None = None,
                         cols: int = 80, rows: int = 24) -> None:
        await ws.accept()

        async def fail(message: str) -> None:
            await ws.send_text(json.dumps({"type": "error", "message": message}))
            await ws.close(code=1008)

        if len(active) >= MAX_PTYS:
            await fail(f"too many terminals open (max {MAX_PTYS})")
            return
        try:
            argv, cwd = command_for(paths, mode, file)
        except SpawnError as e:
            await fail(str(e))
            return

        paths.workspace.mkdir(exist_ok=True)
        try:
            term = Terminal(argv, cwd, terminal_env(paths), max(rows, 1), max(cols, 1))
        except Exception as e:
            await fail(f"could not start {argv[0]}: {e}")
            return

        active.add(term.pid)
        output: asyncio.Queue[bytes] = asyncio.Queue()
        term.start_reading(output)
        await ws.send_text(json.dumps({"type": "started", "pid": term.pid, "argv": argv}))

        async def pump_out() -> None:
            while data := await output.get():
                await ws.send_bytes(data)
            code = await asyncio.to_thread(term.exit_code)
            await ws.send_text(json.dumps({"type": "exit", "code": code}))

        async def pump_in() -> None:
            while True:
                msg = await ws.receive()
                if msg["type"] == "websocket.disconnect":
                    return
                if msg.get("bytes"):
                    term.write(msg["bytes"])
                    continue
                try:
                    m = json.loads(msg.get("text") or "")
                except ValueError:
                    continue
                if m.get("type") == "input" and isinstance(m.get("data"), str):
                    term.write(m["data"].encode("utf-8"))
                elif m.get("type") == "resize":
                    with contextlib.suppress(Exception):
                        term.resize(max(int(m["rows"]), 1), max(int(m["cols"]), 1))

        tasks = {asyncio.create_task(pump_out()), asyncio.create_task(pump_in())}
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in pending:
                t.cancel()
            for t in done:
                if (exc := t.exception()) and not isinstance(exc, (WebSocketDisconnect, OSError)):
                    raise exc
        finally:
            term.stop_reading()
            await asyncio.to_thread(term.stop)
            term.close()
            active.discard(term.pid)
            with contextlib.suppress(Exception):
                await ws.close()

    return r
