"""W8.4.d: the prediction service, tested with FastAPI's TestClient.

A fake model stands in for the real one: it records what it was given and
predicts 150.0, so these tests need neither scikit-learn nor a trained file.
Each test gets a fresh SQLite file under pytest's tmp_path.
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import FEATURES, create_app

PATIENT = {"age": 50, "sex": 2, "bmi": 27.1, "bp": 95.0, "s1": 190, "s2": 115.0,
           "s3": 48.0, "s4": 4.0, "s5": 4.6, "s6": 92}


class FakeModel:
    def __init__(self):
        self.seen = []

    def predict(self, X):
        self.seen.append(X)
        return [150.0] * len(X)


@pytest.fixture
def model():
    return FakeModel()


@pytest.fixture
def client(model, tmp_path):
    return TestClient(create_app(model, tmp_path / "predictions.db"))


def test_form_page(client):
    r = client.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    html = r.text.lower()
    assert "<form" in html and 'action="/predict"' in html
    for name in FEATURES:
        assert f'name="{name}"' in html


def test_api_predict(client, model):
    r = client.post("/api/predict", json=PATIENT)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] == 150.0 and isinstance(body["id"], int)
    X = model.seen[0]
    assert list(X.columns) == FEATURES, "give the model a DataFrame with the dataset's columns"
    assert X.iloc[0]["sex"] == 2


@pytest.mark.parametrize("change", [
    {"sex": 3},              # sex is coded 1 or 2
    {"age": -5},             # impossible age
    {"bmi": "heavy"},        # not a number
    {"bp": None},            # missing value
])
def test_api_rejects_invalid_input(client, model, change):
    r = client.post("/api/predict", json=PATIENT | change)
    assert r.status_code == 422
    assert model.seen == [], "invalid input must never reach the model"


def test_api_rejects_missing_field(client):
    partial = {k: v for k, v in PATIENT.items() if k != "s6"}
    assert client.post("/api/predict", json=partial).status_code == 422


def test_form_post_shows_prediction(client):
    r = client.post("/predict", data={k: str(v) for k, v in PATIENT.items()})
    assert r.status_code == 200 and "150" in r.text


def test_predictions_are_stored(client, tmp_path):
    for _ in range(3):
        client.post("/api/predict", json=PATIENT)
    with sqlite3.connect(tmp_path / "predictions.db") as db:
        assert db.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] == 3


def test_history_newest_first(client):
    ids = [client.post("/api/predict", json=PATIENT | {"age": a}).json()["id"] for a in (30, 40, 50)]
    history = client.get("/api/history").json()
    assert [row["id"] for row in history] == ids[::-1]
    assert history[0]["features"]["age"] == 50 and history[0]["prediction"] == 150.0
    page = client.get("/history")
    assert page.status_code == 200 and "150" in page.text


def test_sql_injection_is_harmless(client, tmp_path):
    """Parameterized queries: the table survives a hostile-looking value."""
    r = client.post("/predict", data={k: str(v) for k, v in PATIENT.items()} | {"bmi": "1); DROP TABLE predictions;--"})
    assert r.status_code == 422
    client.post("/api/predict", json=PATIENT)
    with sqlite3.connect(tmp_path / "predictions.db") as db:
        assert db.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] == 1
