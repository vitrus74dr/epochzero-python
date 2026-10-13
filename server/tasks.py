"""Where a task's work lives in workspace/.

Convention (also in workspace/CLAUDE.md): each task that has code gets one
folder, `workspace/weekN/tN.M-<slug>/`, e.g. `workspace/week1/t1.3-calculator/`.
The tutor creates it; tests run there; a [PROJECT]'s implementation_plan.md
and walkthrough.md sit in it.
"""

from __future__ import annotations

import re
from pathlib import Path

from server.paths import Paths

DOCS = {"plan": "implementation_plan.md", "walkthrough": "walkthrough.md"}
TASK_RE = re.compile(r"^(?:W)?(\d+)\.(\d+)$")


class FolderError(Exception):
    pass


def task_folder(paths: Paths, task_id: str) -> Path | None:
    """The folder for task "1.3", or None if there isn't one yet.
    Raises FolderError if more than one folder claims the task."""
    m = TASK_RE.match(task_id)
    if not m:
        raise FolderError(f"{task_id!r} is not a task id like 1.3")
    week, n = m.groups()
    week_dir = paths.workspace / f"week{week}"
    if not week_dir.is_dir():
        return None
    prefix = f"t{week}.{n}"
    found = sorted(d for d in week_dir.iterdir()
                   if d.is_dir() and (d.name == prefix or d.name.startswith(prefix + "-")))
    if len(found) > 1:
        names = ", ".join(d.name for d in found)
        raise FolderError(f"several folders claim task {week}.{n} in week{week}/: {names}")
    return found[0] if found else None


def task_docs(paths: Paths, task_id: str) -> dict:
    """Folder and plan/walkthrough paths (workspace-relative) for the UI;
    a doc is listed only if it exists."""
    try:
        folder = task_folder(paths, task_id)
    except FolderError:
        folder = None
    if folder is None:
        return {"folder": None, "plan": None, "walkthrough": None}
    rel = folder.relative_to(paths.workspace).as_posix()
    return {"folder": rel} | {
        k: f"{rel}/{name}" if (folder / name).is_file() else None for k, name in DOCS.items()}
