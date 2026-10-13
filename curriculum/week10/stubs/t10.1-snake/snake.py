"""W10.1.a: Snake's rules on a grid. No Arcade: snake_game.py draws them.

Coordinates are (col, row) grid cells with (0, 0) at the BOTTOM-left, like
Arcade, so UP is (0, +1). The board has no wrap-around: walls kill.
"""

import json
import random
from collections import deque
from pathlib import Path

UP, DOWN, LEFT, RIGHT = (0, 1), (0, -1), (-1, 0), (1, 0)
MAX_QUEUED_TURNS = 2


class SnakeGame:
    """
    snake = SnakeGame(cols=20, rows=15, rng=random.Random(1))

    - starts with length 3 at the centre (cols // 2, rows // 2), heading RIGHT;
      body[0] is the head, the other two cells trail to its left
    - food is placed with rng on a free cell (never on the snake)
    - alive is True, score is 0, won is False
    """

    def __init__(self, cols: int, rows: int, rng: random.Random):
        self.cols, self.rows, self.rng = cols, rows, rng
        self.body: deque[tuple[int, int]] = deque()
        self.direction = RIGHT
        self.turns: deque[tuple[int, int]] = deque()
        self.food: tuple[int, int] | None = None
        self.alive = True
        self.won = False
        self.score = 0
        # TODO: build the starting body, then place the food

    def turn(self, direction: tuple[int, int]) -> None:
        """Queue a turn for the coming ticks (so two quick key presses in one
        tick both count). Ignore it if it's the same as, or the exact reverse
        of, the last queued direction (or the current one if none is queued),
        or if MAX_QUEUED_TURNS are already waiting."""
        pass  # stub

    def step(self) -> str:
        """One tick. Take the next queued turn (if any), move the head one cell.
        Return "dead" if it hit a wall or the body (moving into the cell the
        tail is just leaving is fine), "ate" if it reached the food (the snake
        grows by one: the tail stays; score +1; new food), else "moved".
        A dead snake doesn't move: step() keeps returning "dead".
        If there's no free cell left for food, set won = True."""
        pass  # stub

    def place_food(self) -> None:
        """Food on a random free cell (rng.choice over the free cells, in
        (col, row) order), or None, with won = True, if the board is full."""
        pass  # stub


class Ticker:
    """Turns variable frame times into a fixed number of game ticks.

    t = Ticker(interval=0.125)     # 8 moves a second
    t.update(dt) -> how many ticks to run this frame (0, 1, 2, ...)
    Leftover time carries over to the next frame.
    """

    def __init__(self, interval: float):
        self.interval = interval
        self.acc = 0.0

    def update(self, dt: float) -> int:
        pass  # stub


def load_high_score(path: Path) -> int:
    """The saved high score, or 0 if the file is missing or not valid JSON."""
    pass  # stub


def save_high_score(path: Path, score: int) -> None:
    """Write {"high_score": score} as JSON (utf-8)."""
    pass  # stub
