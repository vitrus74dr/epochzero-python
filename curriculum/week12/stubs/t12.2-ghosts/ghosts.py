"""W12.2: ghost brains. How ghosts move, look and interact with Pac-Man in
your game is your design; this module is the rules underneath.

Tiles are (col, row) in maze-text order (row 0 at the top, UP = (0, -1)),
as in maze.py. Nothing here imports the maze: functions take a `neighbours`
function or a list of options, so they work on any grid (and tests can use
tiny ones). With your Maze: neighbours=lambda t: [n for _, n in maze.neighbours(t)].
"""

import math
from collections import deque

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRECTIONS = [UP, LEFT, DOWN, RIGHT]          # the arcade's tie-break order

# Scatter targets: corners just outside the classic 28x31 maze.
SCATTER = {"blinky": (25, -3), "pinky": (2, -3), "inky": (27, 31), "clyde": (0, 31)}

# (mode, seconds); the last chase lasts for ever.
SCHEDULE = [("scatter", 7), ("chase", 20), ("scatter", 7), ("chase", 20),
            ("scatter", 5), ("chase", 20), ("scatter", 5), ("chase", math.inf)]


def bfs_path(neighbours, start, goal) -> list:
    """Shortest path from start to goal as a list of tiles, NOT including
    start but including goal. [] if start == goal or goal is unreachable.
    `neighbours(tile)` returns the tiles you can step to."""
    pass  # stub


def distance2(a, b) -> int:
    """Squared straight-line distance (no sqrt needed to compare distances)."""
    pass  # stub


def choose_direction(options, current, target):
    """The arcade ghost's choice at a tile. `options` is [(direction, tile), ...]
    for the open neighbours. Never reverse (the opposite of `current`) unless
    it's the only option. Pick the option whose tile is closest to `target`
    (distance2); break ties in DIRECTIONS order. None if there are no options."""
    pass  # stub


def blinky_target(pac):
    """Blinky (red) chases Pac-Man's tile directly."""
    pass  # stub


def pinky_target(pac, pac_dir):
    """Pinky (pink) aims 4 tiles ahead of Pac-Man, to cut him off."""
    pass  # stub


def inky_target(pac, pac_dir, blinky):
    """Inky (cyan): take the tile 2 ahead of Pac-Man; the target is that
    tile plus the vector from Blinky to it (i.e. 2 * pivot - blinky)."""
    pass  # stub


def clyde_target(clyde, pac, corner):
    """Clyde (orange) chases like Blinky while more than 8 tiles away
    (distance2 > 64), and heads for his scatter corner when closer."""
    pass  # stub


class ModeTimer:
    """Scatter/chase schedule, paused while the ghosts are frightened.

    t = ModeTimer()
    t.mode -> "scatter" | "chase" | "frightened"
    t.update(dt) -> True if the mode changed during this update (ghosts reverse)
    t.frighten(6) -> frightened for 6 s (restarting if already frightened);
                     the schedule resumes afterwards exactly where it paused
    """

    def __init__(self, schedule=SCHEDULE):
        self.schedule = schedule
        self.index = 0              # current entry in the schedule
        self.elapsed = 0.0          # seconds spent in that entry
        self.frightened_left = 0.0

    @property
    def mode(self) -> str:
        pass  # stub

    def update(self, dt: float) -> bool:
        pass  # stub

    def frighten(self, seconds: float) -> None:
        pass  # stub


# A single ghost's life: house -> active <-> frightened -> eaten -> house
TRANSITIONS = {
    ("house", "release"): "active",
    ("active", "power"): "frightened",
    ("frightened", "power"): "frightened",
    ("frightened", "timeout"): "active",
    ("frightened", "caught"): "eaten",        # Pac-Man ate the ghost
    ("eaten", "home"): "house",               # the eyes got back to the house
}


def next_state(state: str, event: str) -> str:
    """The new state after `event`; events with no entry change nothing.
    (An active ghost catching Pac-Man costs a life: that's the game's job.)"""
    pass  # stub


def ghost_points(eaten_so_far: int) -> int:
    """Points for eating a ghost during one power pellet: 200 for the
    first, then 400, 800, 1600 (eaten_so_far = ghosts already eaten)."""
    pass  # stub
