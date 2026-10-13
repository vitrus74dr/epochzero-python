"""W6.3.d: the level loader. (The tutor adds an asset-path test for your game.)"""

import pytest

from levels import TILE, LevelError, level_files, parse_level, tile_to_pixel

MINI = """
..F
C.E
P##
"""


def test_parse_positions():
    lv = parse_level(MINI)
    assert (lv.rows, lv.cols) == (3, 3)
    assert lv.player == (0, 2)
    assert lv.walls == [(1, 2), (2, 2)]
    assert lv.coins == [(0, 1)] and lv.enemies == [(2, 1)] and lv.flags == [(2, 0)]


def test_trailing_spaces_and_blank_edges_ignored():
    assert parse_level("\n\n..F   \nP##\n\n").cols == 3


@pytest.mark.parametrize("text,words", [
    ("..F\nP#\n", ["row 2"]),            # ragged
    ("..F\nP?#\n", ["?", "row 2", "col 2"]),
    ("..F\n.##\n", ["P"]),               # no player
    ("P.F\nP##\n", ["P"]),               # two players
    ("P..\n###\n", ["F"]),               # no flag
])
def test_bad_levels(text, words):
    with pytest.raises(LevelError) as err:
        parse_level(text)
    for w in words:
        assert w in str(err.value)


def test_tile_to_pixel():
    assert tile_to_pixel(0, 2, rows=3) == (TILE / 2, TILE / 2)            # bottom-left
    assert tile_to_pixel(0, 0, rows=3) == (TILE / 2, 2 * TILE + TILE / 2)  # top-left
    assert tile_to_pixel(4, 1, rows=3, tile=10) == (45, 15)


def test_shipped_levels_load():
    files = level_files()
    assert [f.name for f in files][:2] == ["level1.txt", "level2.txt"]
    for f in files:
        lv = parse_level(f.read_text(encoding="utf-8"))
        assert lv.flags and lv.walls


def test_level_files_sort_numerically(tmp_path, monkeypatch):
    import levels
    for n in (1, 2, 10):
        (tmp_path / f"level{n}.txt").write_text("P.F\n###\n")
    monkeypatch.setattr(levels, "LEVEL_DIR", tmp_path)
    assert [f.name for f in levels.level_files()] == ["level1.txt", "level2.txt", "level10.txt"]
