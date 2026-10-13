"""W9.1.a: Pong's rules, with no Arcade in sight. pong.py draws them.

Units: pixels and seconds. Arcade's origin is bottom-left, so y grows upward.
Every function here mutates the objects it's given (that's normal for game
state) and never reads a clock: time arrives as `dt`.
"""

import math
import random
from dataclasses import dataclass

BALL_SPEED = 420.0                  # px/s at serve
SPEEDUP = 1.05                      # each paddle hit is 5% faster
MAX_SPEED = 1400.0
MAX_BOUNCE_ANGLE = math.radians(60)  # hitting the paddle's very edge
WIN_SCORE = 7


@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 8.0


@dataclass
class Paddle:
    x: float                        # centre
    y: float                        # centre
    width: float = 14.0
    height: float = 90.0


def move_ball(ball: Ball, dt: float) -> None:
    """Advance the ball by its velocity for dt seconds."""
    pass  # stub


def bounce_walls(ball: Ball, height: float) -> bool:
    """If the ball has crossed the bottom (y=0) or top (y=height) wall, put it
    back inside (touching the wall), make vy point away from that wall, and
    return True. Otherwise return False."""
    pass  # stub


def paddle_hit(ball: Ball, paddle: Paddle) -> bool:
    """If the ball overlaps the paddle AND is moving toward it, bounce:

    - offset = (ball.y - paddle.y) / (paddle.height / 2), clamped to [-1, 1]
    - angle = offset * MAX_BOUNCE_ANGLE (centre: straight back; edge: steep)
    - new speed = min(current speed * SPEEDUP, MAX_SPEED)
    - vx points away from the paddle, vy = speed * sin(angle)
    - move the ball so it just touches the paddle's face (no overlap left)

    Return True if it bounced. A ball moving away from the paddle never
    bounces, even if it still overlaps (this stops a double bounce).
    """
    pass  # stub


def scored(ball: Ball, width: float) -> str | None:
    """"right" if the ball is completely past the left edge (the right
    player scores), "left" if completely past the right edge, else None."""
    pass  # stub


def serve(ball: Ball, width: float, height: float, toward: str, rng: random.Random) -> None:
    """Put the ball in the centre and launch it toward "left" or "right" at
    BALL_SPEED, at a random angle within ±30° of horizontal (from rng)."""
    pass  # stub


def winner(scores: dict[str, int]) -> str | None:
    """"left" or "right" once a side reaches WIN_SCORE, else None."""
    pass  # stub
