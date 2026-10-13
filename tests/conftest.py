import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.main import create_app
from server.paths import Paths

REAL_TRACKER = Path(__file__).resolve().parent.parent / "CURRICULUM_TRACKER.md"
TOKEN = "t"
HOST = "127.0.0.1:8765"
ORIGIN = f"http://{HOST}"


@pytest.fixture
def paths(tmp_path) -> Paths:
    shutil.copy(REAL_TRACKER, tmp_path / "CURRICULUM_TRACKER.md")
    (tmp_path / "workspace").mkdir()
    return Paths(tmp_path)


@pytest.fixture
def client(paths) -> TestClient:
    app = create_app(token=TOKEN, root=paths.root, dist=paths.root / "nodist", watch=False)
    c = TestClient(app, base_url=f"http://{HOST}")
    assert c.post("/api/session", json={"token": TOKEN}).status_code == 204
    return c


QUIZ = {
    "id": "W1.2.quiz",
    "title": "Boolean logic",
    "pass_mark": 2,
    "questions": [
        {"id": "q1", "prompt": "`not (True and False)`?", "choices": ["True", "False"],
         "answer": 0, "explain": "and is False, not flips it"},
        {"id": "q2", "prompt": "`bool([])`?", "choices": ["True", "False", "[]"],
         "answer": 1, "explain": "empty containers are falsy"},
        {"id": "q3", "prompt": "`0 or 'x'`?", "choices": ["0", "'x'", "True"],
         "answer": 1, "explain": "or returns the first truthy operand"},
    ],
}


@pytest.fixture
def quiz(paths) -> dict:
    d = paths.curriculum / "week1"
    d.mkdir(parents=True)
    (d / "quiz_1_2.json").write_text(json.dumps(QUIZ), encoding="utf-8")
    return QUIZ
