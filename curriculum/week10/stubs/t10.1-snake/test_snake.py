"""W10.1.c: Snake's rules, the fixed tick and the high score."""

import random

import pytest

from snake import DOWN, LEFT, RIGHT, UP, SnakeGame, Ticker, load_high_score, save_high_score


def game(cols=20, rows=15, seed=1):
    return SnakeGame(cols, rows, random.Random(seed))


def test_start():
    g = game()
    assert list(g.body) == [(10, 7), (9, 7), (8, 7)]
    assert g.direction == RIGHT and g.alive and g.score == 0
    assert g.food is not None and g.food not in g.body


def test_moves_right_by_default():
    g = game()
    g.food = (0, 0)                      # out of the way
    assert g.step() == "moved"
    assert list(g.body) == [(11, 7), (10, 7), (9, 7)]


def test_turn_up_moves_up():
    g = game()
    g.food = (0, 0)
    g.turn(UP)
    g.step()
    assert g.body[0] == (10, 8) and g.direction == UP


def test_reverse_is_ignored():
    g = game()
    g.food = (0, 0)
    g.turn(LEFT)                          # straight back into yourself
    assert g.step() == "moved" and g.body[0] == (11, 7)


def test_two_quick_turns_both_count():
    g = game()
    g.food = (0, 0)
    g.turn(UP)
    g.turn(LEFT)                          # within the same tick: a U-turn over two ticks
    g.step()
    g.step()
    assert list(g.body)[:2] == [(9, 8), (10, 8)] and g.alive


def test_quick_reverse_via_queue_is_still_ignored():
    g = game()
    g.food = (0, 0)
    g.turn(UP)
    g.turn(DOWN)                          # reverse of the queued UP: ignored
    g.step()
    g.step()
    assert g.body[0] == (10, 9) and g.alive


def test_queue_limit():
    g = game()
    g.turn(UP)
    g.turn(LEFT)
    g.turn(DOWN)                          # third waiting turn: dropped
    assert len(g.turns) == 2


def test_eating_grows_and_scores():
    g = game()
    g.food = (11, 7)
    assert g.step() == "ate"
    assert len(g.body) == 4 and g.score == 1
    assert g.food is not None and g.food not in g.body
    g.food = (0, 0)
    g.step()
    assert len(g.body) == 4               # grew once, not forever


def test_wall_kills():
    g = game(cols=12, rows=5)
    g.food = (0, 0)
    results = [g.step() for _ in range(6)]
    assert results[-1] == "dead" and not g.alive
    assert g.step() == "dead"             # stays dead


def test_running_into_yourself_kills():
    g = game()
    g.food = (0, 0)
    # a hook: head (5,5), heading DOWN; turning RIGHT runs into (6,5), a body cell
    g.body = type(g.body)([(5, 5), (5, 6), (6, 6), (6, 5), (6, 4)])
    g.direction = DOWN
    g.turn(RIGHT)
    assert g.step() == "dead" and not g.alive


def test_following_your_own_tail_is_fine():
    g = game()
    g.food = (0, 0)
    g.body = type(g.body)([(5, 5), (5, 6), (6, 6), (6, 5)])   # a 2x2 square, head at (5,5)
    g.direction = DOWN
    g.turn(RIGHT)
    assert g.step() == "moved"            # into (6,5), the cell the tail is leaving
    assert g.alive


def test_food_placement_is_deterministic_and_free():
    a, b = game(seed=42), game(seed=42)
    assert a.food == b.food
    for _ in range(30):
        a.place_food()
        assert a.food not in a.body and 0 <= a.food[0] < 20 and 0 <= a.food[1] < 15


def test_full_board_is_a_win():
    g = SnakeGame(4, 1, random.Random(0))     # head (2,0), body (1,0) (0,0): one free cell
    assert g.food == (3, 0) and not g.won
    g.body.appendleft((3, 0))                 # now the snake fills the board
    g.place_food()
    assert g.won and g.food is None


@pytest.mark.parametrize("frames,expected", [([0.125], 1), ([0.05, 0.05, 0.05], 1), ([0.3], 2), ([0.01] * 12, 0)])
def test_ticker(frames, expected):
    t = Ticker(0.125)
    assert sum(t.update(dt) for dt in frames) == expected


def test_ticker_keeps_leftover_time():
    # powers of two are exact in binary floating point, so no rounding surprises here
    t = Ticker(0.125)
    assert t.update(0.3125) == 2
    assert t.update(0.0625) == 1              # 0.0625 left over + 0.0625


def test_high_score_round_trip(tmp_path):
    path = tmp_path / "high.json"
    save_high_score(path, 7)
    assert load_high_score(path) == 7
    (tmp_path / "broken.json").write_text("{nope")
    assert load_high_score(tmp_path / "broken.json") == 0
    assert load_high_score(tmp_path / "missing.json") == 0
