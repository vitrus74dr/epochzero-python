"""Parse and edit CURRICULUM_TRACKER.md.

Grammar (HANDOFF.md §5):
    ## Week N: Title                     -> week
    ### Task N.M: Title [PROJECT|QUIZ]?  -> task
    - [ ] [WN.M.x] text                  -> checkable item

The parser keeps the raw lines and edits a checkbox by flipping the single
character between the brackets, so serialize() is byte-identical to the input
except for the boxes that were deliberately changed. Anything it doesn't
recognise (rules, focus lines, blank lines) is preserved untouched.
"""

from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from server.compat import lock_exclusive, unlock

WEEK_RE = re.compile(r"^## Week (\d+): (.+?)\s*$")
SECTION_RE = re.compile(r"^## (.+?)\s*$")
TASK_RE = re.compile(r"^### Task (\d+)\.(\d+): (.+?)(?: \[(PROJECT|QUIZ)\])?\s*$")
ITEM_RE = re.compile(r"^- \[([ xX])\] \[(W(\d+)\.(\d+|Z)\.[a-z]+)\] (.+?)\s*$")
CHECKBOX_COL = 3  # "- [x]" -> index of the x


class TrackerError(ValueError):
    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"CURRICULUM_TRACKER.md line {line_no}: {message}")
        self.line_no = line_no


@dataclass
class Item:
    id: str
    text: str
    checked: bool
    line: int  # 0-based index into Tracker.lines


@dataclass
class Task:
    id: str  # "1.2"
    title: str
    kind: str | None  # "PROJECT" | "QUIZ" | None
    items: list[Item] = field(default_factory=list)


@dataclass
class Week:
    n: int
    title: str
    focus: str = ""
    pitfalls: str = ""
    tasks: list[Task] = field(default_factory=list)

    @property
    def items(self) -> list[Item]:
        return [i for t in self.tasks for i in t.items]

    @property
    def complete(self) -> bool:
        return all(i.checked for i in self.items)


@dataclass
class Tracker:
    lines: list[str]
    weeks: list[Week]
    completion: list[Item]  # items under "## Completion"

    def items(self) -> Iterator[Item]:
        for w in self.weeks:
            yield from w.items
        yield from self.completion

    def item(self, item_id: str) -> Item:
        for i in self.items():
            if i.id == item_id:
                return i
        raise KeyError(item_id)

    def week_of(self, item_id: str) -> Week | None:
        """The week an item belongs to; None for completion items."""
        for w in self.weeks:
            if any(i.id == item_id for i in w.items):
                return w
        return None

    def week_unlocked(self, n: int) -> bool:
        """Week 1 is always open; week N opens when week N-1 is fully ticked."""
        prev = [w for w in self.weeks if w.n < n]
        return all(w.complete for w in prev)

    def completion_unlocked(self) -> bool:
        return all(w.complete for w in self.weeks)

    def item_unlocked(self, item_id: str) -> bool:
        week = self.week_of(item_id)
        if week is None:
            return self.completion_unlocked()
        return self.week_unlocked(week.n)

    def current(self) -> tuple[Week | None, Task | None, Item] | None:
        """First unticked item in the lowest unlocked week."""
        for w in self.weeks:
            for t in w.tasks:
                for i in t.items:
                    if not i.checked:
                        return w, t, i
        for i in self.completion:
            if not i.checked:
                return None, None, i
        return None

    def set_checked(self, item_id: str, checked: bool) -> None:
        item = self.item(item_id)
        line = self.lines[item.line]
        mark = "x" if checked else " "
        self.lines[item.line] = line[:CHECKBOX_COL] + mark + line[CHECKBOX_COL + 1:]
        item.checked = checked

    def serialize(self) -> str:
        return "".join(self.lines)


def parse(text: str) -> Tracker:
    lines = text.splitlines(keepends=True)
    weeks: list[Week] = []
    completion: list[Item] = []
    week: Week | None = None
    task: Task | None = None
    section: str | None = None  # non-week "## " heading, e.g. "Completion"
    seen: set[str] = set()

    for idx, raw in enumerate(lines):
        line = raw.rstrip("\r\n")
        line_no = idx + 1

        if m := WEEK_RE.match(line):
            week = Week(n=int(m.group(1)), title=m.group(2))
            if weeks and week.n != weeks[-1].n + 1:
                raise TrackerError(line_no, f"week {week.n} follows week {weeks[-1].n}")
            weeks.append(week)
            task, section = None, None
        elif m := SECTION_RE.match(line):
            week, task, section = None, None, m.group(1)
        elif m := TASK_RE.match(line):
            if week is None:
                raise TrackerError(line_no, "task outside a week")
            if int(m.group(1)) != week.n:
                raise TrackerError(line_no, f"Task {m.group(1)}.{m.group(2)} is under Week {week.n}")
            task = Task(id=f"{m.group(1)}.{m.group(2)}", title=m.group(3), kind=m.group(4))
            week.tasks.append(task)
        elif m := ITEM_RE.match(line):
            checked, item_id, w_n, t_n, item_text = m.groups()
            if item_id in seen:
                raise TrackerError(line_no, f"duplicate item ID {item_id}")
            seen.add(item_id)
            item = Item(id=item_id, text=item_text, checked=checked != " ", line=idx)
            if week is not None:
                if task is None:
                    raise TrackerError(line_no, f"{item_id} is not under a task")
                if f"{w_n}.{t_n}" != task.id:
                    raise TrackerError(line_no, f"{item_id} is under Task {task.id}")
                task.items.append(item)
            elif section == "Completion":
                completion.append(item)
            else:
                raise TrackerError(line_no, f"{item_id} is outside any week or Completion")
        elif line.startswith("- [") and week is not None:
            # Looks like an item but doesn't match the grammar: almost always a
            # hand edit that dropped the ID. Fail loudly rather than hide it.
            raise TrackerError(line_no, "checkbox line without a [WN.M.x] ID")
        elif week is not None and task is None:
            if line.startswith("Focus:"):
                week.focus = line.removeprefix("Focus:").strip()
            elif line.startswith("Pitfalls monitored:"):
                week.pitfalls = line.removeprefix("Pitfalls monitored:").strip()

    return Tracker(lines=lines, weeks=weeks, completion=completion)


def load(path: Path) -> Tracker:
    return parse(path.read_text(encoding="utf-8"))


@contextmanager
def locked(lock_path: Path) -> Iterator[None]:
    """Exclusive advisory lock serializing tracker read-modify-write cycles."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as fh:
        lock_exclusive(fh)
        try:
            yield
        finally:
            unlock(fh)


def write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        # mkstemp creates 0600; keep the existing file's mode, or use the umask default.
        try:
            mode = path.stat().st_mode & 0o7777
        except FileNotFoundError:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise
