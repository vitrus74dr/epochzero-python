"""W4.4.a: sort a folder's files into subfolders by type.

    uv run python organize.py ~/Downloads --dry-run
    uv run python organize.py ~/Downloads

Only files directly inside the folder move; subfolders and hidden files
(names starting with ".") are left alone.
"""

import argparse
from pathlib import Path

CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".txt", ".md", ".docx", ".odt", ".csv", ".xlsx"},
    "audio": {".mp3", ".wav", ".flac", ".ogg"},
    "video": {".mp4", ".mkv", ".mov", ".webm"},
    "archives": {".zip", ".tar", ".gz", ".7z"},
    "code": {".py", ".js", ".html", ".css", ".json"},
}
OTHER = "other"


def category_for(path: Path) -> str:
    """The category name for a file, by suffix, ignoring case
    ("photo.JPG" -> "images"). Unknown or missing suffix -> OTHER."""
    pass  # stub


def unique_destination(dest: Path, taken: set[Path]) -> Path:
    """dest itself if it doesn't exist and isn't in `taken`; otherwise the
    first free name of the form "stem (1).suffix", "stem (2).suffix", ...
    (`taken` holds destinations already planned in this run.)"""
    pass  # stub


def plan_moves(folder: Path) -> list[tuple[Path, Path]]:
    """(source, destination) for every file directly inside `folder`,
    sorted by source name. destination = folder / category / name, made
    unique with unique_destination(). Nothing is moved."""
    pass  # stub


def apply_moves(moves: list[tuple[Path, Path]]) -> None:
    """Create the category folders as needed and move each file."""
    pass  # stub


def main(argv: list[str] | None = None) -> int:
    """Parse arguments (a folder, and --dry-run), print one line per move as
    "name -> category/newname", then move the files unless --dry-run.
    Return 0, or 1 (with a message) if the folder doesn't exist."""
    parser = argparse.ArgumentParser(description="Sort files into folders by type.")
    # TODO: add a positional `folder` argument (type=Path) and a --dry-run flag
    pass  # stub


if __name__ == "__main__":
    raise SystemExit(main())
