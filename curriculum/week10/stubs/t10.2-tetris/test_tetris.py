"""W10.2.d (part): rotation, kicks, locking, line clears, scoring, the bag.
Your tutor adds tests for your game loop and game-over handling."""

import random
from collections import Counter

import pytest

from tetris import (KINDS, SHAPES, Board, Piece, SevenBag, gravity_interval, hard_drop,
                    level_for, rotate_cell, score_for, shape_cells, spawn, try_move, try_rotate)


def test_rotate_cell_corners_clockwise():
    assert rotate_cell((0, 2), 3) == (2, 2)      # top-left -> top-right
    assert rotate_cell((2, 2), 3) == (2, 0)      # top-right -> bottom-right
    assert rotate_cell((1, 1), 3) == (1, 1)      # the centre stays put


@pytest.mark.parametrize("kind", KINDS)
def test_four_turns_is_the_identity(kind):
    assert shape_cells(kind, 4) == shape_cells(kind, 0) == sorted(SHAPES[kind][1])
    assert all(len(shape_cells(kind, r)) == 4 for r in range(4))


def test_t_rotations():
    assert shape_cells("T", 1) == [(1, 0), (1, 1), (1, 2), (2, 1)]   # nub points right
    assert shape_cells("T", 2) == [(0, 1), (1, 0), (1, 1), (2, 1)]   # nub points down
    assert shape_cells("T", -1) == shape_cells("T", 3)


def test_o_never_changes():
    assert shape_cells("O", 0) == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert all(shape_cells("O", r) == shape_cells("O", 0) for r in range(4))


def test_piece_cells():
    assert Piece("O", 0, 4, 0).cells() == [(4, 0), (4, 1), (5, 0), (5, 1)]


def test_board_rows_are_independent():
    b = Board()
    assert len(b.grid) == 20 and all(len(row) == 10 for row in b.grid)
    b.grid[0][0] = "I"
    assert b.grid[1][0] is None, "every row must be its own list ([[None]*w]*h aliases them)"


def test_spawn_and_fits():
    b = Board()
    p = spawn("T", b)
    assert (p.col, p.row) == (3, 17) and b.fits(p)
    assert spawn("I", b).col == 3 and spawn("O", b).col == 4
    assert not b.fits(Piece("O", 0, 9, 0))            # half off the right edge
    assert not b.fits(Piece("O", 0, 0, -1))           # through the floor
    b.lock(Piece("O", 0, 0, 0))
    assert not b.fits(Piece("O", 0, 1, 0))            # overlaps a locked block


def test_try_move():
    b = Board()
    p = Piece("O", 0, 0, 5)
    assert try_move(b, p, -1, 0) is None              # wall
    assert try_move(b, p, 1, -1) == Piece("O", 0, 1, 4)


def test_rotate_kicks_off_the_wall():
    b = Board()
    upright_i = Piece("I", 1, -2, 5)                  # rotation 1: vertical, in box column 2 -> board col 0
    assert upright_i.cells()[0][0] == 0 and b.fits(upright_i)
    flat = try_rotate(b, upright_i, -1)               # flat needs cols -2..1: kicked right
    assert flat is not None and b.fits(flat)
    assert min(c for c, _ in flat.cells()) == 0


def test_rotate_blocked_returns_none():
    b = Board(4, 3)
    for c in range(4):
        b.grid[1][c] = "X"
    assert try_rotate(b, Piece("I", 0, 0, -2), 1) is None


def test_hard_drop():
    b = Board()
    b.lock(Piece("O", 0, 4, 0))
    landed, rows = hard_drop(b, Piece("O", 0, 4, 10))
    assert landed == Piece("O", 0, 4, 2) and rows == 8


def test_clear_one_line_and_shift_down():
    b = Board(4, 4)
    b.grid[0] = ["I", "I", "I", "I"]
    b.grid[1] = ["J", None, None, None]
    assert b.clear_lines() == 1
    assert b.grid[0] == ["J", None, None, None]
    assert b.grid[3] == [None] * 4 and len(b.grid) == 4


def test_clear_multiple_non_adjacent_lines():
    b = Board(3, 5)
    b.grid[0] = ["I"] * 3
    b.grid[1] = ["T", None, "T"]
    b.grid[2] = ["L"] * 3
    b.grid[3] = [None, "S", None]
    assert b.clear_lines() == 2
    assert b.grid[0] == ["T", None, "T"] and b.grid[1] == [None, "S", None]
    assert all(row == [None] * 3 for row in b.grid[2:])


def test_scoring_and_levels():
    assert [score_for(n, 1) for n in range(5)] == [0, 100, 300, 500, 800]
    assert score_for(4, 3) == 2400
    assert [level_for(n) for n in (0, 9, 10, 25)] == [1, 1, 2, 3]
    assert gravity_interval(1) == pytest.approx(0.8)
    assert gravity_interval(2) == pytest.approx(0.68)
    assert gravity_interval(30) == pytest.approx(0.05)


def test_seven_bag():
    bag = SevenBag(random.Random(5))
    dealt = []
    for _ in range(70):
        nxt = bag.peek()
        dealt.append(bag.next())
        assert dealt[-1] == nxt
    for i in range(0, 70, 7):
        assert sorted(dealt[i:i + 7]) == sorted(KINDS)       # every 7 holds each kind once
    assert Counter(dealt) == {k: 10 for k in KINDS}
    other = SevenBag(random.Random(5))
    assert [other.next() for _ in range(14)] == dealt[:14]   # same seed, same order


def test_game_over_when_spawn_is_blocked():
    b = Board()
    assert b.fits(spawn("O", b)) is True
    b.lock(Piece("O", 0, 4, 18))
    assert not b.fits(spawn("O", b))
