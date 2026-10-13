"""W11.2: the physics of Asteroids. The game around it is your design.

Headings are MATHS angles in degrees: 0 = pointing right, 90 = up,
counter-clockwise positive. (Arcade's sprite.angle turns CLOCKWISE; for a
ship image that points up, sprite.angle = 90 - heading. See lesson 11.2.)
Pixels and seconds, y up.
"""

import math
import random
from dataclasses import dataclass

SIZES = {"large": 40.0, "medium": 22.0, "small": 12.0}      # radius
NEXT_SIZE = {"large": "medium", "medium": "small", "small": None}
POINTS = {"large": 20, "medium": 50, "small": 100}


@dataclass
class Body:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 10.0


@dataclass
class Asteroid(Body):
    size: str = "large"


@dataclass
class Bullet(Body):
    age: float = 0.0
    lifetime: float = 1.0


def heading_vector(heading: float) -> tuple[float, float]:
    """Unit vector (dx, dy) for a heading in degrees."""
    pass  # stub


def thrust(body: Body, heading: float, accel: float, dt: float) -> None:
    """Add accel * dt to the velocity, in the heading's direction. No thrust,
    no change: velocity persists (inertia)."""
    pass  # stub


def apply_drag(body: Body, drag: float, dt: float) -> None:
    """Scale velocity by max(0, 1 - drag * dt): a gentle slow-down."""
    pass  # stub


def clamp_speed(body: Body, max_speed: float) -> None:
    """If faster than max_speed, scale the velocity down to exactly max_speed,
    keeping its direction."""
    pass  # stub


def move(body: Body, dt: float) -> None:
    pass  # stub


def wrap(body: Body, width: float, height: float) -> None:
    """Leave one edge, come back at the opposite one. A body counts as gone
    only once it's completely off screen (centre more than its radius beyond
    the edge). Then shift it by width + 2 * radius (or height + 2 * radius),
    so it reappears just off the opposite edge and slides back in.
    E.g. width 800, radius 10: x = -11 -> x = 809.
    (Shifting by only `width` would leave it past the far threshold, and it
    would flicker between the two edges.)"""
    pass  # stub


def collide(a: Body, b: Body) -> bool:
    """Circles touch or overlap: centre distance <= sum of radii."""
    pass  # stub


def split(rock: Asteroid, rng: random.Random) -> list[Asteroid]:
    """Two asteroids of the next size down at the rock's position (none for
    a small rock). Each child's velocity is the parent's, rotated by a random
    angle between 20 and 45 degrees (one child each way), and 1.3x faster."""
    pass  # stub


def age_bullets(bullets: list[Bullet], dt: float) -> list[Bullet]:
    """Age every bullet by dt and return a NEW list of those still younger
    than their lifetime."""
    pass  # stub


def fire(ship: Body, heading: float, speed: float = 500.0) -> Bullet:
    """A bullet at the ship's nose (centre + radius along the heading),
    moving at the ship's velocity plus `speed` along the heading."""
    pass  # stub
