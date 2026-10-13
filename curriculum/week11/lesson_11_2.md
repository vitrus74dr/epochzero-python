# Asteroids

Atari, 1979. A triangle of a ship spins, thrusts and drifts through a field of rocks
that break apart when shot. There's no friction to speak of in space, so the ship keeps
moving after you let go of the thrust: **inertia**. It's a game about vectors, and it
feels completely unlike Pong.

`pygrid-tutor scaffold W11.2` gives `space.py`: headings, thrust, drag, wrap-around,
collisions, splitting and bullets, as stubs plus 17 tests. The game around it is yours,
designed at `/grill-me`.

## 1. Velocity is a vector

Since Pong, velocity has been two numbers, `(vx, vy)`. In Asteroids you **change** it,
rather than set it. Thrust *adds* a little velocity in the direction the ship faces:

```python
import math

def heading_vector(degrees):
    r = math.radians(degrees)
    return math.cos(r), math.sin(r)

vx, vy = 0.0, 0.0
dx, dy = heading_vector(90)                # facing up
vx, vy = vx + dx * 300 * 0.1, vy + dy * 300 * 0.1     # 0.1 s of thrust at 300 px/s²
round(vx, 6), round(vy, 6)                 # (0.0, 30.0)
```

Turn to face right and thrust again: the old upward velocity **stays**, and the new
rightward push is added to it. The ship drifts diagonally. That's inertia, and it's
the whole feel of the game. `thrust()` must add, never overwrite (a test checks).

Keep the speed manageable with a little **drag** (multiply the velocity by slightly less
than 1 each step) and a **speed cap** (if it's too fast, scale it back to the maximum,
keeping its direction).

## 2. Two angle conventions

The maths in `space.py` uses **maths angles**: 0° points right, 90° up, counter-clockwise
positive. That's what `math.cos` and `math.sin` expect (in radians, after `math.radians`).

Arcade's `sprite.angle` turns the image **clockwise**. And the ship image in
`:resources:` points **up**. So to show a ship heading at `heading` degrees:

```python fragment
ship_sprite.angle = 90 - heading
```

Check it: heading 90 (up) gives angle 0, the image as drawn. Heading 0 (right) gives a
90° clockwise turn, nose pointing right. When a sprite flies sideways or backwards
relative to its nose, this conversion is the first thing to check.

## 3. Wrap-around

Fly off the right edge, reappear on the left. Two details make it smooth:

- Wait until the object is **completely** off screen (its centre more than its radius beyond
  the edge), or rocks visibly pop from one side to the other.
- Move it by `width + 2 × radius`, so it reappears just *off* the opposite edge and slides in.
  Move it by only `width` and it lands past the far edge's threshold, so the next frame wraps
  it straight back. It would flicker between the two edges for ever. (A test checks
  that wrapping twice in a row leaves it where it is.)

## 4. Circle collisions

Rocks, bullets and the ship are all treated as circles. Two circles touch when the distance
between their centres is at most the sum of their radii:

```python
import math

def touching(x1, y1, r1, x2, y2, r2):
    return math.hypot(x2 - x1, y2 - y1) <= r1 + r2

touching(0, 0, 10, 25, 0, 15)      # True: exactly touching
```

`math.hypot(dx, dy)` is Pythagoras: `√(dx² + dy²)`.

## 5. Splitting rocks

A large rock breaks into two medium ones, a medium into two small, and a small one
vanishes. The pieces fly off at angles to the parent's path, one each way. That's a
**vector rotation**:

```python
import math

def rotate(vx, vy, degrees):
    a = math.radians(degrees)
    return vx * math.cos(a) - vy * math.sin(a), vx * math.sin(a) + vy * math.cos(a)

[round(v, 6) for v in rotate(100, 0, 90)]      # [0.0, 100.0]: right becomes up
```

Smaller rocks are faster (×1.3) and worth more points: they're harder to hit. The random
angle comes from an injected `rng`, as always.

## 6. Bullets that expire

Bullets wrap too, so without a limit they'd circle the screen forever. Each one has an
`age`; when it passes its `lifetime` (about a second), it's dropped. `age_bullets` returns a
**new** list of the survivors, rather than deleting from the list it's looping over. Also
cap how many can exist at once (the original allowed four).

A bullet starts at the ship's **nose** and moves at the ship's velocity *plus* the bullet
speed. That's real physics: fire forward while flying forward, and the shot goes faster.

## 7. Lives and respawning

When the ship is hit, it reappears in the centre, which might be right where a rock is
passing. Give it a couple of seconds of **invulnerability** after respawning, and make it
blink so the player can tell (draw it only on alternate eighths of a second).

## 8. How it's checked

- **W11.2.a**: `/grill-me W11.2` (controls, waves, the bullet cap, invulnerability, the
  sprite-or-shapes decision).
- **W11.2.b–c**: a demo: drifting with inertia, wrap-around, splitting, expiring
  bullets, losing a life and respawning safely.
- **W11.2.d**: `/verify W11.2`: the scaffold's 17 tests, plus the tutor's tests for your game logic.
- **W11.2.e**: `walkthrough.md`.

**Extras:** hyperspace (jump to a random position, with a small risk of exploding); the
flying saucer that shoots back; a thrust flame drawn only while ↑ is held.

## Pitfalls

- Degrees given to `math.sin`/`math.cos`.
- Arcade's clockwise `sprite.angle` treated as a maths angle (the ship flies sideways).
- Thrust that sets velocity instead of adding to it (no inertia).
- Wrapping as soon as the centre crosses the edge (popping), or by only `width` (flickering).
- Bullet lists that grow forever.
