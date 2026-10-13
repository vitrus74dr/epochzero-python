import asyncio
import shutil
import sys
from pathlib import Path

import pytest

from server import lessons, quizzes, tests_runner, tutor_cli
from server import tracker as tr
from server.paths import Paths

REPO = Path(__file__).resolve().parent.parent
CURRICULUM = REPO / "curriculum"


@pytest.fixture
def with_curriculum(paths) -> Paths:
    shutil.copytree(CURRICULUM, paths.curriculum)
    return paths


def test_week_lessons(client, with_curriculum):
    data = client.get("/api/lessons/1").json()
    assert data["week"] == 1 and data["unlocked"]
    by_task = {l["task"]: l for l in data["lessons"]}
    assert list(by_task) == ["1.1", "1.2", "1.3"]
    assert by_task["1.1"]["markdown"].startswith("# Environment & Hello World")
    assert by_task["1.1"]["has_stubs"] and not by_task["1.2"]["has_stubs"]
    assert by_task["1.2"]["kind"] == "QUIZ"


def test_later_weeks_have_no_lessons_yet(client, with_curriculum):
    data = client.get("/api/lessons/2").json()
    assert not data["unlocked"]
    assert all(l["markdown"] is None for l in data["lessons"])
    assert client.get("/api/lessons/99").status_code == 404


def test_scaffold_copies_without_overwriting(with_curriculum, capsys):
    paths = with_curriculum
    root = ["--root", str(paths.root)]
    assert tutor_cli.main([*root, "scaffold", "W1.3"]) == 0
    out = capsys.readouterr().out
    dest = paths.workspace / "week1/t1.3-calculator"
    assert "folder: week1/t1.3-calculator/" in out and "copied  test_calculator.py" in out
    (dest / "calculator.py").write_text("# learner's work\n")
    assert tutor_cli.main([*root, "scaffold", "W1.3"]) == 0
    assert "kept    calculator.py" in capsys.readouterr().out
    assert (dest / "calculator.py").read_text() == "# learner's work\n"


def test_scaffold_into_existing_task_folder(with_curriculum):
    paths = with_curriculum
    mine = paths.workspace / "week1/t1.3-calc"
    mine.mkdir(parents=True)
    dest, copied, _ = lessons.scaffold(paths, "1.3")
    assert dest == mine and "test_calculator.py" in copied


def test_scaffold_refusals(with_curriculum, capsys):
    root = ["--root", str(with_curriculum.root)]
    assert tutor_cli.main([*root, "scaffold", "W1.2"]) == 1
    assert "write the starter tests yourself" in capsys.readouterr().out
    assert tutor_cli.main([*root, "scaffold", "W2.3"]) == 1
    assert "locked" in capsys.readouterr().out


# ── the shipped Week 1 content ──

def test_week1_quiz_is_valid_and_graded():
    found, errors = quizzes.load_all(CURRICULUM)
    assert errors == []
    quiz = found["W1.2.quiz"]
    assert len(quiz.questions) == 5 and quiz.pass_mark == 4
    item = quizzes.item_for(quiz, tr.load(REPO / "CURRICULUM_TRACKER.md"))
    assert item is not None and item.id == "W1.2.b"


def test_every_week1_task_has_a_lesson():
    t = tr.load(REPO / "CURRICULUM_TRACKER.md")
    for task in t.weeks[0].tasks:
        assert lessons.lesson_path(Paths(REPO), task.id).is_file(), task.id


@pytest.mark.parametrize("task,count", [("1.1", 5), ("1.3", 15)])
def test_stub_tests_fail_cleanly_until_implemented(with_curriculum, monkeypatch, task, count):
    """Stubs are valid Python and the tests import them: every test fails
    (not errors) until the learner writes the code."""
    monkeypatch.setattr(tests_runner, "learner_python", lambda ws, start: [sys.executable])
    dest, _, _ = lessons.scaffold(with_curriculum, task)

    async def run():
        rel = dest.relative_to(with_curriculum.workspace).as_posix()
        return [e async for e in tests_runner.run_pytest(with_curriculum, rel, [])][-1]

    result = asyncio.run(run())
    assert result["counts"] == {"passed": 0, "failed": count, "error": 0, "skipped": 0}, result["summary"]


def test_lesson_add(paths, capsys):
    root = ["--root", str(paths.root)]
    draft = paths.workspace / ".pygrid" / "l.md"
    draft.parent.mkdir()
    draft.write_text("no heading\n")
    assert tutor_cli.main([*root, "lesson-add", "1.2", str(draft)]) == 1
    draft.write_text("# Control Flow\n\nBody")
    assert tutor_cli.main([*root, "lesson-add", "W1.2", str(draft)]) == 0
    assert "installed: curriculum/week1/lesson_1_2.md" in capsys.readouterr().out
    assert (paths.curriculum / "week1/lesson_1_2.md").read_text() == "# Control Flow\n\nBody\n"
    assert tutor_cli.main([*root, "lesson-add", "1.2", str(draft)]) == 0
    assert "replaced" in capsys.readouterr().out
    assert tutor_cli.main([*root, "lesson-add", "2.1", str(draft)]) == 1
    assert "locked" in capsys.readouterr().out
