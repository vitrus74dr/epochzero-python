"""W12.1.c: the maze, coordinates, and Pac-Man's tile-to-tile movement."""

import pytest

from maze import (DOWN, LEFT, POWER_POINTS, RIGHT, TILE, UP, Maze, PacMan, load_maze,
                  pixel_to_tile, tile_to_pixel)

TINY = """
#######
#.o.. #
#.##.##
#P....#
#######
"""


@pytest.fixture
def maze():
    return load_maze()


def test_classic_maze(maze):
    assert (maze.width, maze.height) == (28, 31)
    assert len(maze.pellets) == 240 and len(maze.power) == 4     # the 1980 numbers
    assert maze.pac_start == (13, 23)
    assert len(maze.door) == 2 and len(maze.house) == 18
    assert (0, 0) in maze.walls and (1, 1) in maze.pellets and (1, 3) in maze.power


def test_bad_mazes():
    with pytest.raises(ValueError):
        Maze("###\n#P\n###")
    with pytest.raises(ValueError):
        Maze("####\n#..#\n####")


def test_tile_pixel_round_trip(maze):
    assert tile_to_pixel((0, 30), 31) == (TILE / 2, TILE / 2)                 # bottom-left
    assert tile_to_pixel((0, 0), 31) == (TILE / 2, 30 * TILE + TILE / 2)      # top-left
    for tile in [(0, 0), (13, 23), (27, 30), (5, 14)]:
        assert pixel_to_tile(*tile_to_pixel(tile, 31), 31) == tile
    assert pixel_to_tile(TILE - 0.1, 0.1, 31) == (0, 30)


def test_passable(maze):
    door = next(iter(maze.door))
    assert not maze.passable((0, 0))
    assert maze.passable((1, 1))
    assert not maze.passable(door) and maze.passable(door, ghost=True)
    assert not maze.passable((13, 14)) and maze.passable((13, 14), ghost=True)
    assert not maze.passable((5, -1)) and not maze.passable((5, 31))


def test_tunnel_wraps(maze):
    assert maze.wrap((-1, 14)) == (27, 14) and maze.wrap((28, 14)) == (0, 14)
    dirs = dict(maze.neighbours((0, 14)))
    assert dirs[LEFT] == (27, 14) and dirs[RIGHT] == (1, 14)


def test_neighbours_order(maze):
    assert [d for d, _ in maze.neighbours((6, 5))] == [UP, LEFT, DOWN, RIGHT]   # a crossroads


def test_eat():
    m = Maze(TINY)
    assert m.eat((1, 1)) == 10 and m.eat((1, 1)) == 0
    assert m.eat((2, 1)) == POWER_POINTS and (2, 1) not in m.power
    assert m.eat((5, 1)) == 0


def test_moves_left_by_default_and_stops_at_wall():
    m = Maze(TINY)
    pac = PacMan(m, speed=4)
    pac.update(0.5)                                   # (0,3) to the left is a wall
    assert pac.tile == (1, 3) and not pac.moving and pac.progress == 0


def test_buffered_turn_waits_for_an_opening():
    #  row 2 is "#.##.##": from row 3 you can only go up at columns 1 and 4
    m = Maze(TINY)
    pac = PacMan(m, speed=4)
    pac.tile, pac.direction = (2, 3), RIGHT
    pac.steer(UP)                                     # wall above (2,3): remembered
    pac.update(0.25)                                  # one tile: (3,3), wall above too
    assert pac.tile == (3, 3) and pac.direction == RIGHT and pac.next_direction == UP
    pac.update(0.25)                                  # (4,3): open above, so he turns
    assert pac.tile == (4, 3) and pac.direction == UP and pac.next_direction is None
    pac.update(0.25)
    assert pac.tile == (4, 2)


def test_eating_while_moving():
    m = Maze(TINY)
    pac = PacMan(m, speed=10)
    pac.direction = RIGHT
    points = pac.update(0.35)                         # 3.5 tiles: eats (2,3) (3,3) (4,3)
    assert points == 30 and pac.tile == (4, 3) and pac.progress == pytest.approx(0.5)


def test_instant_reverse():
    m = Maze(TINY)
    pac = PacMan(m, speed=4)
    pac.direction = RIGHT
    pac.update(0.15)                                  # 60% of the way to (2,3)
    pac.steer(LEFT)
    assert pac.direction == LEFT and pac.tile == (2, 3)
    assert pac.progress == pytest.approx(0.4)
    assert pac.position() == pytest.approx((1.6, 3))


def test_stopped_pac_restarts_on_a_buffered_turn():
    m = Maze(TINY)
    pac = PacMan(m, speed=4)
    pac.update(0.1)                                   # walks into the wall: stops
    assert not pac.moving
    pac.steer(RIGHT)
    pac.update(0.25)
    assert pac.moving and pac.tile == (2, 3)


def test_through_the_tunnel(maze):
    pac = PacMan(maze, speed=10)
    pac.tile, pac.direction = (1, 14), LEFT
    pac.update(0.25)                                  # 2.5 tiles: (0,14), (27,14), halfway on
    assert pac.tile == (27, 14) and pac.progress == pytest.approx(0.5)
