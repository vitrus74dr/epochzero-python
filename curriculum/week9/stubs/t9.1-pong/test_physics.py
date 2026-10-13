"""W9.1.c: Pong's rules without opening a window."""

import math
import random

import pytest

from physics import (BALL_SPEED, MAX_BOUNCE_ANGLE, MAX_SPEED, SPEEDUP, WIN_SCORE, Ball,
                     Paddle, bounce_walls, move_ball, paddle_hit, scored, serve, winner)


def speed(b):
    return math.hypot(b.vx, b.vy)


def test_move_is_frame_rate_independent():
    one, many = Ball(0, 0, 300, -120), Ball(0, 0, 300, -120)
    move_ball(one, 0.5)
    for _ in range(30):
        move_ball(many, 0.5 / 30)
    assert (one.x, one.y) == pytest.approx((150, -60))
    assert (many.x, many.y) == pytest.approx((one.x, one.y))


@pytest.mark.parametrize("y,vy,new_y_check,new_vy_sign", [
    (-3, -200, lambda y, r: y == pytest.approx(r), 1),          # through the floor
    (603, 200, lambda y, r: y == pytest.approx(600 - r), -1),   # through the ceiling
])
def test_bounce_walls(y, vy, new_y_check, new_vy_sign):
    b = Ball(100, y, 300, vy)
    assert bounce_walls(b, 600) is True
    assert new_y_check(b.y, b.radius)
    assert b.vy * new_vy_sign > 0 and abs(b.vy) == 200 and b.vx == 300


def test_no_wall_bounce_in_the_middle():
    b = Ball(100, 300, 300, 200)
    assert bounce_walls(b, 600) is False and b.vy == 200


def test_centre_hit_goes_straight_back_faster():
    p = Paddle(30, 300)
    b = Ball(p.x + p.width / 2 + 2, 300, -400, 0)          # overlapping the right face
    assert paddle_hit(b, p) is True
    assert b.vx > 0 and b.vy == pytest.approx(0, abs=1e-9)
    assert speed(b) == pytest.approx(400 * SPEEDUP)
    assert b.x - b.radius >= p.x + p.width / 2 - 1e-9      # pushed out of the paddle


@pytest.mark.parametrize("dy,sign", [(45, 1), (-45, -1), (50, 1)])   # 50: past the edge, clamped
def test_edge_hits_bounce_steeply(dy, sign):
    p = Paddle(770, 300)
    b = Ball(p.x - p.width / 2 - 2, 300 + dy, 400, 0)
    assert paddle_hit(b, p) is True
    assert b.vx < 0                                         # away from the right paddle
    angle = math.atan2(b.vy, -b.vx)
    assert angle == pytest.approx(sign * MAX_BOUNCE_ANGLE)  # clamped at the edge


def test_half_way_up_is_half_the_angle():
    p = Paddle(30, 300)
    b = Ball(p.x + p.width / 2 + 2, 300 + p.height / 4, -400, 0)
    paddle_hit(b, p)
    assert math.atan2(b.vy, b.vx) == pytest.approx(MAX_BOUNCE_ANGLE / 2)


def test_moving_away_never_bounces():
    p = Paddle(30, 300)
    b = Ball(p.x + p.width / 2 + 2, 300, +400, 0)
    assert paddle_hit(b, p) is False and b.vx == 400


def test_miss():
    p = Paddle(30, 300)
    assert paddle_hit(Ball(p.x + 2, 500, -400, 0), p) is False


def test_speed_is_capped():
    p = Paddle(30, 300)
    b = Ball(p.x + p.width / 2 + 2, 300, -MAX_SPEED, 0)
    assert paddle_hit(b, p) is True and b.vx > 0
    assert speed(b) == pytest.approx(MAX_SPEED)


def test_scored():
    # completely past an edge scores; touching it doesn't yet
    assert [scored(Ball(x, 300), 800) for x in (-9, -7, 400, 807, 809)] == [
        "right", None, None, None, "left"]


@pytest.mark.parametrize("toward,sign", [("left", -1), ("right", 1)])
def test_serve(toward, sign):
    rng = random.Random(3)
    for _ in range(50):
        b = Ball(5, 5, 0, 0)
        serve(b, 800, 600, toward, rng)
        assert (b.x, b.y) == (400, 300)
        assert speed(b) == pytest.approx(BALL_SPEED)
        assert b.vx * sign > 0
        assert abs(math.atan2(b.vy, abs(b.vx))) <= math.radians(30) + 1e-9


def test_serve_uses_the_injected_rng():
    a, b = Ball(0, 0), Ball(0, 0)
    serve(a, 800, 600, "left", random.Random(7))
    serve(b, 800, 600, "left", random.Random(7))
    assert speed(a) > 0 and (a.vx, a.vy) == (b.vx, b.vy)
    c = Ball(0, 0)
    serve(c, 800, 600, "left", random.Random(8))
    assert (c.vx, c.vy) != (a.vx, a.vy), "the angle should come from rng"


def test_winner():
    assert winner({"left": 0, "right": 0}) is None
    assert winner({"left": WIN_SCORE - 1, "right": 3}) is None
    assert winner({"left": 2, "right": WIN_SCORE}) == "right"
