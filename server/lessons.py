"""Lessons (GET /api/lessons/{week}) and task scaffolds.

One markdown lesson per task: curriculum/weekN/lesson_N_M.md. Week 1 ships
with the app; later weeks are authored just-in-time by the tutor, so a task
without a lesson file is normal, not an error.

Scaffolds: curriculum/weekN/stubs/tN.M-<slug>/ holds starter files (tests
first, plus signature-only stubs) that `pygrid-tutor scaffold` copies into the
learner's task folder. The tutor session can't read curriculum/ itself.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException

from server import tracker as tr
from server.paths import Paths
from server.tasks import task_folder


def lesson_path(paths: Paths, task_id: str) -> Path:
    week, n = task_id.split(".")
    return paths.curriculum / f"week{week}" / f"lesson_{week}_{n}.md"


def stub_dir(paths: Paths, task_id: str) -> Path | None:
    week, n = task_id.split(".")
    base = paths.curriculum / f"week{week}" / "stubs"
    found = sorted(base.glob(f"t{week}.{n}-*")) if base.is_dir() else []
    return found[0] if found else None


def scaffold(paths: Paths, task_id: str) -> tuple[Path, list[str], list[str]]:
    """Copy a task's stubs into its workspace folder (created from the stub's
    name if there isn't one yet). Never overwrites: existing files are the
    learner's. Returns (folder, copied, skipped) with folder-relative names."""
    src = stub_dir(paths, task_id)
    if src is None:
        raise FileNotFoundError(f"no stubs for task {task_id}")
    dest = task_folder(paths, task_id) or (paths.workspace / f"week{task_id.split('.')[0]}" / src.name)
    copied, skipped = [], []
    for f in sorted(p for p in src.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        rel = f.relative_to(src)
        target = dest / rel
        if target.exists():
            skipped.append(rel.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)
        copied.append(rel.as_posix())
    return dest, copied, skipped


def router(paths: Paths) -> APIRouter:
    r = APIRouter(prefix="/api/lessons")

    @r.get("/{week}")
    def week_lessons(week: int):
        try:
            t = tr.load(paths.tracker)
        except tr.TrackerError as e:
            raise HTTPException(422, str(e)) from None
        w = next((w for w in t.weeks if w.n == week), None)
        if w is None:
            raise HTTPException(404, f"no week {week}")
        lessons = []
        for task in w.tasks:
            p = lesson_path(paths, task.id)
            try:
                markdown = p.read_text(encoding="utf-8")
            except FileNotFoundError:
                markdown = None
            lessons.append({"task": task.id, "title": task.title, "kind": task.kind,
                            "markdown": markdown,
                            "has_stubs": stub_dir(paths, task.id) is not None})
        return {"week": w.n, "title": w.title, "unlocked": t.week_unlocked(w.n),
                "lessons": lessons}

    return r
