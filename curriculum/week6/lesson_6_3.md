# 2D Platformer

Your first complete game: a platformer with coins, enemies, a goal flag, and at least two
levels. The levels are **text files**. You'll design them in the editor with characters,
and a loader turns them into sprites. The same idea runs Pac-Man's maze in Week 12.

## 1. Levels as text

```text
....................................
....................................
................CCC.................
...........CCC..####................
...........####...............##....
P..CC..###............E.CCC.##....F.
####################################
```

| Char | Means |
|---|---|
| `#` | ground / wall |
| `C` | coin |
| `E` | enemy (patrols left and right) |
| `F` | the goal flag |
| `P` | player start (exactly one) |
| `.` | empty |

Run `epochzero-tutor scaffold W6.3`. You get `levels.py`, whose loader has a fixed
interface (a file format is a contract), plus its tests, and two starter levels. Everything
else (the game, enemies, states, how levels switch) is yours to design at `/grill-me`.

## 2. Rows, columns, pixels

The text's **first line is the top** of the level, but Arcade's `y` grows **upward**
(Lesson 5.1). So row 0 of the text is the *highest* row on screen:

```python
TILE = 64

def tile_to_pixel(col, row, rows, tile=TILE):
    """Centre of the tile at (col, row); row 0 is the top line of the text."""
    x = col * tile + tile / 2
    y = (rows - 1 - row) * tile + tile / 2
    return x, y

tile_to_pixel(0, 6, rows=7)     # (32.0, 32.0): the bottom-left tile
tile_to_pixel(0, 0, rows=7)     # (32.0, 416.0): the top-left tile
```

Get this wrong and your level is upside down: the classic off-by-one-row bug.

## 3. Assets next to the code

Your own images and sounds live in an `assets/` folder beside the code. The current
working directory depends on *how* the game was started, so `"assets/coin.png"` works
from one folder and fails from another. Anchor every path to the file:

```python fragment
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
COIN = ASSETS / "coin.png"
LEVELS = sorted((Path(__file__).parent / "levels").glob("level*.txt"))
```

W6.3.d tests exactly this: every asset path in your code resolves to a file that exists.
`:resources:` paths are fine too (Arcade resolves those itself).

## 4. Enemies that patrol

A simple patrol: walk until you'd hit a wall *or* walk off a ledge, then turn round.

```python fragment
def on_fixed_update(self, delta_time):
    for enemy in self.enemies:
        enemy.center_x += enemy.change_x
        if arcade.check_for_collision_with_list(enemy, self.walls):
            enemy.center_x -= enemy.change_x
            enemy.change_x *= -1
```

Ledge detection is a good `/grill-me` question: how does an enemy know the tile ahead of
its feet is empty? (Hint: you have the level grid.)

Touching an enemy costs a life, or ends the level. Jumping *on* one, Mario-style, is a
worthy extra: compare the player's `bottom` with the enemy's `center_y` while the player
is falling.

## 5. Game states and Views

A game has screens: title, playing, level complete, game over. Arcade's `arcade.View`
is a screen with its own `on_draw`, `on_update` and key handlers. Switch with
`self.window.show_view(next_view)`:

```python fragment
class GameOverView(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.text = arcade.Text(f"Game over: {score}", 400, 300, arcade.color.WHITE, 30,
                                anchor_x="center")

    def on_draw(self):
        self.clear()
        self.text.draw()

    def on_key_press(self, key, modifiers):
        self.window.show_view(TitleView())
```

Your main loop then starts with `window = arcade.Window(...)`,
`window.show_view(TitleView())`, `arcade.run()`.

## 6. How it's checked

- **W6.3.a**: `/grill-me W6.3` (Views, enemies, level progression, lives).
- **W6.3.b–c**: a demo: collect coins, avoid or stomp enemies, finish level 1, load level 2, win.
- **W6.3.d**: `/verify W6.3`: the loader tests from the scaffold, plus an asset-path test
  the tutor writes against your `assets/` folder.
- **W6.3.e**: `walkthrough.md`.

## Pitfalls

- Relative asset paths (`"assets/x.png"`) instead of `Path(__file__).parent / ...`.
- Text row 0 drawn at the bottom (an upside-down level).
- Levels with zero or two `P`s. The loader must reject them with a clear message.
- Running physics in `on_update` instead of `on_fixed_update` (Lesson 6.2).
