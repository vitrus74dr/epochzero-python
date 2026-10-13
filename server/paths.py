from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def tracker(self) -> Path:
        return self.root / "CURRICULUM_TRACKER.md"

    @property
    def tracker_lock(self) -> Path:
        return self.root / "progress" / ".tracker.lock"

    @property
    def progress(self) -> Path:
        return self.root / "progress"

    @property
    def verifications(self) -> Path:
        return self.progress / "verifications.jsonl"

    @property
    def workspace(self) -> Path:
        return self.root / "workspace"
