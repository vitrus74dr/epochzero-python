"""File watching -> in-process event hub -> SSE (GET /api/events).

Pushes a small JSON event whenever the tracker, the verification log, quiz
results, curriculum files (lessons, quiz specs) or workspace files change, so edits made by Claude Code in the
terminal show up in the browser without a refresh.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path

from watchfiles import awatch

KEEPALIVE_SECONDS = 15


class EventHub:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict]] = set()

    def publish(self, event: dict) -> None:
        for q in self._subscribers:
            q.put_nowait(event)

    async def stream(self) -> AsyncIterator[str]:
        """SSE-formatted events for one client, with keepalive comments."""
        q: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.add(q)
        try:
            yield "retry: 1000\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), KEEPALIVE_SECONDS)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            self._subscribers.discard(q)


def classify(path: Path, root: Path) -> str | None:
    """Map a changed path to an event type, or None to ignore it."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if any(p.startswith(".") or p == "__pycache__" for p in parts):
        return None  # lock files, temp files from atomic writes, caches
    if rel == Path("CURRICULUM_TRACKER.md"):
        return "tracker"
    if parts[0] == "progress":
        if parts[1:] == ("verifications.jsonl",):
            return "verifications"
        if len(parts) > 1 and parts[1] == "quizzes":
            return "quizzes"
        return None
    if parts[0] == "workspace":
        return "workspace"
    if parts[0] == "curriculum":
        return "curriculum"
    return None


async def watch_root(root: Path, hub: EventHub, stop: asyncio.Event) -> None:
    """Watch the repo root (non-recursive, for the tracker) plus progress/,
    workspace/ and curriculum/ recursively. Not the whole repo: node_modules and .venv
    would cost thousands of inotify watches."""
    (root / "progress").mkdir(exist_ok=True)
    (root / "workspace").mkdir(exist_ok=True)
    (root / "curriculum").mkdir(exist_ok=True)

    async def run(paths: list[Path], recursive: bool) -> None:
        async for changes in awatch(*paths, recursive=recursive, stop_event=stop,
                                    debounce=100, step=50):
            kinds: dict[str, set[str]] = {}
            for _, p in changes:
                path = Path(p)
                if (kind := classify(path, root)) is not None:
                    kinds.setdefault(kind, set()).add(path.relative_to(root).as_posix())
            for kind, paths_changed in sorted(kinds.items()):
                hub.publish({"type": kind, "paths": sorted(paths_changed)})

    await asyncio.gather(
        run([root], recursive=False),
        run([root / "progress", root / "workspace", root / "curriculum"], recursive=True),
    )
