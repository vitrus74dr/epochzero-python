import re
from pathlib import Path

import pytest

from server import tracker as tr

REAL = Path(__file__).resolve().parent.parent / "CURRICULUM_TRACKER.md"

MINI = """# Title

## Rules
- not an item

## Week 1: One
Focus: basics.
Pitfalls monitored: `=` vs `==`.

### Task 1.1: First
- [ ] [W1.1.a] alpha
- [x] [W1.1.b] beta

### Task 1.2: Quiz it [QUIZ]
- [ ] [W1.2.a] gamma

## Week 2: Two

### Task 2.1: Build [PROJECT]
- [ ] [W2.1.a] delta

## Completion
- [ ] [W2.Z.a] certificate
"""


def test_real_tracker_round_trips_byte_identical():
    raw = REAL.read_bytes()
    assert tr.parse(raw.decode("utf-8")).serialize().encode("utf-8") == raw


def test_crlf_round_trips():
    text = MINI.replace("\n", "\r\n")
    t = tr.parse(text)
    assert t.serialize() == text
    assert t.item("W1.1.b").checked


def test_tick_then_untick_restores_bytes():
    t = tr.parse(MINI)
    t.set_checked("W1.1.a", True)
    ticked = t.serialize()
    assert "- [x] [W1.1.a] alpha" in ticked
    assert sum(a != b for a, b in zip(ticked, MINI)) == 1
    t.set_checked("W1.1.a", False)
    assert t.serialize() == MINI


def test_structure_of_real_tracker():
    t = tr.load(REAL)
    assert [w.n for w in t.weeks] == list(range(1, 9))
    assert t.weeks[0].title == "Foundations & Interactive CLI"
    assert t.weeks[0].focus.startswith("variables")
    assert "`=` vs `==`" in t.weeks[0].pitfalls
    kinds = {task.id: task.kind for w in t.weeks for task in w.tasks}
    assert kinds["1.2"] == "QUIZ" and kinds["1.3"] == "PROJECT" and kinds["1.1"] is None
    assert [i.id for i in t.completion] == ["W8.Z.a"]
    assert len(list(t.items())) == len({i.id for i in t.items()})


def test_parse_mini():
    t = tr.parse(MINI)
    assert [task.title for task in t.weeks[0].tasks] == ["First", "Quiz it"]
    assert t.weeks[1].tasks[0].kind == "PROJECT"
    assert t.item("W1.1.b").text == "beta"


def test_locking_and_current():
    t = tr.parse(MINI)
    assert t.week_unlocked(1) and not t.week_unlocked(2)
    assert not t.completion_unlocked()
    w, task, item = t.current()
    assert (w.n, task.id, item.id) == (1, "1.1", "W1.1.a")

    for i in ("W1.1.a", "W1.2.a"):
        t.set_checked(i, True)
    assert t.week_unlocked(2) and t.item_unlocked("W2.1.a")
    assert t.current()[2].id == "W2.1.a"

    t.set_checked("W2.1.a", True)
    assert t.completion_unlocked()
    assert t.current() == (None, None, t.completion[0])
    t.set_checked("W2.Z.a", True)
    assert t.current() is None


@pytest.mark.parametrize("bad,message", [
    (MINI.replace("[W1.2.a]", "[W1.1.a]"), "duplicate item ID"),
    (MINI.replace("- [ ] [W1.2.a] gamma", "- [ ] gamma"), "without a [WN.M.x] ID"),
    (MINI.replace("[W1.2.a]", "[W1.1.c]"), "is under Task 1.2"),
    (MINI.replace("### Task 2.1", "### Task 3.1"), "is under Week 2"),
    (MINI.replace("## Week 2: Two", "## Week 3: Two"), "week 3 follows week 1"),
], ids=["duplicate", "missing-id", "wrong-task", "wrong-week", "week-gap"])
def test_malformed_tracker_reports_line(bad, message):
    with pytest.raises(tr.TrackerError, match=re.escape(message)) as exc:
        tr.parse(bad)
    assert exc.value.line_no > 0


def test_write_atomic_leaves_no_temp_files(tmp_path):
    p = tmp_path / "CURRICULUM_TRACKER.md"
    tr.write_atomic(p, MINI)
    assert p.read_text(encoding="utf-8") == MINI
    assert [f.name for f in tmp_path.iterdir()] == ["CURRICULUM_TRACKER.md"]
