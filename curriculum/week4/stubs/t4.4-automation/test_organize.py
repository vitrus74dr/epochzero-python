"""W4.4.c: the organizer, on throwaway folders from pytest's tmp_path."""

from pathlib import Path

import pytest

from organize import OTHER, apply_moves, category_for, main, plan_moves, unique_destination


def make(folder: Path, *names: str) -> None:
    for name in names:
        (folder / name).write_text(name, encoding="utf-8")


@pytest.mark.parametrize("name,category", [
    ("cat.jpg", "images"), ("CAT.JPG", "images"), ("notes.md", "documents"),
    ("song.mp3", "audio"), ("backup.tar", "archives"), ("app.py", "code"),
    ("README", OTHER), ("weird.xyz", OTHER),
])
def test_category_for(name, category):
    assert category_for(Path(name)) == category


def test_unique_destination(tmp_path):
    dest = tmp_path / "images" / "cat.jpg"
    assert unique_destination(dest, set()) == dest
    dest.parent.mkdir()
    dest.write_text("x")
    assert unique_destination(dest, set()).name == "cat (1).jpg"
    taken = {dest.with_name("cat (1).jpg")}
    assert unique_destination(dest, taken).name == "cat (2).jpg"


def test_plan_moves_only_top_level_files(tmp_path):
    make(tmp_path, "b.png", "a.txt", ".hidden")
    (tmp_path / "sub").mkdir()
    make(tmp_path / "sub", "inner.png")
    moves = plan_moves(tmp_path)
    assert [(s.name, d.relative_to(tmp_path).as_posix()) for s, d in moves] == [
        ("a.txt", "documents/a.txt"), ("b.png", "images/b.png")]


def test_plan_moves_resolves_clashes(tmp_path):
    (tmp_path / "images").mkdir()
    make(tmp_path / "images", "cat.jpg")
    make(tmp_path, "cat.jpg")
    [(src, dest)] = plan_moves(tmp_path)
    assert dest == tmp_path / "images" / "cat (1).jpg"


def test_apply_moves(tmp_path):
    make(tmp_path, "a.txt", "b.png", "c.zzz")
    apply_moves(plan_moves(tmp_path))
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()) == [
        "documents/a.txt", "images/b.png", "other/c.zzz"]
    assert (tmp_path / "documents" / "a.txt").read_text() == "a.txt"


def test_dry_run_moves_nothing(tmp_path, capsys):
    make(tmp_path, "a.txt", "b.png")
    assert main([str(tmp_path), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "a.txt -> documents/a.txt" in out and "b.png -> images/b.png" in out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.txt", "b.png"]


def test_main_moves(tmp_path):
    make(tmp_path, "a.txt")
    assert main([str(tmp_path)]) == 0
    assert (tmp_path / "documents" / "a.txt").exists()


def test_missing_folder(tmp_path, capsys):
    assert main([str(tmp_path / "nope")]) == 1
    captured = capsys.readouterr()
    assert "nope" in captured.out + captured.err, "say which folder is missing"
