"""Pytest runner (POST /api/tests/run) and the verification it can record.

pytest runs as a subprocess in the learner's environment (see
pty_ws.learner_python), never inside the app. Its output streams back as
NDJSON while it runs; the pass/fail summary comes from a JUnit XML report,
not from scraping the console.

Protocol (one JSON object per line):
    {"type": "start", "argv": [...], "cwd": "week1/calc", "items": ["W1.3.c"]}
    {"type": "output", "data": "..."}
    {"type": "result", "passed": true, "summary": "6 passed", "counts": {...},
     "tests": [...], "exit_code": 0, "records": [...], "error": null}

A run that names items appends a verification record for each, pass or fail.
Only a run with at least one passing test and no failures or errors passes.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from server import progress
from server import tracker as tr
from server.compat import kill_tree, new_group_kwargs
from server.fs import SandboxError, resolve_in
from server.paths import Paths
from server.pty_ws import child_env, learner_python
from server.verifications import Record, VerificationLog, verify_kind

TIMEOUT_SECONDS = 300
MAX_DETAIL = 4000
OUTCOMES = ("passed", "failed", "error", "skipped")
NO_PYTEST = ("pytest isn't installed in the learner's environment. "
             "In the workspace project, run: uv add --dev pytest")


class RunRefused(Exception):
    pass


def parse_junit(xml_text: str) -> list[dict]:
    """Testcases from a pytest JUnit XML report, in report order."""
    root = ET.fromstring(xml_text)
    tests = []
    for case in root.iter("testcase"):
        outcome, message, detail = "passed", "", ""
        for tag in ("failure", "error", "skipped"):
            el = case.find(tag)
            if el is not None:
                outcome = "failed" if tag == "failure" else tag
                message = el.get("message", "")
                detail = (el.text or "")[-MAX_DETAIL:]
                break
        classname, name = case.get("classname", ""), case.get("name", "")
        tests.append({
            "id": f"{classname}::{name}" if classname else name,
            "name": name,
            "classname": classname,
            "outcome": outcome,
            "message": message,
            "detail": detail,
            "time": float(case.get("time") or 0),
        })
    return tests


def summarize(tests: list[dict], exit_code: int | None) -> tuple[bool, str, dict]:
    counts = {k: sum(t["outcome"] == k for t in tests) for k in OUTCOMES}
    parts = [f"{counts[k]} {k if k != 'error' else 'errors'}" for k in OUTCOMES if counts[k]]
    if exit_code == 5 or not tests:
        summary = "no tests collected"
    elif exit_code not in (0, 1) and not counts["error"]:
        summary = ", ".join(parts + [f"pytest exited {exit_code}"])
    else:
        summary = ", ".join(parts)
    passed = (exit_code == 0 and counts["passed"] > 0
              and counts["failed"] == 0 and counts["error"] == 0)
    return passed, summary, counts


def check_item_for_pytest(paths: Paths, item_id: str) -> None:
    """A pytest run may only record against an existing, unlocked pytest item."""
    t = progress.load_state(paths)
    try:
        item = t.item(item_id)
    except KeyError:
        raise RunRefused(f"no item {item_id} in the tracker") from None
    if (kind := verify_kind(item.text)) != "pytest":
        raise RunRefused(f"{item_id} is verified by {kind}, not by a pytest run")
    if not t.item_unlocked(item_id):
        raise RunRefused(f"{item_id} is in a locked week")


def pytest_argv(paths: Paths, target: Path, report: Path) -> tuple[list[str], Path]:
    ws = paths.workspace.resolve()
    cwd = target if target.is_dir() else target.parent
    argv = learner_python(ws, cwd) + [
        "-m", "pytest", "-q", "--color=no", "-p", "no:cacheprovider",
        f"--junitxml={report}", "-o", "junit_family=xunit2",
        target.name if target != cwd else ".",
    ]
    return argv, cwd


async def run_pytest(paths: Paths, rel: str, items: list[str],
                     by: str = "app") -> AsyncIterator[dict]:
    ws = paths.workspace.resolve()
    target = resolve_in(ws, rel)
    with tempfile.TemporaryDirectory(prefix="epochzero-junit-") as tmp:
        report = Path(tmp) / "report.xml"
        argv, cwd = pytest_argv(paths, target, report)
        yield {"type": "start", "argv": argv, "cwd": cwd.relative_to(ws).as_posix() or ".",
               "items": items}

        env = child_env() | {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"}
        env.pop("COLORTERM", None)
        env["TERM"] = "dumb"
        proc = await asyncio.create_subprocess_exec(
            *argv, cwd=cwd, env=env, stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            **new_group_kwargs())
        error = None
        output_tail = ""
        try:
            async with asyncio.timeout(TIMEOUT_SECONDS):
                assert proc.stdout is not None
                while chunk := await proc.stdout.read(4096):
                    text = chunk.decode("utf-8", errors="replace")
                    output_tail = (output_tail + text)[-2000:]
                    yield {"type": "output", "data": text}
                await proc.wait()
        except TimeoutError:
            error = f"timed out after {TIMEOUT_SECONDS}s"
        finally:
            if proc.returncode is None:
                kill_tree(proc.pid)
                await proc.wait()

        tests: list[dict] = []
        if report.is_file():
            try:
                tests = parse_junit(report.read_text(encoding="utf-8"))
            except ET.ParseError as e:
                error = error or f"could not read the JUnit report: {e}"
        elif error is None:
            error = NO_PYTEST if "No module named pytest" in output_tail else \
                "pytest produced no report"

    exit_code = proc.returncode
    passed, summary, counts = summarize(tests, exit_code)
    if error:
        passed, summary = False, error
    log = VerificationLog(paths.verifications)
    records = [log.append(Record(item=i, kind="pytest", passed=passed, summary=summary, by=by))
               .model_dump() for i in items]
    yield {"type": "result", "passed": passed, "summary": summary, "counts": counts,
           "tests": tests, "exit_code": exit_code, "records": records, "error": error}


class RunRequest(BaseModel):
    path: str
    item: str | None = None


def router(paths: Paths) -> APIRouter:
    r = APIRouter(prefix="/api/tests")
    busy = asyncio.Lock()

    @r.post("/run")
    async def run(body: RunRequest):
        try:
            target = resolve_in(paths.workspace, body.path)
        except SandboxError as e:
            raise HTTPException(403, str(e)) from None
        if not target.exists():
            raise HTTPException(404, f"{body.path} not found")
        if target.is_file() and target.suffix != ".py":
            raise HTTPException(422, f"{body.path} is not a Python file or folder")
        if body.item:
            try:
                check_item_for_pytest(paths, body.item)
            except tr.TrackerError as e:
                raise HTTPException(422, str(e)) from None
            except RunRefused as e:
                raise HTTPException(409, str(e)) from None
        if busy.locked():
            raise HTTPException(409, "a test run is already in progress")

        async def stream() -> AsyncIterator[str]:
            # Acquired inside the stream so a request dropped before streaming
            # starts can't leave the lock held. Disconnecting mid-run kills
            # pytest (run_pytest's finally) and records nothing.
            async with busy:
                async for event in run_pytest(paths, body.path, [body.item] if body.item else []):
                    yield json.dumps(event) + "\n"

        return StreamingResponse(stream(), media_type="application/x-ndjson",
                                 headers={"Cache-Control": "no-store"})

    return r
