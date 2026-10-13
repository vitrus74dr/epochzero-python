"""W12.2.d (part): shortest paths, targeting, the mode timer, ghost states."""

import math

import pytest

from ghosts import (DOWN, LEFT, RIGHT, SCHEDULE, UP, ModeTimer, bfs_path, blinky_target,
                    choose_direction, clyde_target, distance2, ghost_points, inky_target,
                    next_state, pinky_target)

GRID = """
#########
#.......#
#.##.##.#
#.#...#.#
#.#.#.#.#
#...#...#
#########
"""
CELLS = {(c, r) for r, line in enumerate(GRID.strip().splitlines()) for c, ch in enumerate(line) if ch != "#"}


def neighbours(tile):
    c, r = tile
    return [n for n in ((c, r - 1), (c - 1, r), (c, r + 1), (c + 1, r)) if n in CELLS]


def options(tile):
    c, r = tile
    return [(d, (c + d[0], r + d[1])) for d in (UP, LEFT, DOWN, RIGHT) if (c + d[0], r + d[1]) in CELLS]


def test_bfs_shortest_path():
    path = bfs_path(neighbours, (1, 5), (7, 5))
    assert path[-1] == (7, 5) and (1, 5) not in path
    assert len(path) == 10                          # through the middle; (4,5) is a wall
    for a, b in zip([(1, 5)] + path, path):
        assert b in neighbours(a)                   # every step is a real move


def test_bfs_edge_cases():
    assert bfs_path(neighbours, (1, 1), (1, 1)) == []
    assert bfs_path(neighbours, (1, 1), (0, 0)) == []        # a wall: unreachable
    assert bfs_path(neighbours, (1, 1), (2, 1)) == [(2, 1)]


def test_distance2():
    assert distance2((0, 0), (3, 4)) == 25


def test_choose_never_reverses():
    # at (2,1) heading RIGHT the only options are LEFT (back) and RIGHT; the target is behind
    assert choose_direction(options((2, 1)), RIGHT, (0, 1)) == RIGHT


def test_choose_closest_and_ties():
    # at (4,1) heading RIGHT: options RIGHT (5,1) and DOWN (4,2); UP and LEFT excluded/blocked
    assert choose_direction(options((4, 1)), RIGHT, (4, 5)) == DOWN
    assert choose_direction(options((4, 1)), RIGHT, (9, 1)) == RIGHT
    # equal distances: UP beats LEFT beats DOWN beats RIGHT
    assert choose_direction([(DOWN, (5, 4)), (LEFT, (4, 3))], DOWN, (4, 4)) == LEFT


def test_dead_end_reverses():
    assert choose_direction([(UP, (3, 3))], DOWN, (3, 5)) == UP
    assert choose_direction([], DOWN, (0, 0)) is None


def test_targets():
    assert blinky_target((10, 5)) == (10, 5)
    assert pinky_target((10, 5), LEFT) == (6, 5)
    assert pinky_target((10, 5), UP) == (10, 1)
    assert inky_target((10, 10), RIGHT, (8, 14)) == (16, 6)     # pivot (12,10); 2*(12,10)-(8,14)
    assert clyde_target((0, 0), (20, 0), (0, 31)) == (20, 0)     # far: chase
    assert clyde_target((0, 0), (5, 5), (0, 31)) == (0, 31)      # near: retreat


def test_schedule_runs_in_order():
    t = ModeTimer()
    assert t.mode == "scatter"
    assert t.update(6.9) is False and t.mode == "scatter"
    assert t.update(0.2) is True and t.mode == "chase"
    assert t.update(20) is True and t.mode == "scatter"


def test_big_step_crosses_several_entries():
    t = ModeTimer([("scatter", 1), ("chase", 1), ("scatter", 1), ("chase", math.inf)])
    t.update(2.5)
    assert t.mode == "scatter" and t.elapsed == pytest.approx(0.5)


def test_last_chase_lasts_for_ever():
    t = ModeTimer()
    t.update(sum(s for _, s in SCHEDULE[:-1]) + 1)
    assert t.mode == "chase"
    assert t.update(10_000) is False and t.mode == "chase"


def test_frightened_pauses_the_schedule():
    t = ModeTimer()
    t.update(5)                                    # 5 s into the first scatter
    t.frighten(6)
    assert t.mode == "frightened"
    assert t.update(4) is False and t.mode == "frightened"
    t.frighten(6)                                  # a second power pellet restarts the clock
    assert t.update(5.5) is False
    assert t.update(1) is True and t.mode == "scatter"    # 0.5 s of fright, then 0.5 s of scatter
    assert t.elapsed == pytest.approx(5.5)                 # the schedule resumed where it paused
    assert t.update(1.4) is False                          # 6.9 s of scatter
    assert t.update(0.2) is True and t.mode == "chase"


def test_ghost_states():
    s = "house"
    for event, expected in [("power", "house"), ("release", "active"), ("caught", "active"),
                            ("power", "frightened"), ("power", "frightened"), ("caught", "eaten"),
                            ("timeout", "eaten"), ("home", "house")]:
        s = next_state(s, event)
        assert s == expected, (event, s)


def test_ghost_points():
    assert [ghost_points(n) for n in range(4)] == [200, 400, 800, 1600]
