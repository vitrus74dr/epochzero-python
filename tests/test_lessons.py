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


def test_missing_lessons_are_null(client):
    """No curriculum/ at all: every task is listed, with markdown null."""
    data = client.get("/api/lessons/2").json()
    assert not data["unlocked"]
    assert data["lessons"] and all(l["markdown"] is None for l in data["lessons"])
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
    assert (dest / "calculator.py").read_text(encoding="utf-8") == "# learner's work\n"


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


# ── the shipped curriculum ──

TRACKER = tr.load(REPO / "CURRICULUM_TRACKER.md")
WEEKS_WITH_CONTENT = sorted(int(d.name[4:]) for d in CURRICULUM.glob("week*") if d.is_dir())
STUB_DIRS = sorted(CURRICULUM.glob("week*/stubs/t*"))


def test_quizzes_are_valid():
    found, errors = quizzes.load_all(CURRICULUM)
    assert errors == []
    for quiz in found.values():
        item = quizzes.item_for(quiz, TRACKER)
        assert item is not None, f"{quiz.id} verifies nothing"
        assert len(quiz.questions) == 5 and quiz.pass_mark == 4, quiz.id


@pytest.mark.parametrize("week", WEEKS_WITH_CONTENT)
def test_every_task_has_a_lesson_and_quiz(week):
    found, _ = quizzes.load_all(CURRICULUM)
    w = next(w for w in TRACKER.weeks if w.n == week)
    for task in w.tasks:
        assert lessons.lesson_path(Paths(REPO), task.id).is_file(), f"lesson for {task.id}"
        if any(i.text.startswith("Quiz:") for i in task.items):
            assert f"W{task.id}.quiz" in found, f"quiz for {task.id}"


def third_party_imports(folder: Path) -> set[str]:
    import ast
    local = {p.stem for p in folder.glob("*.py")}
    names = set()
    for f in folder.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names.add(node.module.split(".")[0])
    return {n for n in names - local if n not in sys.stdlib_module_names and n != "pytest"}


@pytest.mark.parametrize("stub", STUB_DIRS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_stub_tests_fail_cleanly_until_implemented(paths, monkeypatch, stub):
    """Stubs are valid Python and the tests import them: every test fails
    (not errors) until the learner writes the code."""
    import importlib.util
    missing = [m for m in third_party_imports(stub) if importlib.util.find_spec(m) is None]
    if missing:
        pytest.skip(f"needs {', '.join(sorted(missing))} (checked in the learner env instead)")
    shutil.copytree(CURRICULUM, paths.curriculum)
    monkeypatch.setattr(tests_runner, "learner_python", lambda ws, start: [sys.executable])
    task = stub.name[1:].split("-")[0]
    dest, _, _ = lessons.scaffold(paths, task)

    async def run():
        rel = dest.relative_to(paths.workspace).as_posix()
        return [e async for e in tests_runner.run_pytest(paths, rel, [])][-1]

    result = asyncio.run(run())
    c = result["counts"]
    assert c["failed"] > 0 and c["passed"] == 0 and c["error"] == 0, result["summary"]


def test_lesson_add(paths, capsys):
    root = ["--root", str(paths.root)]
    draft = paths.workspace / ".epochzero" / "l.md"
    draft.parent.mkdir()
    draft.write_text("no heading\n")
    assert tutor_cli.main([*root, "lesson-add", "1.2", str(draft)]) == 1
    draft.write_text("# Control Flow\n\nBody")
    assert tutor_cli.main([*root, "lesson-add", "W1.2", str(draft)]) == 0
    assert "installed: curriculum/week1/lesson_1_2.md" in capsys.readouterr().out
    assert (paths.curriculum / "week1/lesson_1_2.md").read_text(encoding="utf-8") == "# Control Flow\n\nBody\n"
    assert tutor_cli.main([*root, "lesson-add", "1.2", str(draft)]) == 0
    assert "replaced" in capsys.readouterr().out
    assert tutor_cli.main([*root, "lesson-add", "2.1", str(draft)]) == 1
    assert "locked" in capsys.readouterr().out
