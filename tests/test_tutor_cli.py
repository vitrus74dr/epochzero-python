import json
import sys

import pytest

from server import tests_runner, tutor_cli
from server.paths import Paths
from server.tasks import FolderError, task_docs, task_folder
from server.verifications import Record, VerificationLog

PASSING = "def test_a():\n    assert 1 + 1 == 2\n"
FAILING = "def test_a():\n    assert 1 + 1 == 3\n"
PLAN = "# Implementation plan: calculator\n\n" + "## Goal\nA calculator that never crashes on bad input.\n" * 8


@pytest.fixture(autouse=True)
def app_python(monkeypatch):
    monkeypatch.setattr(tests_runner, "learner_python", lambda ws, start: [sys.executable])


@pytest.fixture
def tutor(paths, capsys):
    def run(*argv: str) -> tuple[int, str]:
        code = tutor_cli.main(["--root", str(paths.root), *argv])
        out = capsys.readouterr()
        return code, out.out + out.err
    return run


def folder(paths: Paths, name="week1/t1.3-calculator", **files: str):
    d = paths.workspace / name
    d.mkdir(parents=True, exist_ok=True)
    for fname, body in files.items():
        (d / fname).write_text(body)
    return d


def records(paths):
    return VerificationLog(paths.verifications).read()


# ── task folders ──

def test_task_folder(paths):
    assert task_folder(paths, "1.3") is None
    d = folder(paths)
    folder(paths, "week1/t1.30-other")  # must not match 1.3
    assert task_folder(paths, "1.3") == d
    assert task_folder(paths, "W1.3") == d
    folder(paths, "week1/t1.3")
    with pytest.raises(FolderError, match="several"):
        task_folder(paths, "1.3")


def test_task_docs(paths):
    assert task_docs(paths, "1.3") == {"folder": None, "plan": None, "walkthrough": None}
    folder(paths, **{"implementation_plan.md": PLAN})
    assert task_docs(paths, "1.3") == {"folder": "week1/t1.3-calculator",
                                        "plan": "week1/t1.3-calculator/implementation_plan.md",
                                        "walkthrough": None}


def test_tracker_json_has_docs(client, paths):
    folder(paths, **{"walkthrough.md": PLAN})
    task = client.get("/api/tracker").json()["weeks"][0]["tasks"][2]
    assert task["id"] == "1.3"
    assert task["docs"]["walkthrough"] == "week1/t1.3-calculator/walkthrough.md"
    assert task["items"][2]["verify"] == "pytest"


# ── the acceptance flow: /verify W1.3 then /checkoff W1.3.c ──

def test_verify_task_then_checkoff(paths, tutor):
    folder(paths, **{"test_calc.py": PASSING})
    code, out = tutor("verify", "W1.3")
    assert code == 0, out
    assert "RESULT: PASS  1 passed" in out
    assert "recorded: W1.3.c pytest pass" in out
    [rec] = records(paths)
    assert (rec.item, rec.kind, rec.by) == ("W1.3.c", "pytest", "claude-code")

    code, out = tutor("checkoff", "W1.3.c")
    assert code == 0 and "ticked: W1.3.c" in out
    assert "W1.3.c" in paths.checked.read_text() and "- [x]" not in paths.tracker.read_text()


def test_verify_fail_blocks_checkoff(paths, tutor):
    folder(paths, **{"test_calc.py": FAILING})
    code, out = tutor("verify", "W1.3.c")
    assert code == 1 and "RESULT: FAIL" in out
    code, out = tutor("checkoff", "W1.3.c")
    assert code == 1 and "refused: W1.3.c: no passing record" in out
    assert not paths.checked.exists()


def test_verify_needs_a_folder(paths, tutor):
    code, out = tutor("verify", "W1.3")
    assert code == 2 and "t1.3-<slug>" in out


def test_verify_with_path(paths, tutor, monkeypatch):
    folder(paths, "week1/calc", **{"test_calc.py": PASSING})
    monkeypatch.chdir(paths.workspace)
    code, out = tutor("verify", "W1.3", "--path", "week1/calc")
    assert code == 0, out
    code, out = tutor("verify", "W1.3", "--path", "../progress")
    assert code == 2 and "inside workspace" in out


@pytest.mark.parametrize("target,msg", [
    ("W1.2", "no pytest-verified items"),
    ("W1.1.a", "verified by tutor"),
    ("W2.1.b", "locked week"),
])
def test_verify_refusals(paths, tutor, target, msg):
    folder(paths, **{"test_calc.py": PASSING})
    code, out = tutor("verify", target, "--path", str(paths.workspace / "week1/t1.3-calculator"))
    assert code == 1 and msg in out
    assert records(paths) == []


# ── record ──

def test_record_tutor(paths, tutor):
    code, out = tutor("record", "W1.1.a", "--kind", "tutor")
    assert code == 2 and "--summary" in out
    code, out = tutor("record", "W1.1.a", "--kind", "tutor", "--summary", "uv venv on 3.12")
    assert code == 0
    [rec] = records(paths)
    assert (rec.kind, rec.passed, rec.summary) == ("tutor", True, "uv venv on 3.12")


