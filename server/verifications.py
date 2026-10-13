"""Append-only verification log: progress/verifications.jsonl.

One JSON record per line (HANDOFF.md §5):
    {"item": "W1.3.c", "kind": "pytest", "passed": true, "summary": "6 passed",
     "at": "2026-10-12T21:20:00-04:00", "by": "claude-code|app"}

kind is "pytest", "quiz", "tutor" (a recorded tutor check for items with no
automated test) or "artifact" (a required file such as implementation_plan.md
exists). JSONL rather than a JSON array so appending never rewrites the file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from server.tracker import locked

Kind = Literal["pytest", "quiz", "tutor", "artifact"]


class Record(BaseModel):
    item: str
    kind: Kind
    passed: bool
    summary: str = ""
    at: str = ""
    by: str = "app"


class VerificationLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock_path = path.with_name(f".{path.name}.lock")

    def read(self) -> list[Record]:
        """All records, oldest first. Corrupt lines are skipped, not fatal."""
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        records = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                records.append(Record.model_validate_json(line))
            except ValueError:
                continue
        return records

    def append(self, record: Record) -> Record:
        if not record.at:
            record = record.model_copy(
                update={"at": datetime.now().astimezone().isoformat(timespec="seconds")})
        with locked(self.lock_path):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
        return record

    def passing_items(self) -> set[str]:
        return {r.item for r in self.read() if r.passed}

    def has_pass(self, item_id: str) -> bool:
        return item_id in self.passing_items()
