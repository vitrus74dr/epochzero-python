import json
import os
import time

import pytest
from starlette.websockets import WebSocketDisconnect

from conftest import HOST, ORIGIN


def connect(client, **params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    return client.websocket_connect(f"ws://{HOST}/api/pty?{q}", headers={"Origin": ORIGIN})


def read_until(ws, needle: str, limit: int = 200) -> tuple[str, list[dict]]:
    """Collect output until needle appears; return (text, control messages)."""
    out, controls = b"", []
    for _ in range(limit):
        msg = ws.receive()
        if msg.get("bytes"):
            out += msg["bytes"]
        elif msg.get("text"):
            controls.append(json.loads(msg["text"]))
            if controls[-1]["type"] in ("exit", "error") and needle not in out.decode(errors="replace"):
                break
        if needle in out.decode(errors="replace"):
            break
    return out.decode(errors="replace"), controls


def script(paths, name, body):
    p = paths.workspace / name
    p.write_text(body, encoding="utf-8")
    return name


def test_input_round_trip(client, paths):
    script(paths, "greet.py", 'name = input("name? ")\nprint(f"hello {name}")\n')
    with connect(client, mode="run", file="greet.py") as ws:
        started = json.loads(ws.receive_text())
        assert started["type"] == "started" and started["argv"][-1] == "greet.py"
        text, _ = read_until(ws, "name? ")
        assert "name? " in text
        ws.send_text(json.dumps({"type": "input", "data": "Ada\r"}))
        text, controls = read_until(ws, "hello Ada")
        assert "hello Ada" in text
        for _ in range(100):
            if any(c["type"] == "exit" for c in controls):
                break
            msg = ws.receive()
            if msg.get("text"):
                controls.append(json.loads(msg["text"]))
        assert [c for c in controls if c["type"] == "exit"][0]["code"] == 0


def test_is_a_real_tty_and_resize_applies(client, paths):
    script(paths, "size.py",
           "import os, sys\nprint('tty', sys.stdin.isatty())\ninput()\n"
           "s = os.get_terminal_size()\nprint(f'size {s.columns}x{s.lines}')\n")
    with connect(client, mode="run", file="size.py", cols=80, rows=24) as ws:
        text, _ = read_until(ws, "tty True")
        assert "tty True" in text
        ws.send_text(json.dumps({"type": "resize", "cols": 132, "rows": 40}))
        ws.send_text(json.dumps({"type": "input", "data": "\r"}))
        text, _ = read_until(ws, "size 132x40")
        assert "size 132x40" in text


def test_run_rejects_paths_outside_workspace(client):
    with connect(client, mode="run", file="../CURRICULUM_TRACKER.md") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        with pytest.raises(WebSocketDisconnect):
            ws.receive_text()


def test_run_rejects_non_python(client, paths):
    script(paths, "notes.txt", "hi")
    with connect(client, mode="run", file="notes.txt") as ws:
        assert json.loads(ws.receive_text())["type"] == "error"


def test_disconnect_kills_process(client, paths):
    script(paths, "sleepy.py", "import time\nprint('ready', flush=True)\ntime.sleep(60)\n")
    with connect(client, mode="run", file="sleepy.py") as ws:
        pid = json.loads(ws.receive_text())["pid"]
        read_until(ws, "ready")
    for _ in range(50):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        # A zombie still answers kill(0); check its state.
        try:
            with open(f"/proc/{pid}/stat") as fh:
                if fh.read().split()[2] == "Z":
                    break
        except FileNotFoundError:
            break
        time.sleep(0.1)
    else:
        pytest.fail(f"process {pid} survived the disconnect")


def test_pty_requires_session(paths):
    from fastapi.testclient import TestClient
    from server.main import create_app
    c = TestClient(create_app(token="t", root=paths.root, dist=paths.root / "x", watch=False),
                   base_url=f"http://{HOST}")
    with pytest.raises(WebSocketDisconnect):
        with c.websocket_connect(f"ws://{HOST}/api/pty?mode=shell", headers={"Origin": ORIGIN}):
            pass


def test_child_env_drops_app_venv(monkeypatch):
    from server.paths import ROOT
    from server.pty_ws import child_env
    venv_bin = str(ROOT / ".venv" / "bin")
    monkeypatch.setenv("VIRTUAL_ENV", str(ROOT / ".venv"))
    monkeypatch.setenv("PATH", f"{venv_bin}:/usr/bin")
    env = child_env()
    assert "VIRTUAL_ENV" not in env
    assert env["PATH"] == "/usr/bin"
    assert env["TERM"] == "xterm-256color"


def test_quiz_in_terminal_with_arrow_keys(client, paths, quiz):
    from server.verifications import VerificationLog
    DOWN, ENTER = "\x1b[B", "\r"

    def send(data):
        ws.send_text(json.dumps({"type": "input", "data": data}))

    def until(needle):
        # Play terminal: blessed (under inquirer) asks for the cursor position
        # and waits for the reply, which xterm.js sends automatically.
        out = ""
        for _ in range(200):
            msg = ws.receive()
            chunk = (msg.get("bytes") or b"").decode(errors="replace")
            for _ in range(chunk.count("\x1b[6n")):
                send("\x1b[1;1R")
            out += chunk
            if needle in out:
                return out
        raise AssertionError(out)

    with connect(client, mode="quiz", file="W1.2.quiz", cols=100, rows=30) as ws:
        until("> True")
        # q1: first choice is right. q2: one down. q3: one down.
        send(ENTER)
        until("  []")  # only q2 has this choice
        send(DOWN + ENTER)
        until("  'x'")  # only q3
        send(DOWN + ENTER)
        assert "[ PASS ]" in until("recorded for W1.2.b")
    [rec] = VerificationLog(paths.verifications).read()
    assert (rec.item, rec.kind, rec.passed, rec.by) == ("W1.2.b", "quiz", True, "cli")
    assert rec.summary == "3/3 (pass 2)"


def test_quiz_mode_rejects_bad_id(client):
    with connect(client, mode="quiz", file="../../etc") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error" and "quiz id" in msg["message"]


def test_terminal_knows_app_and_data_roots(client, paths):
    from server.paths import ROOT
    script(paths, "env.py", 'import os\nprint("APP=" + os.environ["PYGRID_APP"])\n'
                            'print("DATA=" + os.environ["PYGRID_ROOT"])\n')
    with connect(client, mode="run", file="env.py") as ws:
        out, _ = read_until(ws, "DATA=")
        read_more, _ = read_until(ws, "\n")
    out += read_more
    assert f"APP={ROOT}" in out and f"DATA={paths.root}" in out
