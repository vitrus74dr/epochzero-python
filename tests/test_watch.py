import asyncio
import json
from pathlib import Path

import pytest

from server.watch import EventHub, classify, watch_root


@pytest.mark.parametrize("rel,kind", [
    ("CURRICULUM_TRACKER.md", "tracker"),
    ("progress/verifications.jsonl", "verifications"),
    ("progress/quizzes/W1.2.quiz.json", "quizzes"),
    ("workspace/week1/calc.py", "workspace"),
    ("curriculum/week1/quiz_1_2.json", "curriculum"),
    ("progress/.tracker.lock", None),
    (".CURRICULUM_TRACKER.md.abc.tmp", None),
    ("workspace/week1/__pycache__/calc.cpython-312.pyc", None),
    ("web/src/App.tsx", None),
])
def test_classify(rel, kind):
    root = Path("/r")
    assert classify(root / rel, root) == kind


async def next_event(q: asyncio.Queue, kind: str, timeout: float = 3.0) -> dict:
    async def wait():
        while True:
            e = await q.get()
            if e["type"] == kind:
                return e
    return await asyncio.wait_for(wait(), timeout)


def test_file_changes_reach_subscribers(tmp_path):
    async def scenario():
        hub = EventHub()
        q: asyncio.Queue = asyncio.Queue()
        hub._subscribers.add(q)
        stop = asyncio.Event()
        task = asyncio.create_task(watch_root(tmp_path, hub, stop))
        await asyncio.sleep(0.4)  # let inotify watches register

        (tmp_path / "CURRICULUM_TRACKER.md").write_text("x", encoding="utf-8")
        assert (await next_event(q, "tracker"))["paths"] == ["CURRICULUM_TRACKER.md"]

        (tmp_path / "progress" / "verifications.jsonl").write_text("{}\n", encoding="utf-8")
        await next_event(q, "verifications")

        (tmp_path / "workspace" / "week1").mkdir()
        (tmp_path / "workspace" / "week1" / "a.py").write_text("print(1)\n", encoding="utf-8")
        e = await next_event(q, "workspace")
        assert any(p.startswith("workspace/week1") for p in e["paths"])

        stop.set()
        await asyncio.wait_for(task, 3)

    asyncio.run(scenario())


def test_stream_formats_sse():
    async def scenario():
        hub = EventHub()
        gen = hub.stream()
        assert await gen.__anext__() == "retry: 1000\n\n"
        nxt = asyncio.ensure_future(gen.__anext__())
        await asyncio.sleep(0)
        hub.publish({"type": "tracker", "paths": []})
        chunk = await asyncio.wait_for(nxt, 1)
        assert chunk.startswith("data: ")
        assert json.loads(chunk[6:]) == {"type": "tracker", "paths": []}
        await gen.aclose()
        assert hub._subscribers == set()

    asyncio.run(scenario())
