import json

import pytest

from server import quizzes
from server.verifications import VerificationLog

ALL_RIGHT = {"q1": 0, "q2": 1, "q3": 1}


def test_spec_without_answers(client, quiz):
    data = client.get("/api/quizzes/W1.2.quiz").json()
    assert [q["id"] for q in data["questions"]] == ["q1", "q2", "q3"]
    text = json.dumps(data)
    assert "answer" not in text and "explain" not in text
    assert "flips" not in text


def test_list(client, quiz):
    data = client.get("/api/quizzes").json()
    assert data["errors"] == []
    [q] = data["quizzes"]
    assert q == {"id": "W1.2.quiz", "title": "Boolean logic", "item": "W1.2.b",
                 "unlocked": True, "questions": 3, "pass_mark": 2, "last": None,
                 "problem": None}


def test_unknown_quiz(client, quiz):
    assert client.get("/api/quizzes/W9.9.quiz").status_code == 404


def test_pass_records_and_unlocks_tick(client, paths, quiz):
    r = client.post("/api/quizzes/W1.2.quiz/submit",
                    json={"answers": {"q1": 0, "q2": 1, "q3": 0}})
    assert r.status_code == 200
    body = r.json()
    assert (body["score"], body["total"], body["passed"], body["item"]) == (2, 3, True, "W1.2.b")
    # Explanations only for questions answered correctly; no answer key either way.
    res = {x["id"]: x for x in body["results"]}
    assert res["q1"]["correct"] and res["q1"]["explain"]
    assert not res["q3"]["correct"] and res["q3"]["explain"] == ""
    assert "answer" not in json.dumps(body["results"])

    [rec] = VerificationLog(paths.verifications).read()
    assert (rec.item, rec.kind, rec.passed, rec.by) == ("W1.2.b", "quiz", True, "app")
    saved = json.loads((paths.quiz_results / "W1.2.quiz.json").read_text(encoding="utf-8"))
    assert saved["item"] == "W1.2.b" and len(saved["attempts"]) == 1
    assert client.post("/api/tracker/check", json={"item": "W1.2.b"}).status_code == 200


def test_fail_records_but_does_not_unlock(client, paths, quiz):
    body = client.post("/api/quizzes/W1.2.quiz/submit",
                       json={"answers": {"q1": 1, "q2": 0, "q3": 1}}).json()
    assert (body["score"], body["passed"]) == (1, False)
    [rec] = VerificationLog(paths.verifications).read()
    assert rec.passed is False and rec.summary == "1/3 (pass 2)"
    assert client.post("/api/tracker/check", json={"item": "W1.2.b"}).status_code == 409


def test_attempts_accumulate(client, paths, quiz):
    for _ in range(2):
        client.post("/api/quizzes/W1.2.quiz/submit", json={"answers": ALL_RIGHT})
    saved = json.loads((paths.quiz_results / "W1.2.quiz.json").read_text(encoding="utf-8"))
    assert len(saved["attempts"]) == 2
    assert client.get("/api/quizzes").json()["quizzes"][0]["last"]["score"] == 3


def test_unanswered_rejected(client, paths, quiz):
    r = client.post("/api/quizzes/W1.2.quiz/submit", json={"answers": {"q1": 0}})
    assert r.status_code == 422
    assert VerificationLog(paths.verifications).read() == []


def test_locked_week_refused(client, paths, quiz):
    spec = dict(quiz, id="W2.2.quiz")
    d = paths.curriculum / "week2"
    d.mkdir()
    (d / "quiz_2_2.json").write_text(json.dumps(spec))
    r = client.post("/api/quizzes/W2.2.quiz/submit", json={"answers": ALL_RIGHT})
    assert r.status_code == 409 and "locked" in r.json()["detail"]
    assert VerificationLog(paths.verifications).read() == []


def test_item_must_be_a_quiz_item(client, paths, quiz):
    spec = dict(quiz, item="W1.2.a")
    (paths.curriculum / "week1" / "quiz_1_2.json").write_text(json.dumps(spec))
    r = client.post("/api/quizzes/W1.2.quiz/submit", json={"answers": ALL_RIGHT})
    assert r.status_code == 409 and "not a quiz item" in r.json()["detail"]


@pytest.mark.parametrize("change,error", [
    ({"pass_mark": 4}, "pass_mark"),
    ({"id": "quiz1"}, "W1.2.quiz"),
    ({"questions": [{"id": "q1", "prompt": "p", "choices": ["a", "b"], "answer": 2}]}, "answer"),
    ({"questions": [{"id": "q1", "prompt": "p", "choices": ["a"], "answer": 0}]}, "choices"),
])
def test_invalid_specs_reported(client, paths, quiz, change, error):
    (paths.curriculum / "week1" / "quiz_1_2.json").write_text(json.dumps(dict(quiz, **change)))
    data = client.get("/api/quizzes").json()
    assert data["quizzes"] == []
    [err] = data["errors"]
    assert err["file"] == "curriculum/week1/quiz_1_2.json"
    assert error in err["error"]


def test_duplicate_ids(paths, quiz):
    (paths.curriculum / "week1" / "quiz_other.json").write_text(json.dumps(quiz))
    found, errors = quizzes.load_all(paths.curriculum)
    assert list(found) == ["W1.2.quiz"]
    assert "duplicate" in errors[0]["error"]
