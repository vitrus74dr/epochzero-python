"""W9.2: the fiddly core of Breakout. The game around it is your design.

Rectangles are (left, bottom, right, top) tuples in pixels, y up.
"""

from dataclasses import dataclass

LEVEL_1 = """
3333333333
2222222222
1111111111
1111111111
"""

LEVEL_2 = """
3.3.3.3.3.
.2.2.2.2.2
1111111111
..111111..
"""


@dataclass
class Brick:
    col: int
    row: int          # 0 = the top line of the layout
    hits: int         # hits left before it breaks (1-3)


def parse_layout(text: str) -> list[Brick]:
    """One Brick per digit 1-3 ("." is a gap), in reading order. Blank lines
    at the start and end are ignored. Any other character -> ValueError."""
    pass  # stub


def hit_side(x: float, y: float, radius: float, rect: tuple[float, float, float, float]) -> str | None:
    """Which side of `rect` a ball centred at (x, y) has hit: "left", "right",
    "top" or "bottom", or None if the ball doesn't overlap the rect.

    The side is the one with the SMALLEST penetration depth: e.g. a ball that
    has pushed 2 px in through the bottom edge but 9 px past the left edge
    hit the bottom. On an exact tie, prefer "top"/"bottom"."""
    pass  # stub


def bounce(vx: float, vy: float, side: str) -> tuple[float, float]:
    """New velocity after hitting `side` of something: pointing away from it
    ("left" -> vx negative, "top" -> vy positive, ...), speed unchanged."""
    pass  # stub


def damage(bricks: list[Brick], brick: Brick) -> bool:
    """One hit on `brick`: take a hit off it, and remove it from `bricks` when
    none are left. Return True if it broke."""
    pass  # stub


def level_cleared(bricks: list[Brick]) -> bool:
    pass  # stub
