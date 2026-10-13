"""W9.2.d (part): collision sides, brick damage and clearing a level.
Your tutor adds tests for your game-state class and level progression."""

import pytest

from bricks import LEVEL_1, LEVEL_2, Brick, bounce, damage, hit_side, level_cleared, parse_layout

RECT = (100, 200, 160, 220)          # a 60x20 brick


def test_parse_layout():
    bricks = parse_layout("\n3.1\n.2.\n\n")
    assert bricks == [Brick(0, 0, 3), Brick(2, 0, 1), Brick(1, 1, 2)]


def test_parse_rejects_junk():
    with pytest.raises(ValueError):
        parse_layout("12x")


def test_shipped_levels():
    assert len(parse_layout(LEVEL_1)) == 40
    assert len(parse_layout(LEVEL_2)) == 26


@pytest.mark.parametrize("x,y,side", [
    (130, 195, "bottom"),     # from below, centred
    (130, 225, "top"),        # from above
    (96, 210, "left"),        # from the left, mid-height
    (164, 210, "right"),
    (102, 194, "bottom"),     # near the bottom-left corner, but deeper past the left edge
    (95, 214, "left"),        # near the top-left corner, deeper past the top edge
])
def test_hit_side(x, y, side):
    assert hit_side(x, y, 8, RECT) == side


@pytest.mark.parametrize("x,y", [(130, 189), (91, 210), (300, 300)])
def test_no_hit(x, y):
    assert hit_side(130, 195, 8, RECT) == "bottom"      # sanity: a real hit
    assert hit_side(x, y, 8, RECT) is None


@pytest.mark.parametrize("side,v,expected", [
    ("bottom", (120, 300), (120, -300)),
    ("top", (120, -300), (120, 300)),
    ("left", (300, 50), (-300, 50)),
    ("right", (-300, 50), (300, 50)),
    ("bottom", (120, -300), (120, -300)),     # already moving away: unchanged
])
def test_bounce(side, v, expected):
    assert bounce(*v, side) == expected


def test_damage_and_clear():
    bricks = parse_layout("21")
    strong, weak = bricks
    assert damage(bricks, strong) is False and strong.hits == 1 and strong in bricks
    assert damage(bricks, weak) is True and weak not in bricks
    assert not level_cleared(bricks)
    assert damage(bricks, strong) is True
    assert level_cleared(bricks) and bricks == []
