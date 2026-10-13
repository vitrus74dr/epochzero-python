# Space Invaders

Taito, 1978: rows of aliens march side to side, step down at each edge, and speed up as
you shoot them. It was so popular that it was blamed (probably unfairly) for a coin
shortage in Japan. This game is about **lots of objects**: dozens of invaders, bullets and
bombs, and shields that crumble, all being created and destroyed every second.

`pygrid-tutor scaffold W11.1` gives `formation.py`, the invaders' marching logic, as stubs
plus 10 tests. Then you build `invaders.py`.

## 1. The formation is one thing

Don't give 55 invaders 55 separate velocities. The formation moves **as a block**: one
offset `(left, bottom)` and one direction. Each invader is just a slot `(col, row)`, and
its position is calculated from the offset:

```python
SPACING_X, SPACING_Y = 48, 40
left, bottom = 80, 360

def position(slot):
    col, row = slot
    return left + col * SPACING_X, bottom + row * SPACING_Y

position((2, 1))          # (176, 400)
```

Dead invaders are slots removed from a `set`. Move the block, and every survivor moves with it.

## 2. The march

Every tick, the formation steps sideways. When the next step would carry the outermost
**survivor** past the margin, it steps **down** instead, and turns round. Note "survivor":
shoot out the whole right-hand column and the formation marches further right before
turning, just like the arcade. That's why `edges()` looks only at invaders still alive.

The tick is the accumulator from Snake (Lesson 10.1), with one twist: the interval
**shrinks** as invaders die. Fewer invaders, faster march, more panic. In the 1978
original, this speed-up was partly an accident: the hardware simply drew fewer aliens per
frame, faster. The designers kept it.

## 3. Who can shoot?

Only the **lowest invader in each column** drops bombs; the ones above it would hit their
own side. "The lowest alive per column" is a grouping problem you've seen before (Lesson 2.2):

```python
alive = {(0, 0), (0, 1), (2, 3), (2, 1)}
lowest = {}
for col, row in alive:
    if col not in lowest or row < lowest[col]:
        lowest[col] = row
sorted(lowest.items())          # [(0, 0), (2, 1)]
```

## 4. Bullets, bombs and SpriteLists

Bullets and bombs are perfect `SpriteList` material (Lesson 6.1). Make
`arcade.SpriteSolidColor(width, height, x, y, colour)` sprites, move them every update,
and remove them when they hit something or leave the screen:

```python fragment
for bomb in list(self.bombs):            # a copy: we remove inside the loop
    bomb.center_y -= BOMB_SPEED * dt
    if arcade.check_for_collision(bomb, self.player):
        bomb.remove_from_sprite_lists()
        self.lives -= 1
    elif bomb.top < 0:
        bomb.remove_from_sprite_lists()  # off screen: forget it
```

Forget the "off screen" branch and the list grows forever: a slow memory leak, and
collision checks against thousands of invisible bombs. This week's pitfall watch includes it.

**The one-bullet rule:** the original allowed one player bullet on screen at a time. That's
a design decision (it makes every shot count) and one line of code: only fire if
`len(self.bullets) == 0`.

## 5. Shields that crumble

Each shield is a grid of small square sprites, say 8×4 blocks of 8 px each, all in one
`SpriteList`. A bullet or bomb that hits one removes that block (and itself). Holes appear
exactly where the shots land, with no image editing at all.

## 6. Waves

When the formation is empty, `next_wave()` brings everyone back, a little lower each time,
which leaves less room before they land. If the lowest invader reaches the shields' height,
the invasion has succeeded: game over.

## 7. How it's checked

- **W11.1.a**: tutor review of `formation.py`.
- **W11.1.b**: a demo: one bullet at a time, bombs only from the bottom invaders, shields
  wearing away, and a second wave.
- **W11.1.c**: `/verify W11.1` (10 tests).

**Extras:** the mystery saucer across the top for bonus points; a two-frame animation for
the invaders (swap textures on every march step); the famous four-note march sound,
speeding up with the formation.

## Pitfalls

- 55 independent invaders instead of one formation offset.
- Edges measured from all slots instead of the survivors.
- Bullet and bomb lists that never shrink (no off-screen removal).
- Removing sprites while iterating over the same list.