def test_record_kind_must_match(paths, tutor):
    code, out = tutor("record", "W1.3.c", "--kind", "tutor", "--summary", "looked fine")
    assert code == 1 and "/verify" in out
    code, out = tutor("record", "W1.2.b", "--kind", "tutor", "--summary", "x")
    assert code == 1 and "quiz" in out
    assert records(paths) == []


def test_record_artifact_checks_the_file(paths, tutor):
    code, out = tutor("record", "W1.3.a", "--kind", "artifact")
    assert code == 1 and "no folder" in out
    folder(paths, **{"implementation_plan.md": "# TODO\n"})
    code, out = tutor("record", "W1.3.a", "--kind", "artifact")
    assert code == 1 and "stub" in out
    folder(paths, **{"implementation_plan.md": PLAN})
    code, out = tutor("record", "W1.3.a", "--kind", "artifact", "--summary", "approved")
    assert code == 0
    [rec] = records(paths)
    assert rec.kind == "artifact" and rec.summary.startswith("week1/t1.3-calculator/implementation_plan.md")
    assert rec.summary.endswith("; approved")
    # walkthrough item wants the other file
    code, out = tutor("record", "W1.3.d", "--kind", "artifact")
    assert code == 1 and "walkthrough.md does not exist" in out


def test_record_locked_week(paths, tutor):
    code, out = tutor("record", "W2.1.a", "--kind", "tutor", "--summary", "x")
    assert code == 1 and "locked" in out


def test_checkoff_undo_and_unknown(paths, tutor):
    VerificationLog(paths.verifications).append(
        Record(item="W1.1.a", kind="tutor", passed=True, summary="x"))
    assert tutor("checkoff", "W1.1.a")[0] == 0
    code, out = tutor("checkoff", "W1.1.a", "--undo")
    assert code == 0 and "unticked" in out
    code, out = tutor("checkoff", "W9.9.z")
    assert code == 1 and "no item" in out


def test_status(paths, tutor):
    folder(paths, "week1/t1.1-hello")
    VerificationLog(paths.verifications).append(
        Record(item="W1.1.a", kind="tutor", passed=True, summary="env ok"))
    code, out = tutor("status")
    assert code == 0
    assert "current: [W1.1.a]" in out
    assert "folder:  workspace/week1/t1.1-hello" in out
    assert "ready for /checkoff" in out
    assert "PASS  W1.1.a" in out


# ── quizzes ──

def test_quiz_check(paths, tutor, quiz):
    code, out = tutor("quiz-check", str(paths.curriculum / "week1/quiz_1_2.json"))
    assert code == 0 and "verifies W1.2.b" in out
    bad = paths.curriculum / "week1/quiz_bad.json"
    bad.write_text(json.dumps(dict(quiz, id="W1.1.quiz", pass_mark=9)))
    code, out = tutor("quiz-check", str(bad))
    assert code == 1 and "pass_mark" in out


def test_quiz_add_installs_draft(paths, tutor):
    from conftest import QUIZ
    draft = paths.workspace / ".epochzero" / "quiz.json"
    draft.parent.mkdir()
    draft.write_text(json.dumps(QUIZ))
    code, out = tutor("quiz-add", str(draft))
    assert code == 0 and "installed: curriculum/week1/quiz_1_2.json (W1.2.quiz, verifies W1.2.b)" in out
    assert json.loads((paths.curriculum / "week1/quiz_1_2.json").read_text())["id"] == "W1.2.quiz"
    # Re-adding replaces it; the same id under another file name is refused.
    assert tutor("quiz-add", str(draft))[0] == 0
    (paths.curriculum / "week1/quiz_old.json").write_text(json.dumps(QUIZ))
    code, out = tutor("quiz-add", str(draft))
    assert code == 1 and "already defined" in out
    draft.write_text(json.dumps(dict(QUIZ, pass_mark=0)))
    assert tutor("quiz-add", str(draft))[0] == 1


def test_status_lists_task_items(paths, tutor):
    code, out = tutor("status")
    assert "task 1.1 items" in out and "[ ] W1.1.c  pytest" in out
    assert "pitfalls:" in out


def test_quiz_results_show_tutor_the_answers(client, paths, tutor, quiz):
    code, out = tutor("quiz-results", "W1.2.quiz")
    assert "no attempts" in out
    client.post("/api/quizzes/W1.2.quiz/submit", json={"answers": {"q1": 0, "q2": 0, "q3": 1}})
    code, out = tutor("quiz-results", "W1.2.quiz")
    assert code == 0 and "latest 2/3 (PASS" in out
    assert "missed q2" in out and "learner chose: True" in out and "correct:       False" in out
    assert "missed q1" not in out


def test_practice_quiz_records_nothing(client, paths, quiz):
    spec = dict(quiz, id="W1.1.check")
    (paths.curriculum / "week1/quiz_1_1.json").write_text(json.dumps(spec))
    listed = {q["id"]: q for q in client.get("/api/quizzes").json()["quizzes"]}
    assert listed["W1.1.check"]["item"] is None and listed["W1.1.check"]["unlocked"]
    body = client.post("/api/quizzes/W1.1.check/submit",
                       json={"answers": {"q1": 0, "q2": 1, "q3": 1}}).json()
    assert body["passed"] and body["item"] is None
    assert records(paths) == []
    assert json.loads((paths.quiz_results / "W1.1.check.json").read_text())["attempts"]
