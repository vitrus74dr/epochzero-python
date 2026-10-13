# Context Managers: Files and JSON

Programs that forget everything when they exit aren't much use. This lesson covers
reading and writing files *safely*, and saving structured data as JSON, the format
you'll meet in every web API next lesson.

## 1. `with open(...)`

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")
    f.write("second line\n")

with open("notes.txt", encoding="utf-8") as f:
    text = f.read()
```

`with` is a **context manager**: when the indented block ends, the file is closed,
*even if an exception happened inside it*. Without `with`, an error halfway through
can leave a file open and half-written, which is on the week's pitfall watch.

The mode is the second argument:

| Mode | Means |
|---|---|
| `"r"` | read (the default); the file must exist |
| `"w"` | write; **empties the file first**, or creates it |
| `"a"` | append to the end, or create |
| `"x"` | create; fails if the file already exists |

Always pass `encoding="utf-8"`. Without it, Python uses the operating system's
default, so a file with `é` or `🔥` written on one machine can come back garbled on another.

## 2. Reading line by line

A file is iterable, one line at a time, so even a 2 GB log file never has to fit in memory:

```python
with open("notes.txt", encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):
        print(line_number, line.rstrip("\n"))
```

Each `line` ends with `"\n"`; `.rstrip("\n")` removes it.

## 3. `pathlib`: paths as objects

```python
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
notes = data_dir / "notes.txt"          # joins with the right separator on any OS
notes.write_text("hello\n", encoding="utf-8")
notes.read_text(encoding="utf-8")       # 'hello\n'
notes.exists(), notes.suffix, notes.stem, notes.name
# (True, '.txt', 'notes', 'notes.txt')
```

`write_text` and `read_text` open and close the file for you, which is ideal for small files.

To find a file *next to your script*, whatever folder you run it from:

```python fragment
HERE = Path(__file__).parent
config = HERE / "config.json"
```

You'll need this pattern for game assets in Week 6.

## 4. JSON

JSON is text that looks like Python's dicts and lists:

```python
import json

profile = {"name": "Ada", "scores": [95, 88], "admin": False, "nickname": None}

with open("profile.json", "w", encoding="utf-8") as f:
    json.dump(profile, f, indent=2)

with open("profile.json", encoding="utf-8") as f:
    loaded = json.load(f)

loaded == profile          # True
```

`dump`/`load` work with files; `dumps`/`loads` (with an **s**, for *string*) work with strings.

Python `True`/`None` become JSON `true`/`null`. JSON has no dates, sets or custom
objects: convert them to strings, lists or dicts first (Lesson 3.3 did this for dates).

A file that isn't valid JSON raises `json.JSONDecodeError`:

```python
>>> json.loads("{'name': 'Ada'}")
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

JSON requires **double** quotes.

## 5. Your turn (W4.1.a)

Write `week4/t4.1-files/notes.py`, a tiny notes app:

- `add` appends a note with a timestamp to `notes.json`, a list of `{"time": ..., "text": ...}` dicts
- `list` prints them numbered
- a missing `notes.json` means "no notes yet", not a crash. Catch `FileNotFoundError`
  specifically.

Use `with`, `encoding="utf-8"` and `json.dump(..., indent=2)`. Then open `notes.json`
in the workbench to see what you wrote, and show the tutor.

## Pitfalls

- `open()` without `with`. Use `with`, always.
- No `encoding="utf-8"`.
- Opening with `"w"` when you meant `"a"`: the old content is gone.
- Single quotes in hand-written JSON.
