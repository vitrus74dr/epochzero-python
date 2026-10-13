"""W12.1: the maze and Pac-Man's movement, as pure logic. pacman.py draws them.

Tiles are (col, row) in TEXT order: row 0 is the TOP line of maze.txt, so
UP is (0, -1) here. (Only tile_to_pixel converts to Arcade's y-up pixels.)

    #  wall          .  pellet (10)        o  power pellet (50)
    -  ghost-house door (ghosts only)      G  inside the ghost house (ghosts only)
    P  Pac-Man's start (an empty tile)     space  empty floor
"""

from pathlib import Path

TILE = 24                                   # pixels
MAZE_FILE = Path(__file__).parent / "maze.txt"
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRECTIONS = [UP, LEFT, DOWN, RIGHT]        # the classic tie-break order
PELLET_POINTS, POWER_POINTS = 10, 50


class Maze:
    def __init__(self, text: str):
        """Parse maze text. Blank lines at the start/end are ignored.
        Raise ValueError if rows differ in width or there isn't exactly one P.

        Sets: width, height, walls, pellets, power, door, house (sets of
        tiles) and pac_start (a tile)."""
        pass  # stub

    def wrap(self, tile: tuple[int, int]) -> tuple[int, int]:
        """Wrap the column round (col % width): the side tunnel. Rows don't wrap."""
        pass  # stub

    def passable(self, tile: tuple[int, int], ghost: bool = False) -> bool:
        """After wrapping: False outside the rows or on a wall; the door and
        the house are passable only for ghosts; everything else is floor."""
        pass  # stub

    def neighbours(self, tile: tuple[int, int], ghost: bool = False) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """[(direction, next tile), ...] for each passable neighbour, in
        DIRECTIONS order, with the tile wrapped."""
        pass  # stub

    def eat(self, tile: tuple[int, int]) -> int:
        """Remove a pellet or power pellet at tile and return its points (else 0)."""
        pass  # stub


def load_maze(path: Path = MAZE_FILE) -> Maze:
    return Maze(path.read_text(encoding="utf-8"))


def tile_to_pixel(tile: tuple[int, int], height: int, size: int = TILE) -> tuple[float, float]:
    """Pixel centre of a tile; the TOP text row is the HIGHEST on screen."""
    pass  # stub


def pixel_to_tile(x: float, y: float, height: int, size: int = TILE) -> tuple[int, int]:
    """The tile containing pixel (x, y): the inverse of tile_to_pixel."""
    pass  # stub


class PacMan:
    """Moves tile to tile. `progress` (0 <= progress < 1) is how far he is
    from `tile` toward the next tile in `direction`.

    pac = PacMan(maze, speed=7.5)       # tiles per second
    pac.steer(UP)                        # remembered until it's possible
    points = pac.update(dt)
    """

    def __init__(self, maze: Maze, speed: float = 7.5):
        self.maze, self.speed = maze, speed
        self.tile = maze.pac_start if maze else (0, 0)
        self.direction = LEFT
        self.next_direction: tuple[int, int] | None = None
        self.progress = 0.0
        self.moving = True

    def steer(self, direction: tuple[int, int]) -> None:
        """Buffer a turn. A reverse (the exact opposite of `direction`) happens
        at once: between tiles (progress > 0) the next tile becomes the current
        one and progress becomes 1 - progress; at a tile centre he simply turns.
        Any other turn waits in next_direction until Pac-Man is at a tile
        centre where it's possible."""
        pass  # stub

    def update(self, dt: float) -> int:
        """Move speed * dt tiles. At every tile centre reached or sat on:
        eat (adding points); take next_direction if that way is passable;
        then if the way ahead is a wall, stop there (moving = False,
        progress = 0), otherwise keep moving (moving = True). So a stopped
        Pac-Man starts again as soon as a turn makes the way ahead open.
        Tiles wrap through the tunnel. Return the points eaten."""
        pass  # stub

    def position(self) -> tuple[float, float]:
        """Fractional tile coordinates for drawing: tile + direction * progress
        (col may be < 0 or >= width briefly while in the tunnel)."""
        pass  # stub
