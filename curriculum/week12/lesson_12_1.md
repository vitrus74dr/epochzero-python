# The Maze & Pac-Man

Namco, 1980. Toru Iwatani wanted a game that wasn't about shooting. He gave us a yellow
circle in a maze, four ghosts with distinct personalities, and the best-selling arcade game
of all time. This week you build it, and almost everything from the past eleven weeks is in
it: text maps, grids, ticks, state machines, pathfinding.

`pygrid-tutor scaffold W12.1` gives `maze.txt` (the classic 28×31 layout, with the
original's 240 pellets and 4 power pellets), `maze.py` (stubs) and 13 tests.

## 1. The maze is text

```text
############################
#............##............#
#.####.#####.##.#####.####.#
#o####.#####.##.#####.####o#
...
######.## #GGGGGG# ##.######
      .   #GGGGGG#   .         ← the tunnel row: open at both ends
```

`#` wall, `.` pellet, `o` power pellet, `-` the ghost-house door, `G` inside the house,
`P` Pac-Man's start. Parsing it is Lesson 6.3 again: one pass over the characters, filling
sets of tiles. Sets make "is there a pellet here?" instant, and eating a pellet is
`pellets.remove(tile)`.

This time keep tiles in **text order**: row 0 is the *top* line, so moving up is
`(0, -1)`. Grid logic is easier to check against the text file that way. Only drawing
converts to Arcade's y-up pixels, with `tile_to_pixel`, which you've written before
(Lesson 6.3, section 2).

## 2. Who can go where

| Tile | Pac-Man | Ghosts |
|---|---|---|
| wall `#` | no | no |
| door `-`, house `G` | no | yes |
| everything else | yes | yes |

`passable(tile, ghost=False)` encodes that table. The **tunnel**: walking off the left
edge of row 14 brings you in on the right. Wrapping the column (`col % width`) does it in
one line, and the walls make sure it only matters on that row.

## 3. Moving tile to tile

Pac-Man doesn't move freely like the Asteroids ship. He travels **between tile centres**.
His state is the tile he's leaving, a direction, and `progress`, how far along he is
(0 to 1). Each update adds `speed × dt` (in tiles) to `progress`; every time it passes 1,
he's arrived at the next tile. This is the accumulator from Snake (Lesson 10.1) again,
except that he's *drawn* in between, which makes the movement smooth.

```python fragment
def position(self):
    return (self.tile[0] + self.direction[0] * self.progress,
            self.tile[1] + self.direction[1] * self.progress)
```

## 4. Buffered turns: why Pac-Man feels good

Press ↑ a moment *before* the junction, and Pac-Man turns *at* the junction. The game
remembers the request (`next_direction`) and tries it at every tile centre until it's
possible. Without the buffer you'd have to press the key at the exact frame he's centred,
which is impossible to play. It's the same idea as Snake's turn queue, with one slot.

Reversing is different: allowed **instantly**, even between tiles, because it never needs
a junction. Swap the "from" and "to" tiles and use `1 − progress`:

```text
before:  (1,3) ──60%──▶ (2,3)        facing RIGHT, progress 0.6
after:   (1,3) ◀──40%── (2,3)        facing LEFT from (2,3), progress 0.4
```

He's drawn at the same spot before and after; only his direction changed.

## 5. Eating

At each tile centre, `maze.eat(tile)` removes a pellet (10 points) or power pellet (50) and
returns the points. When both sets are empty, the level is cleared: reload the maze and
speed everything up a little.

## 6. Drawing

- Walls: build the wall sprites **once** into a `SpriteList(use_spatial_hash=True)`, or draw
  the maze into a texture once. Drawing 400 rectangles one by one every frame is slow.
- Pellets: small circles at `tile_to_pixel(tile)`. Pac-Man: a yellow circle at his
  `position()`, converted to pixels. A chomping mouth is a classic extra:
  `arcade.draw_arc_filled`, with the mouth angle opening and closing over time.

## 7. How it's checked

- **W12.1.a–b** (tutor checks): the maze loads and draws; Pac-Man moves smoothly, turns
  early, reverses instantly, eats, and goes through the tunnel.
- **W12.1.c**: `/verify W12.1` (13 tests).

## Pitfalls

- Mixing text rows (down = +1) with Arcade pixels (up = +y): convert in one place only.
- Turning only when a key is held at the exact centre (no buffer).
- Letting Pac-Man through the ghost-house door.
- Naming a game attribute `self.time`: `arcade.Window` already has a read-only `time`
  property, and assigning to it crashes. Use `self.clock`.
