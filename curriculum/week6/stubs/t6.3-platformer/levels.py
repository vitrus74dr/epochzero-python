"""W6.3: load platformer levels from text files.

The format is a contract (lesson 6.3, section 1): one character per tile,
first line = top row.

    #  wall      C  coin      E  enemy      F  goal flag
    P  player start (exactly one)           .  empty

Everything else about the game is yours to design.
"""

from dataclasses import dataclass, field
from pathlib import Path

TILE = 64
LEVEL_DIR = Path(__file__).parent / "levels"
KINDS = {"#": "walls", "C": "coins", "E": "enemies", "F": "flags", "P": "player"}


class LevelError(ValueError):
    """The level text is malformed."""


@dataclass
class Level:
    rows: int
    cols: int
    walls: list[tuple[int, int]] = field(default_factory=list)    # (col, row) grid cells,
    coins: list[tuple[int, int]] = field(default_factory=list)    # row 0 = top line,
    enemies: list[tuple[int, int]] = field(default_factory=list)  # in reading order
    flags: list[tuple[int, int]] = field(default_factory=list)
    player: tuple[int, int] = (0, 0)


def parse_level(text: str) -> Level:
    """Parse level text into a Level.

    - Blank lines at the start and end are ignored; trailing spaces too.
    - Every row must be the same width -> otherwise LevelError naming the row.
    - Unknown characters -> LevelError naming the character, row and column.
    - Exactly one P -> otherwise LevelError.
    - At least one F -> otherwise LevelError.
    """
    pass  # stub


def tile_to_pixel(col: int, row: int, rows: int, tile: int = TILE) -> tuple[float, float]:
    """Pixel centre of a grid cell; row 0 (the top text line) is the highest on screen."""
    pass  # stub


def level_files() -> list[Path]:
    """levels/level*.txt next to this file, in order (level1, level2, ..., level10)."""
    pass  # stub
