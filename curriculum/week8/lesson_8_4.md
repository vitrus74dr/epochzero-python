# Web App: Prediction Service

A model in a notebook helps one person. A model behind a web address helps everyone. You'll
put your Task 8.3 model behind **FastAPI**: a form for humans, a JSON API for programs, and
a **SQLite** database that remembers every prediction. Along the way you'll meet the two
most important habits of web development: validate every input, and never build SQL
from strings.

```sh
uv add "fastapi[standard]" joblib pandas scikit-learn
```

`"fastapi[standard]"` (with the quotes) also installs the `fastapi` command, the uvicorn
server, form parsing, and the `httpx` library that the tests use.

## 1. A first API

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello/{name}")
def hello(name: str, excited: bool = False):
    return {"message": f"Hello, {name}{'!' if excited else '.'}"}
```

Save as `hello.py`, then run `uv run fastapi dev hello.py` and open
`http://127.0.0.1:8000/hello/Ada?excited=true`. Also try `http://127.0.0.1:8000/docs`:
FastAPI writes interactive documentation for you, from your type hints.

- `@app.get("/hello/{name}")` is a **decorator**: it registers the function for that URL.
- `{name}` in the path becomes the `name` argument. Other parameters (`excited`) come from the query string.
- Return a dict and FastAPI sends it as JSON.

## 2. Request bodies with Pydantic

For POST requests, describe the expected JSON as a Pydantic model. FastAPI checks every
request against it **before** your function runs:

```python
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Patient(BaseModel):
    age: Annotated[float, Field(gt=0, lt=120)]
    sex: Annotated[int, Field(ge=1, le=2)]
    bmi: Annotated[float, Field(gt=0)]


@app.post("/api/predict")
def predict(p: Patient):
    return {"received": p.model_dump()}
```

Send `{"age": -5, "sex": 2, "bmi": 27}` and you get **422 Unprocessable Entity**, with a
message saying which field is wrong and why. Your function never sees bad data, and the
model never gets nonsense. This is W8.4.d's "invalid input → 422".

## 3. Testing an API without running a server

```python
from fastapi.testclient import TestClient

client = TestClient(app)
r = client.post("/api/predict", json={"age": 50, "sex": 2, "bmi": 27.1})
r.status_code, r.json()["received"]["sex"]      # (200, 2)
client.post("/api/predict", json={"age": 50, "sex": 3, "bmi": 27.1}).status_code   # 422
```

`TestClient` calls your app directly, as if it were a browser. No server and no network
are needed, so tests are fast.

## 4. The app factory

`pygrid-tutor scaffold W8.4` gives `app.py` and `test_app.py`. The contract is one function:

```python fragment
def create_app(model, db_path) -> FastAPI:
```

Everything the app depends on comes **in** as an argument instead of being loaded at
import time. So the tests pass a fake model (it always predicts 150.0) and a throwaway
database, and the real app passes `joblib.load("model.joblib")` and `predictions.db`.
It's the same "inject the dependency" idea as `today` in Lesson 3.3 and the HTTP session
in Lesson 4.3, at a bigger scale.

Give the model a **DataFrame** with the dataset's column names. Your 8.3 pipeline's
`ColumnTransformer` picks columns *by name*:

```python fragment
X = pd.DataFrame([patient.model_dump()], columns=FEATURES)
prediction = float(model.predict(X)[0])
```

## 5. HTML forms

People don't type JSON. `GET /` returns a page with a form; the browser POSTs its fields
to `/predict`. FastAPI can validate form fields with the **same** Pydantic model:

```python fragment
from fastapi import Form
from fastapi.responses import HTMLResponse

@app.post("/predict", response_class=HTMLResponse)
def predict_form(data: Annotated[Patient, Form()]):
    ...
    return f"<p>Predicted progression: {prediction:.1f}</p>"
```

> **Gotcha:** HTML forms send every value as a **string**. `sex: Literal[1, 2]` looks
> neat, but Pydantic won't turn the string `"2"` into the number `2` for a `Literal`, so
> every form submission fails with 422. `Annotated[int, Field(ge=1, le=2)]` converts
> `"2"` first, then checks the range.

When you put any text from users or the database into HTML, pass it through
`html.escape()` first. Otherwise a value like `<script>...` becomes code on your page.
(In a bigger app, Jinja2 templates escape for you.)

## 6. SQLite and parameterized queries

SQLite is a whole SQL database in a single file, built into Python:

```python
import json
import sqlite3

with sqlite3.connect("demo.db") as db:
    db.execute("CREATE TABLE IF NOT EXISTS predictions ("
               "id INTEGER PRIMARY KEY, created TEXT, features TEXT, prediction REAL)")
    cur = db.execute(
        "INSERT INTO predictions (created, features, prediction) VALUES (?, ?, ?)",
        ("2026-10-13T20:15:00", json.dumps({"age": 50}), 151.3),
    )
    new_id = cur.lastrowid
    rows = db.execute("SELECT id, prediction FROM predictions ORDER BY id DESC LIMIT 20").fetchall()
```

The `?` placeholders are the habit that matters. The values travel **separately** from
the SQL text, so nothing a user types can change the query. Compare:

```python fragment
db.execute(f"INSERT INTO notes VALUES ('{text}')")      # ⚠ NEVER: SQL injection
db.execute("INSERT INTO notes VALUES (?)", (text,))      # always
```

With the f-string, text such as `x'); DROP TABLE notes;--` becomes part of your SQL.
In this app, validation already rejects text in number fields, but placeholders are the
habit for *every* query. The tutor checks every `execute` call at W8.4.c.

`with sqlite3.connect(...)` commits the transaction when the block succeeds; it does
**not** close the connection. For a small app, opening a connection per request is fine.

## 7. How it's checked

- **W8.4.a**: `/grill-me W8.4` (routes, the Pydantic model, the table design, error pages).
- **W8.4.b–c**: a demo: the form in your browser, a `curl` or `/docs` call to the API, the history page.
- **W8.4.d**: `/verify W8.4` (the scaffold's 11 tests, plus any you add).
- **W8.4.e**: `walkthrough.md`: follow one prediction from the browser to the database and back.

## Pitfalls

- SQL built with f-strings or `+`.
- Loading the model or opening the database at import time: then the tests can't inject fakes.
- `Literal[1, 2]` for a form field (section 5).
- Unescaped values in HTML.
- Passing the model a plain list when its pipeline selects columns by name.
