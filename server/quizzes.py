"""Quiz specs, server-side grading and attempt results (HANDOFF.md §5).

Specs live in curriculum/weekN/quiz_<task>.json and are indexed by their "id".
Answers never reach the browser: GET returns the questions without answer or
explanation, and grading happens here. The browser and the CLI runner
(server/quiz_cli.py) both go through record_attempt(), so they write the same
result file and the same verification record.

Results: progress/quizzes/<id>.json, {"id", "title", "item", "attempts": [...]},
newest attempt last. The tutor reads it to walk through missed questions.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError, model_validator

from server import tracker as tr
from server.paths import Paths
from server.tracker import locked, write_atomic
from server.verifications import Record, VerificationLog, verify_kind

QUIZ_ID_RE = re.compile(r"^W(\d+)\.(\d+)\.[A-Za-z0-9_-]+$")
MAX_CHOICES = 9  # keys 1-9 pick an answer


class QuizError(Exception):
    pass


class Unanswered(QuizError):
    pass


class Question(BaseModel):
    id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    choices: list[str] = Field(min_length=2, max_length=MAX_CHOICES)
    answer: int
    explain: str = ""

    @model_validator(mode="after")
    def answer_in_range(self) -> Question:
        if not 0 <= self.answer < len(self.choices):
            raise ValueError(f"{self.id}: answer {self.answer} is not a choice index")
        return self


class Quiz(BaseModel):
    id: str
    title: str
    pass_mark: int = Field(ge=1)
    item: str | None = None  # tracker item this verifies; derived from id if absent
    questions: list[Question] = Field(min_length=1)

    @model_validator(mode="after")
    def consistent(self) -> Quiz:
        if not QUIZ_ID_RE.match(self.id):
            raise ValueError(f"id {self.id!r} must look like W1.2.quiz")
        ids = [q.id for q in self.questions]
        if len(set(ids)) != len(ids):
            raise ValueError("question ids must be unique")
        if self.pass_mark > len(self.questions):
            raise ValueError("pass_mark is higher than the number of questions")
        return self

    @property
    def task_id(self) -> str:
        m = QUIZ_ID_RE.match(self.id)
        assert m
        return f"{m[1]}.{m[2]}"

    def public(self) -> dict:
        """The spec as the browser may see it: no answers, no explanations."""
        return {
            "id": self.id, "title": self.title, "pass_mark": self.pass_mark,
            "questions": [{"id": q.id, "prompt": q.prompt, "choices": q.choices}
                          for q in self.questions],
        }


def load_all(curriculum: Path) -> tuple[dict[str, Quiz], list[dict]]:
    """Every valid spec by id, plus a list of files that failed to load."""
    quizzes: dict[str, Quiz] = {}
    errors: list[dict] = []
    for path in sorted(curriculum.glob("week*/quiz_*.json")):
        rel = path.relative_to(curriculum.parent).as_posix()
        try:
            quiz = Quiz.model_validate_json(path.read_text(encoding="utf-8"))
        except ValidationError as e:
            errors.append({"file": rel, "error": "; ".join(
                f"{'.'.join(map(str, err['loc'])) or 'spec'}: {err['msg']}" for err in e.errors())})
            continue
        except (OSError, ValueError) as e:
            errors.append({"file": rel, "error": str(e)})
            continue
        if quiz.id in quizzes:
            errors.append({"file": rel, "error": f"duplicate quiz id {quiz.id}"})
            continue
        quizzes[quiz.id] = quiz
    return quizzes, errors


def get(paths: Paths, quiz_id: str) -> Quiz:
    quizzes, _ = load_all(paths.curriculum)
    if quiz_id not in quizzes:
        raise KeyError(f"no quiz {quiz_id}")
    return quizzes[quiz_id]


def item_for(quiz: Quiz, t: tr.Tracker) -> tr.Item:
    """The tracker item a quiz verifies: its explicit "item", else the
    task's "Quiz:" item. It must be a quiz item."""
    if quiz.item:
        try:
            item = t.item(quiz.item)
        except KeyError:
            raise QuizError(f"{quiz.id}: no item {quiz.item} in the tracker") from None
    else:
        task = next((tk for w in t.weeks for tk in w.tasks if tk.id == quiz.task_id), None)
        if task is None:
            raise QuizError(f"{quiz.id}: no task {quiz.task_id} in the tracker")
        item = next((i for i in task.items if verify_kind(i.text) == "quiz"), None)
        if item is None:
            raise QuizError(f"{quiz.id}: task {quiz.task_id} has no Quiz: item")
    if verify_kind(item.text) != "quiz":
        raise QuizError(f"{quiz.id}: {item.id} is not a quiz item")
    return item


