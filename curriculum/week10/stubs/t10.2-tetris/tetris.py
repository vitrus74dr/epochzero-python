"""W10.2: Tetris's rules. The game loop, controls and drawing are your design.

Coordinates are (col, row) with row 0 at the BOTTOM of the board (y up, like
Arcade). A piece is a shape inside a small n×n box; the box's bottom-left
corner sits at (piece.col, piece.row) on the board.
"""

import random
from dataclasses import dataclass, replace

WIDTH, HEIGHT = 10, 20
KINDS = "IOTSZJL"

# Each shape at rotation 0: (box size n, cells in box coordinates, row 0 at the bottom).
SHAPES = {
    "I": (4, [(0, 2), (1, 2), (2, 2), (3, 2)]),
    "O": (2, [(0, 0), (1, 0), (0, 1), (1, 1)]),
    "T": (3, [(0, 1), (1, 1), (2, 1), (1, 2)]),
    "S": (3, [(0, 1), (1, 1), (1, 2), (2, 2)]),
    "Z": (3, [(0, 2), (1, 2), (1, 1), (2, 1)]),
    "J": (3, [(0, 2), (0, 1), (1, 1), (2, 1)]),
    "L": (3, [(2, 2), (0, 1), (1, 1), (2, 1)]),
}
# Tried in order when a rotation doesn't fit where it is: (d_col, d_row).
KICKS = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, 1)]
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}


def rotate_cell(cell: tuple[int, int], n: int) -> tuple[int, int]:
    """Rotate one box cell a quarter turn CLOCKWISE inside an n×n box.
    With row 0 at the bottom: the top-left corner (0, n-1) goes to the
    top-right (n-1, n-1). Hint: (c, r) -> (r, n - 1 - c)."""
    pass  # stub


def shape_cells(kind: str, rotation: int) -> list[tuple[int, int]]:
    """The box cells of `kind` after `rotation` clockwise quarter turns
    (rotation is taken mod 4), sorted."""
    pass  # stub


@dataclass(frozen=True)
class Piece:
    kind: str
    rotation: int = 0
    col: int = 0
    row: int = 0

    def cells(self) -> list[tuple[int, int]]:
        """Board cells this piece covers, sorted."""
        pass  # stub


class Board:
    """board.grid[row][col] is None (empty) or the kind that locked there.
    Row 0 is the bottom row."""

    def __init__(self, width: int = WIDTH, height: int = HEIGHT):
        self.width, self.height = width, height
        self.grid: list[list[str | None]] = []  # TODO: height rows of width Nones (beware aliasing!)

    def fits(self, piece: Piece) -> bool:
        """Every cell inside the board (0 <= col < width, 0 <= row < height)
        and empty."""
        pass  # stub

    def lock(self, piece: Piece) -> None:
        """Write the piece's kind into its cells."""
        pass  # stub

    def clear_lines(self) -> int:
        """Remove every full row; rows above drop down; new empty rows appear
        at the top. Return how many rows were cleared."""
        pass  # stub


def spawn(kind: str, board: Board) -> Piece:
    """A new piece at rotation 0, horizontally centred (col = (width - n) // 2)
    with its box touching the top (row = height - n)."""
    pass  # stub


def try_move(board: Board, piece: Piece, d_col: int, d_row: int) -> Piece | None:
    """The moved piece if it fits, else None."""
    pass  # stub


def try_rotate(board: Board, piece: Piece, turns: int = 1) -> Piece | None:
    """Rotate by `turns` quarter turns (1 = clockwise, -1 = anticlockwise),
    trying each offset in KICKS in order; return the first that fits, else None."""
    pass  # stub


def hard_drop(board: Board, piece: Piece) -> tuple[Piece, int]:
    """Move the piece straight down as far as it fits. Return (piece, rows dropped)."""
    pass  # stub


def score_for(lines: int, level: int) -> int:
    """LINE_SCORES[lines] * level; 0 lines -> 0."""
    pass  # stub


def level_for(total_lines: int) -> int:
    """Level 1 for 0-9 lines cleared, 2 for 10-19, and so on."""
    pass  # stub


def gravity_interval(level: int) -> float:
    """Seconds between automatic drops: 0.8 * 0.85 ** (level - 1), never below 0.05."""
    pass  # stub


class SevenBag:
    """The modern Tetris randomizer: shuffle all 7 kinds into a bag, deal
    them out, refill when empty. Never more than 12 pieces between two of the
    same kind, and no long droughts of I pieces."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.bag: list[str] = []

    def next(self) -> str:
        """Deal the next kind."""
        pass  # stub

    def peek(self) -> str:
        """The kind next() will return, without dealing it (for the preview)."""
        pass  # stub
