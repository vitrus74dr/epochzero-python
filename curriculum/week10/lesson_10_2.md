# Tetris

Alexey Pajitnov wrote Tetris in Moscow in 1984; it's probably the most-played video game
ever made. Under the falling blocks is a neat puzzle in grids and geometry: how do you
*rotate* a shape, what happens when it doesn't fit, and how do whole rows vanish?

`pygrid-tutor scaffold W10.2` gives `tetris.py`: shapes, rotation, the board, kicks,
scoring and the randomizer, as stubs with a contract and 22 tests. The game loop (gravity,
controls, lock timing, the preview, game over) is yours, planned at `/grill-me`.

## 1. A board is a 2-D list, built carefully

```python
rows, cols = 3, 4
grid = [[None] * cols for _ in range(rows)]      # three separate rows
grid[0][1] = "T"
grid
# [[None, 'T', None, None], [None, None, None, None], [None, None, None, None]]
```

`grid[row][col]`: row first, then column. Row 0 is the bottom, so pieces fall towards row 0.

The **aliasing trap** (quiz W2.2.b, question 5) is fatal here:

```python
bad = [[None] * 4] * 3          # ONE row, listed three times
bad[0][1] = "T"
bad[2][1]                        # 'T': every "row" changed
```

The scaffold's tests check for exactly this.

## 2. Shapes and rotation without lookup tables

Each tetromino sits in a small square box (3×3; the I uses 4×4, the O 2×2). Rather than
typing out all 4 rotations of 7 pieces (28 shapes, 112 cells to get wrong), compute them.
A quarter turn clockwise inside an `n×n` box, with row 0 at the bottom, maps

```text
(c, r)  →  (r, n − 1 − c)
```

Check it on a 3×3 box: the top-left corner `(0, 2)` goes to `(2, 2)`, the top-right corner.
That's clockwise. The centre `(1, 1)` stays put. Apply it twice for a half turn, and four
times to get back where you started (a test checks this for every piece).

```python
def rotate(cells, n):
    return sorted((r, n - 1 - c) for c, r in cells)

L_SHAPE = [(2, 2), (0, 1), (1, 1), (2, 1)]
rotate(L_SHAPE, 3)                 # [(1, 0), (1, 1), (1, 2), (2, 0)]
```

**Try it:** draw the L on squared paper, rotate the paper a quarter turn clockwise, and
compare with the output.

## 3. Kicks: when a rotation doesn't fit

Rotate a vertical I piece that's flush against the left wall, and the flat result
sticks out past the edge. Real Tetris doesn't refuse: it tries nudging the piece a cell or
two sideways (or up one), and takes the first position that fits. These are **wall kicks**.

The scaffold's `KICKS` list is a simple version: no shift, left 1, right 1, left 2,
right 2, up 1. (The official "Super Rotation System" uses different kick tables per piece and
rotation. It's an extra, if you want an authentic feel.)

## 4. Clearing lines

A full row has no `None` in it. To clear: keep the rows that *aren't* full, then add
fresh empty rows on top to get back to full height:

```python
grid = [["I", "I"], ["J", None], ["L", "L"]]           # rows 0 and 2 are full
keep = [row for row in grid if None in row]
cleared = len(grid) - len(keep)
grid = keep + [[None] * 2 for _ in range(cleared)]
grid, cleared                                           # ([['J', None], [None, None], [None, None]], 2)
```

One list comprehension handles one line, four lines, and lines that aren't next to each
other. Deleting rows one at a time inside a loop over the rows is the same "modifying while
iterating" bug as ever.

## 5. Fair randomness: the 7-bag

Pure `random.choice` can deal four S pieces in a row, or forty pieces without a single I.
Modern Tetris shuffles all seven kinds into a **bag** and deals them out, refilling when
it's empty. Every group of seven has one of each kind, so droughts are impossible.
`peek()` shows the next piece for the preview without dealing it. As always, the `rng` is
injected, so tests and replays are repeatable.

## 6. Gravity and levels

Pieces fall one row per *gravity interval*, which shrinks as the level rises:
`0.8 × 0.85^(level − 1)` seconds, never below 0.05. Level = 1 + lines ÷ 10. Use the
**accumulator** from Snake (Lesson 10.1): add `dt` each frame, drop a row whenever a whole
interval has built up. Score by lines cleared at once, times the level: 100, 300, 500,
or **800 for a "Tetris"** (four at once).

Things to decide at `/grill-me`:

- **Lock delay:** does a piece lock the instant it lands, or can you still slide it for
  half a second? (Modern games: half a second.)
- Soft drop (↓ speeds the fall) and hard drop (space: straight down and lock).
- What does game over look like? (A new piece that doesn't fit at spawn.)
- **DAS** (delayed auto-shift): holding ← moves once, pauses, then repeats quickly.

## 7. How it's checked

- **W10.2.a**: `/grill-me W10.2`.
- **W10.2.b–c**: a demo: all seven pieces, rotation against walls, line clears, levels
  speeding up, hard drop, the preview.
- **W10.2.d**: `/verify W10.2`: the scaffold's 22 tests, plus the tutor's tests for your loop and game over.
- **W10.2.e**: `walkthrough.md`.

## Pitfalls

- `[[None] * w] * h`: all rows are one row.
- Rows and columns swapped (`grid[col][row]`).
- Deleting full rows while looping over them.
- Gravity counted in frames instead of time.
- `random.choice` for pieces: droughts and floods.
