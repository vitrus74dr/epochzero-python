"""W11.2.d (part): vector motion, wrap-around, splitting and bullet lifetime."""

import math
import random

import pytest

from space import (SIZES, Asteroid, Body, Bullet, age_bullets, apply_drag, clamp_speed,
                   collide, fire, heading_vector, move, split, thrust, wrap)


def speed(b):
    return math.hypot(b.vx, b.vy)


@pytest.mark.parametrize("heading,expected", [(0, (1, 0)), (90, (0, 1)), (180, (-1, 0)), (270, (0, -1)),
                                              (45, (math.sqrt(0.5), math.sqrt(0.5)))])
def test_heading_vector(heading, expected):
    assert heading_vector(heading) == pytest.approx(expected, abs=1e-9)


def test_thrust_and_inertia():
    ship = Body(0, 0)
    for _ in range(10):
        thrust(ship, 90, 300, 0.1)            # one second of thrust, upward
    assert (ship.vx, ship.vy) == pytest.approx((0, 300), abs=1e-9)
    move(ship, 2)                              # engines off: keeps going
    assert (ship.x, ship.y) == pytest.approx((0, 600), abs=1e-9)
    thrust(ship, 0, 100, 1)                    # a sideways push adds, it doesn't replace
    assert (ship.vx, ship.vy) == pytest.approx((100, 300), abs=1e-9)


def test_drag_and_clamp():
    b = Body(0, 0, 300, 400)
    apply_drag(b, 0.5, 0.1)
    assert (b.vx, b.vy) == pytest.approx((285, 380))
    clamp_speed(b, 100)
    assert speed(b) == pytest.approx(100) and b.vy / b.vx == pytest.approx(380 / 285)
    slow = Body(0, 0, 3, 4)
    clamp_speed(slow, 100)
    assert (slow.vx, slow.vy) == (3, 4)
    stop = Body(0, 0, 3, 4)
    apply_drag(stop, 50, 1)                    # huge drag: stops, never reverses
    assert (stop.vx, stop.vy) == (0, 0)


@pytest.mark.parametrize("start,expected", [
    ((-11, 300), (809, 300)), ((811, 300), (-9, 300)),
    ((400, -11), (400, 609)), ((400, 611), (400, -9)),
])
def test_wrap(start, expected):
    b = Body(*start, radius=10)
    wrap(b, 800, 600)
    assert (b.x, b.y) == pytest.approx(expected)
    wrap(b, 800, 600)
    assert (b.x, b.y) == pytest.approx(expected), "wrapping must not flip it straight back"


def test_no_wrap_while_partly_visible():
    b = Body(-9, 300, radius=10)
    wrap(b, 800, 600)
    assert b.x == -9
    b.x = -10.5
    wrap(b, 800, 600)
    assert b.x == pytest.approx(809.5)


def test_collide():
    assert collide(Body(0, 0, radius=10), Body(25, 0, radius=15))      # touching
    assert not collide(Body(0, 0, radius=10), Body(26, 0, radius=15))
    assert collide(Body(0, 0, radius=10), Body(10, 10, radius=5))


def test_split_sizes_and_motion():
    rng = random.Random(1)
    rock = Asteroid(100, 100, 50, 0, radius=SIZES["large"], size="large")
    kids = split(rock, rng)
    assert [k.size for k in kids] == ["medium", "medium"]
    assert all(k.radius == SIZES["medium"] and (k.x, k.y) == (100, 100) for k in kids)
    angles = sorted(math.degrees(math.atan2(k.vy, k.vx)) for k in kids)
    assert -45 <= angles[0] <= -20 and 20 <= angles[1] <= 45            # one each way
    assert all(speed(k) == pytest.approx(65) for k in kids)
    grandkids = split(kids[0], rng)
    assert [k.size for k in grandkids] == ["small", "small"]
    assert split(grandkids[0], rng) == []


def test_split_is_repeatable():
    rock = Asteroid(0, 0, 10, 10, size="large")
    a, b = split(rock, random.Random(3)), split(rock, random.Random(3))
    assert [(k.vx, k.vy) for k in a] == [(k.vx, k.vy) for k in b] != []


def test_bullets_expire():
    bullets = [Bullet(0, 0, lifetime=1.0), Bullet(0, 0, age=0.95, lifetime=1.0)]
    kept = age_bullets(bullets, 0.1)
    assert kept is not bullets and len(kept) == 1 and kept[0].age == pytest.approx(0.1)


def test_fire_from_the_nose_with_inherited_velocity():
    ship = Body(100, 100, 30, 0, radius=12)
    b = fire(ship, 90, speed=500)
    assert (b.x, b.y) == pytest.approx((100, 112))
    assert (b.vx, b.vy) == pytest.approx((30, 500))
