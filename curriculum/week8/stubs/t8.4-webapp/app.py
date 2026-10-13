"""W8.4: the Week 8 model as a web service.

    uv run fastapi dev app.py          # then open http://127.0.0.1:8000

Needs: uv add "fastapi[standard]" joblib pandas scikit-learn
("fastapi[standard]" brings the `fastapi` command, uvicorn, form parsing and the
httpx library that TestClient uses.)

The tests call create_app() with a fake model and a temporary database, so
nothing below may load the model or open the database at import time.
"""

import sqlite3
from pathlib import Path

import pandas as pd
from fastapi import FastAPI

FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
HERE = Path(__file__).parent

# TODO: a Pydantic model `Patient` for the JSON body: one field per feature,
#       with constraints so nonsense is rejected with 422 (sex is 1 or 2,
#       ages and measurements are positive, nothing is optional).


def create_app(model, db_path: Path) -> FastAPI:
    """Build the app around `model` (anything with .predict(DataFrame)) and an
    SQLite file at `db_path` (create the table if it doesn't exist).

    Routes:
      GET  /              HTML form, one input per feature, posting to /predict
      POST /predict       form fields -> HTML page showing the prediction
      POST /api/predict   JSON Patient -> {"prediction": float, "id": int}
      GET  /history       HTML table of recent predictions, newest first
      GET  /api/history   the same as JSON: [{"id", "created", "features": {...},
                          "prediction"}, ...] newest first
    Every prediction is stored with a parameterized INSERT.
    """
    pass  # stub


def load_default_app() -> FastAPI:
    """The real app: model.joblib from Task 8.3, predictions.db beside this file."""
    import joblib

    return create_app(joblib.load(HERE / "model.joblib"), HERE / "predictions.db")


if (HERE / "model.joblib").exists():
    app = load_default_app()        # what `fastapi dev app.py` serves
