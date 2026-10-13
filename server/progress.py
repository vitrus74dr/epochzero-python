"""Which tracker items the learner has ticked: progress/checked.json.

CURRICULUM_TRACKER.md is the curriculum (weeks, tasks, item IDs and wording)
and is never written by the app. Ticks live here instead, so a student can
`git pull` course updates without conflicts with their own progress.
progress/ is git-ignored.

    {"checked": ["W1.1.a", "W1.1.b"]}

Every reader goes through load_state(); every tick goes through
tracker_api.check_item(), which writes this file under the tracker lock.
"""

from __future__ import annotations

import json

from server import tracker as tr
from server.paths import Paths


class ProgressError(ValueError):
    """progress/checked.json exists but can't be read. Never silently treated
    as "nothing ticked": the next tick would overwrite the learner's progress."""


def read_checked(paths: Paths) -> set[str] | None:
    """The ticked IDs, or None if there's no progress file yet."""
    try:
        text = paths.checked.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    try:
        data = json.loads(text)
        ids = data["checked"]
        if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
            raise TypeError
    except (ValueError, KeyError, TypeError):
        raise ProgressError(f"{paths.checked} is not valid progress JSON; fix or remove it") from None
    return set(ids)


def write_checked(paths: Paths, ids: set[str]) -> None:
    paths.checked.parent.mkdir(parents=True, exist_ok=True)
    tr.write_atomic(paths.checked, json.dumps({"checked": sorted(ids)}, indent=2) + "\n")


def load_state(paths: Paths) -> tr.Tracker:
    """The tracker with the learner's ticks applied (and nothing else).

    With no progress file yet, `[x]` marks in the tracker text are taken as
    the starting state: a one-time import from the pre-progress-file layout.
    """
    t = tr.load(paths.tracker)
    ids = read_checked(paths)
    if ids is None:
        return t
    known = {i.id for i in t.items()}
    for item in t.items():
        item.checked = item.id in ids & known
    return t
