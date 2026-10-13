"""W4.4.b: summarize a log file.

Each line looks like:

    2026-10-13 14:02:11 ERROR [db] connection refused

date, time, level (DEBUG|INFO|WARNING|ERROR|CRITICAL), [source], message.
Blank lines are ignored; other lines that don't match are counted as
skipped, never a crash.

    uv run python logstats.py app.log
"""

import argparse
import re
from collections import Counter
from pathlib import Path

# TODO: one regular expression with named groups: date, hour, level, source, message.
LINE_RE = re.compile(r"")


def parse_line(line: str) -> dict | None:
    """{"date": "2026-10-13", "hour": 14, "level": "ERROR", "source": "db",
    "message": "connection refused"} for a matching line (hour is an int),
    or None if the line doesn't match. Surrounding whitespace is ignored."""
    pass  # stub


def summarize(lines) -> dict:
    """Summary of an iterable of lines:
    {"levels": {"INFO": 3, "ERROR": 2, ...},       # only levels that occur
     "top_errors": [("connection refused", 2), ...],  # ERROR and CRITICAL messages,
                                                      # most common first, at most 3;
                                                      # ties in first-seen order
     "busiest_hour": 14,                            # hour with most lines; None if no lines parsed;
                                                    # ties -> the earliest hour
     "parsed": 5, "skipped": 1}"""
    pass  # stub


def main(argv: list[str] | None = None) -> int:
    """Print the summary of the log file named on the command line."""
    pass  # stub


if __name__ == "__main__":
    raise SystemExit(main())
