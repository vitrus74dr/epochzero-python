"""W11.1.a: the Space Invaders formation, as pure logic. invaders.py draws it.

Pixels, y up (Arcade). An invader is identified by its grid slot (col, row);
row 0 is the BOTTOM row of the formation. Its pixel position is

    x = left + col * SPACING_X        y = bottom + row * SPACING_Y

where (left, bottom) is the formation's current offset.
"""

COLS, ROWS = 11, 5
SPACING_X, SPACING_Y = 48, 40
STEP_X = 12                 # pixels per march step, sideways
STEP_DOWN = 24              # pixels down when the formation reaches an edge
BASE_INTERVAL = 0.8         # seconds between steps with every invader alive
MIN_INTERVAL = 0.05


class Formation:
    def __init__(self, screen_width: float = 800, margin: float = 24,
                 left: float = 80, bottom: float = 360):
        self.screen_width, self.margin = screen_width, margin
        self.start_left, self.start_bottom = left, bottom
        self.left, self.bottom = left, bottom
        self.direction = 1                      # +1 right, -1 left
        self.alive: set[tuple[int, int]] = set()
        self.wave = 0
        # TODO: fill `alive` with every (col, row) slot

    def position(self, slot: tuple[int, int]) -> tuple[float, float]:
        pass  # stub

    def edges(self) -> tuple[float, float]:
        """(leftmost x, rightmost x) of the invaders still alive."""
        pass  # stub

    def interval(self) -> float:
        """Seconds between march steps: BASE_INTERVAL scaled by the fraction
        still alive (all alive -> BASE_INTERVAL), never below MIN_INTERVAL."""
        pass  # stub

    def march(self) -> None:
        """One step. If moving STEP_X in the current direction would put an
        alive invader within `margin` of either screen edge (x < margin or
        x > screen_width - margin), instead move DOWN by STEP_DOWN and reverse
        direction (no sideways move on that step). Otherwise move sideways."""
        pass  # stub

    def kill(self, slot: tuple[int, int]) -> None:
        """Remove an invader. Killing one that's already gone is a no-op."""
        pass  # stub

    def shooters(self) -> list[tuple[int, int]]:
        """The lowest alive invader in each column (only they drop bombs),
        sorted by column."""
        pass  # stub

    def lowest_y(self) -> float | None:
        """y of the lowest alive invader, or None if the wave is cleared."""
        pass  # stub

    def next_wave(self) -> None:
        """Every invader back, direction right, left at the start position;
        each new wave starts STEP_DOWN lower than the previous one, but never
        lower than start_bottom - 4 * STEP_DOWN."""
        pass  # stub
