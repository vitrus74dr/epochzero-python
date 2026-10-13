# Snake

Snake has been on everything from 1970s arcades to old Nokia phones. It's a different kind
of game from Pong: the world is a **grid**, and time moves in **ticks** (the snake jumps
one whole cell at a time), not smoothly. Those two ideas carry Tetris and Pac-Man.

`pygrid-tutor scaffold W10.1` gives `snake.py` (a `SnakeGame` model, a `Ticker`, and
high-score functions, all stubs) and 19 tests. You write the model, then `snake_game.py`
draws it.

## 1. Grid coordinates

A grid cell is `(col, row)`. Following Arcade, row 0 is at the **bottom**, so "up" is `(0, +1)`:

```python
UP, DOWN, LEFT, RIGHT = (0, 1), (0, -1), (-1, 0), (1, 0)

head = (10, 7)
direction = UP
new_head = (head[0] + direction[0], head[1] + direction[1])     # (10, 8)
```

Drawing converts cells to pixels: `x = col * CELL`, `y = row * CELL`. Keep the model in
cells and the drawing in pixels, and never mix them up. Mixing `(x, y)` with
`(row, col)` is this week's classic bug: pick `(col, row)` and use it everywhere.

## 2. The body is a deque

A snake moves by adding a new head and dropping the tail. A `deque` (double-ended
queue) does both cheaply:

```python
from collections import deque

body = deque([(10, 7), (9, 7), (8, 7)])    # body[0] is the head
body.appendleft((11, 7))                   # new head
body.pop()                                 # drop the tail
list(body)                                 # [(11, 7), (10, 7), (9, 7)]
```

To **grow**, skip the `pop()` on the tick it eats. That's the whole trick.

## 3. Collisions on a grid

No geometry here: a collision is just "is this cell taken?". `new_head in body` works,
but one rule is easy to miss: moving into the cell the tail is **leaving this tick** is
fine, because the tail moves away at the same moment. So check against the body *without*
its last cell, unless the snake is eating this tick, when the tail stays put.

## 4. Turning: the queue and the 180° rule

Two traps, both caught by the tests:

- **Reversing.** Heading right, press left: the head moves into the neck and you die.
  Real Snake ignores a turn straight back.
- **Fast fingers.** Ticks are slow (8 a second). Press ↑ then ← quickly, inside one
  tick, and a single `direction` variable keeps only the ←, which is a reverse, so it's
  ignored and your ↑ is lost. The fix: **queue** turns, apply one per tick, and judge
  each new turn against the *last queued* direction. Cap the queue at two so mashing keys
  doesn't build up a backlog.

## 5. Fixed ticks from variable frames

Arcade calls `on_update(dt)` with whatever time passed. Snake needs "move every 0.125 s".
An **accumulator** turns one into the other:

```python
class Stopwatch:
    """Counts whole seconds from uneven frame times."""

    def __init__(self):
        self.acc = 0.0
        self.seconds = 0

    def update(self, dt):
        self.acc += dt
        while self.acc >= 1.0:
            self.acc -= 1.0
            self.seconds += 1


sw = Stopwatch()
for dt in (0.4, 0.4, 0.4, 0.9):
    sw.update(dt)
sw.seconds, round(sw.acc, 2)      # (2, 0.1)
```

The leftover time carries over, so nothing is lost or gained over many frames. Your `Ticker`
returns *how many* ticks to run this frame; on a slow frame, that might be two.
(Arcade's `on_fixed_update` does the same internally, at a fixed 60 Hz.)

A floating-point warning:

```python
>>> 0.25 - 0.1 - 0.1
0.04999999999999999
>>> 0.25 - 0.1 - 0.1 + 0.05 >= 0.1
False
```

`0.1` can't be stored exactly in binary, so accumulated tenths drift a hair below the
threshold. With a 0.1 s interval, an occasional tick arrives a frame late. That's harmless
in a game, but it surprises tests. Intervals that are powers of two (0.125, 0.0625) are exact.

## 6. Random food you can test

Food goes on a random **free** cell. Build the list of free cells, then
`rng.choice(free)`. Picking random cells until one is free gets very slow on a nearly full
board, and never finishes on a full one. The random generator is injected (Lesson 4.3), so
the same seed gives the same food: tests can rely on it, and you can replay a bug.

## 7. High score

JSON, as in Lesson 4.1: save `{"high_score": 12}`, and load it with a fallback to 0 when
the file is missing or broken. A corrupt save file must never stop the game from starting.

## 8. How it's checked

- **W10.1.a**: tutor review of the model.
- **W10.1.b**: a demo: arrow keys, fast U-turns that work, speed independent of frame
  rate, food never on the snake, high score kept between runs.
- **W10.1.c**: `/verify W10.1` (19 tests).

**Extras:** speed up every 5 foods; wrap-around walls as an option; a two-player mode on
one keyboard.

## Pitfalls

- `(x, y)` vs `(row, col)` confusion.
- One `direction` variable instead of a turn queue: quick turns get lost.
- Checking the new head against the whole body, including the tail that's moving away.
- Moving the snake in `on_update` every frame instead of on ticks.
