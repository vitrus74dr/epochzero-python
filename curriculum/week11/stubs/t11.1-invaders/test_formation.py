"""W11.1.c: the march, edge turns, speed-up and waves."""

import pytest

from formation import (BASE_INTERVAL, COLS, MIN_INTERVAL, ROWS, SPACING_X, SPACING_Y, STEP_DOWN,
                       STEP_X, Formation)


def test_start():
    f = Formation()
    assert len(f.alive) == COLS * ROWS == 55
    assert f.position((0, 0)) == (80, 360)
    assert f.position((2, 1)) == (80 + 2 * SPACING_X, 360 + SPACING_Y)
    assert f.edges() == (80, 80 + 10 * SPACING_X)


def test_march_sideways():
    f = Formation()
    f.march()
    assert (f.left, f.bottom, f.direction) == (80 + STEP_X, 360, 1)


def test_edge_turns_down_and_back():
    f = Formation()
    for _ in range(100):                    # bounded: a march() that never turns fails, not hangs
        if f.direction != 1:
            break
        f.march()
    assert f.direction == -1, "the formation never turned at the right edge"
    right = f.edges()[1]
    assert right <= 800 - 24 and right + STEP_X > 800 - 24      # stopped just short of the margin
    assert f.bottom == 360 - STEP_DOWN                           # the turn step moved down only
    left_before = f.left
    f.march()
    assert f.left == left_before - STEP_X and f.bottom == 360 - STEP_DOWN


def test_left_edge_turns_too():
    f = Formation(left=30)                  # one step left would reach x=18, inside the 24px margin
    f.direction = -1
    f.march()
    assert f.direction == 1 and f.bottom == 360 - STEP_DOWN and f.left == 30


def test_edges_follow_the_survivors():
    f = Formation()
    for row in range(ROWS):
        f.kill((COLS - 1, row))                  # the whole right column dies
    assert f.edges() == (80, 80 + 9 * SPACING_X)


def test_speeds_up_as_they_die():
    f = Formation()
    assert f.interval() == pytest.approx(BASE_INTERVAL)
    slots = sorted(f.alive)
    for s in slots[:44]:
        f.kill(s)
    assert f.interval() == pytest.approx(BASE_INTERVAL * 11 / 55)
    for s in slots[44:54]:
        f.kill(s)
    assert f.interval() == pytest.approx(max(MIN_INTERVAL, BASE_INTERVAL / 55))


def test_kill_twice_is_harmless():
    f = Formation()
    f.kill((3, 2))
    f.kill((3, 2))
    assert len(f.alive) == 54


def test_shooters_are_the_lowest_per_column():
    f = Formation()
    f.kill((0, 0))
    f.kill((0, 1))
    for row in range(ROWS):
        f.kill((5, row))
    shooters = f.shooters()
    assert shooters[0] == (0, 2) and (5, 0) not in shooters
    assert len(shooters) == 10 and shooters == sorted(shooters)


def test_lowest_y_and_cleared():
    f = Formation()
    assert f.lowest_y() == 360
    for s in list(f.alive):
        f.kill(s)
    assert f.lowest_y() is None


def test_waves_start_lower_but_not_forever():
    f = Formation()
    f.kill((0, 0))
    f.march()
    f.next_wave()
    assert len(f.alive) == 55 and f.direction == 1
    assert (f.left, f.bottom) == (80, 360 - STEP_DOWN)
    for _ in range(10):
        f.next_wave()
    assert f.bottom == 360 - 4 * STEP_DOWN