def grade(quiz: Quiz, answers: dict[str, int]) -> dict:
    missing = [q.id for q in quiz.questions if q.id not in answers]
    if missing:
        raise Unanswered(f"unanswered: {', '.join(missing)}")
    results = [{"q": q.id, "choice": answers[q.id], "correct": answers[q.id] == q.answer}
               for q in quiz.questions]
    score = sum(r["correct"] for r in results)
    return {"score": score, "total": len(results), "pass_mark": quiz.pass_mark,
            "passed": score >= quiz.pass_mark, "answers": results}


def record_attempt(paths: Paths, quiz: Quiz, answers: dict[str, int], by: str) -> dict:
    """Grade, append to progress/quizzes/<id>.json and the verification log.
    Refused for a locked week, so a quiz can't verify ahead of the gate."""
    t = tr.load(paths.tracker)
    item = item_for(quiz, t)
    if not t.item_unlocked(item.id):
        raise QuizError(f"{item.id} is in a locked week")
    attempt = grade(quiz, answers) | {
        "at": datetime.now().astimezone().isoformat(timespec="seconds"), "by": by}

    out = paths.quiz_results / f"{quiz.id}.json"
    with locked(paths.quiz_results / f".{quiz.id}.lock"):
        try:
            doc = json.loads(out.read_text(encoding="utf-8"))
            attempts = doc.get("attempts", []) if isinstance(doc, dict) else []
        except (OSError, ValueError):
            attempts = []
        attempts.append(attempt)
        write_atomic(out, json.dumps({"id": quiz.id, "title": quiz.title, "item": item.id,
                                      "attempts": attempts}, indent=2, ensure_ascii=False) + "\n")

    summary = f"{attempt['score']}/{attempt['total']} (pass {quiz.pass_mark})"
    VerificationLog(paths.verifications).append(Record(
        item=item.id, kind="quiz", passed=attempt["passed"], summary=summary,
        at=attempt["at"], by=by))
    return attempt | {"item": item.id}


def last_attempt(paths: Paths, quiz_id: str) -> dict | None:
    try:
        doc = json.loads((paths.quiz_results / f"{quiz_id}.json").read_text(encoding="utf-8"))
        attempts = doc["attempts"]
        return attempts[-1] if attempts else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def feedback(quiz: Quiz, attempt: dict) -> list[dict]:
    """Per-question result for the browser. Explanations only for questions
    answered correctly; missed ones are for the tutor to walk through, and
    showing the explanation would hand over the answer for the retake."""
    by_id = {q.id: q for q in quiz.questions}
    return [{"id": a["q"], "choice": a["choice"], "correct": a["correct"],
             "explain": by_id[a["q"]].explain if a["correct"] else ""}
            for a in attempt["answers"]]


class SubmitRequest(BaseModel):
    answers: dict[str, int]


def router(paths: Paths) -> APIRouter:
    r = APIRouter(prefix="/api/quizzes")
    paths.quiz_results.mkdir(parents=True, exist_ok=True)

    def load(quiz_id: str) -> Quiz:
        try:
            return get(paths, quiz_id)
        except KeyError as e:
            raise HTTPException(404, e.args[0]) from None

    @r.get("")
    def list_quizzes():
        quizzes, errors = load_all(paths.curriculum)
        try:
            t: tr.Tracker | None = tr.load(paths.tracker)
        except (OSError, tr.TrackerError):
            t = None
        out = []
        for q in quizzes.values():
            item, unlocked, problem = None, False, None
            if t is not None:
                try:
                    it = item_for(q, t)
                    item, unlocked = it.id, t.item_unlocked(it.id)
                except QuizError as e:
                    problem = str(e)
            out.append({"id": q.id, "title": q.title, "item": item, "unlocked": unlocked,
                        "questions": len(q.questions), "pass_mark": q.pass_mark,
                        "last": last_attempt(paths, q.id), "problem": problem})
        out.sort(key=lambda d: [int(n) for n in QUIZ_ID_RE.match(d["id"]).groups()])  # type: ignore[union-attr]
        return {"quizzes": out, "errors": errors}

    @r.get("/{quiz_id}")
    def get_quiz(quiz_id: str):
        return load(quiz_id).public()

    @r.post("/{quiz_id}/submit")
    def submit(quiz_id: str, body: SubmitRequest):
        quiz = load(quiz_id)
        try:
            attempt = record_attempt(paths, quiz, body.answers, by="app")
        except Unanswered as e:
            raise HTTPException(422, str(e)) from None
        except QuizError as e:
            raise HTTPException(409, str(e)) from None
        except tr.TrackerError as e:
            raise HTTPException(422, str(e)) from None
        return {k: attempt[k] for k in ("item", "score", "total", "pass_mark", "passed", "at")} | {
            "results": feedback(quiz, attempt)}

    return r
