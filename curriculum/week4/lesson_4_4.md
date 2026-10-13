# Automation: File Organizer & Log Analyzer

Python's most immediately useful job is doing boring things for you. You'll build two
command-line tools you might genuinely keep: one tidies a messy folder (your Downloads,
say), and one reads a log file and tells you what went wrong. New tools: `argparse`
for command-line options, `pathlib` for walking folders, `re` for pattern matching,
and `collections.Counter`.

Start with `epochzero-tutor scaffold W4.4`. You get `organize.py` and `logstats.py`, each a
set of stubs with docstrings saying exactly what they must do, plus the tests. This is
a **guided** task: the design is given and the code is yours.

## 1. Command-line arguments with `argparse`

```python
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Sort files into folders by type.")
parser.add_argument("folder", type=Path, help="the folder to tidy")
parser.add_argument("--dry-run", action="store_true", help="show the plan, move nothing")

args = parser.parse_args(["Downloads", "--dry-run"])     # normally: parse_args()
args.folder, args.dry_run          # (PosixPath('Downloads'), True)
```

- A name without dashes (`folder`) is **positional**, and required.
- `--dry-run` is an **option**; `action="store_true"` makes it a flag that is `False`
  unless it's given. In code it's `args.dry_run`: dashes become underscores.
- `--help` comes free: try `uv run python organize.py --help`.

Why `main(argv=None)`, with `parse_args(argv)` inside? With `None`, argparse reads the real
command line; a test can pass a list instead. The tests call `main([str(tmp_path), "--dry-run"])`.

## 2. Walking a folder

```python
from pathlib import Path

folder = Path(".")
for p in sorted(folder.iterdir()):          # direct children only
    if p.is_file() and not p.name.startswith("."):
        print(p.name, p.suffix.lower())
```

`Path("photo.JPG").suffix` is `".JPG"`: compare with `.lower()`. `folder.rglob("*")`
walks *every* level, which is useful elsewhere, but here the organizer only touches the top level.

Moving a file is `src.rename(dest)` (the same disk) or `shutil.move(src, dest)` (it
works across disks). Create the target folder first with `dest.parent.mkdir(exist_ok=True)`.

## 3. Dry runs and name clashes

A tool that moves files should be able to **show what it would do** first. That's why
the organizer *plans* (a list of `(source, destination)` pairs) separately from *doing*
(`apply_moves`). The plan is easy to test, print and check; `--dry-run` just stops after
printing it.

Clash: `cat.jpg` is already in `images/`. Never overwrite. Pick `cat (1).jpg`, then
`cat (2).jpg`. Watch out: two files in the *same run* can want the same name, so
`unique_destination` also takes the set of names already planned.

```python
from pathlib import Path

dest = Path("images/cat.jpg")
dest.with_name(f"{dest.stem} (1){dest.suffix}")      # PosixPath('images/cat (1).jpg')
```

## 4. Regular expressions

A log line:

```text
2026-10-13 14:02:11 ERROR [db] connection refused
```

A **regular expression** describes its shape, and *named groups* pull the parts out:

```python
import re

LINE_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<hour>\d{2}):\d{2}:\d{2} "
    r"(?P<level>INFO|ERROR) "
    r"\[(?P<source>[^\]]+)\] "
    r"(?P<message>.*)"
)
m = LINE_RE.fullmatch("2026-10-13 14:02:11 ERROR [db] connection refused")
m["level"], m["source"], m["message"]      # ('ERROR', 'db', 'connection refused')
```

| Piece | Matches |
|---|---|
| `\d{4}` | exactly four digits |
| `(?P<name>...)` | a group you can read back as `m["name"]` |
| `INFO\|ERROR` | either word |
| `\[` `\]` | literal brackets (plain `[` starts a character class) |
| `[^\]]+` | one or more characters that aren't `]` |
| `.*` | anything, to the end |

`fullmatch` must match the **whole** string; `match` only the start; `search` anywhere.
Always write patterns as raw strings, `r"..."`, so `\d` reaches `re` intact. The
stub's level list must include all five levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

**Try it:** paste `LINE_RE` into `uv run python` and test it on a line with a typo. What
does `fullmatch` return?

## 5. Counting with `Counter`

```python
from collections import Counter

levels = Counter(["INFO", "ERROR", "INFO", "ERROR", "ERROR"])
levels["ERROR"]            # 3
levels.most_common(1)      # [('ERROR', 3)]
dict(levels)               # {'INFO': 2, 'ERROR': 3}
```

`most_common(n)` breaks ties by first appearance, which is exactly what `top_errors`
asks for. For `busiest_hour`, the tie rule is "the earliest hour". Think about what
`min(hours, key=...)` with a tuple key would do.

## 6. Run it for real

```sh
uv run python organize.py ~/Downloads --dry-run
```

Read the plan before you run it without `--dry-run`. For the analyzer, make a log by
hand (copy the lines from `test_logstats.py`), or point it at a real one.

## 7. How it's checked

- **W4.4.a–b** (tutor checks): a dry run on a real folder, and a summary of a real log.
- **W4.4.c**: `/verify W4.4` runs both test files. Run them yourself with
  **Ctrl/Cmd+Shift+Enter** as you fill in each stub; watch the count of red tests drop.

## Pitfalls

- A pattern without `r"..."`: `"\d"` happens to work, but `"\b"` silently means backspace.
- `match` where you meant `fullmatch`: `"ERRORS"` would match `ERROR`.
- Moving files while iterating over `folder.iterdir()`. Plan first, then move, as the stubs do.
- Overwriting an existing file on a clash. `rename` replaces silently on Linux and macOS.
