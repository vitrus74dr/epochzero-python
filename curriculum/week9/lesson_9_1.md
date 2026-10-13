# Pong

1972: two paddles, a ball and a score. Pong made video games a business, and it's still
the best first game to build, because every idea in it comes back in every game after
it: a loop that updates and draws, velocity, collisions, and the rules of play.

Arcade Classics weeks follow one pattern: **the rules live in a pure module with no
Arcade in it**, tested like any other code, and a thin Arcade file draws them and feeds
them keyboard input. Run `epochzero-tutor scaffold W9.1`. You get `physics.py` (stubs whose
docstrings are the spec) and `test_physics.py`. You write the physics, then `pong.py`.

## 1. State is data

Pong's whole world is a few numbers:

```python
from dataclasses import dataclass


@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0       # velocity: pixels per second, horizontally
    vy: float = 0.0
    radius: float = 8.0


b = Ball(400, 300, vx=-420, vy=90)
b                          # Ball(x=400, y=300, vx=-420, vy=90, radius=8.0)
```

A **dataclass** writes `__init__` and `__repr__` for you (Lesson 3.1 by hand). Each frame,
the rules change these numbers; the drawing code only reads them.

## 2. Velocity and `dt`

Position changes by velocity × time: `x += vx * dt` (Lesson 5.2). The test
`test_move_is_frame_rate_independent` checks that one 0.5-second step lands exactly where
thirty small steps do. That property is what makes a game feel the same at 30 or 240 fps.

## 3. Bouncing off walls

When the ball crosses the floor, two things must happen: put it **back inside** (or it
can get stuck outside, flipping direction every frame), and make its velocity point
**away** from the wall. Note: *away*, not just "reversed". `vy = abs(vy)` is safer than
`vy = -vy`, because it can't flip the wrong way twice.

## 4. The paddle: where you hit it matters

If the ball always bounced straight back, Pong would be a solved game. The original's
trick: the bounce angle depends on **where** the ball meets the paddle. The centre sends
it straight back; the edges send it off steeply.

```text
      ┌─┐  ← hit here: steep upward (+60°)
      │ │
      │ │  ← centre: straight back (0°)
      │ │
      └─┘  ← hit here: steep downward (-60°)
```

That's a **mapping**: offset in [-1, 1] → angle in [-60°, +60°]. Then velocity from an
angle and a speed, the unit circle again (Lesson 5.3):

```python
import math

speed, angle = 500, math.radians(30)
vx, vy = speed * math.cos(angle), speed * math.sin(angle)
round(vx), round(vy)           # (433, 250)
round(math.hypot(vx, vy))      # 500: the speed survives the change of direction
```

One subtlety the tests check: only bounce when the ball is moving **toward** the paddle.
Otherwise a ball still overlapping the paddle next frame bounces *again*, and gets stuck
jittering inside it.

## 5. Tunnelling

At 1,400 px/s and 60 fps, the ball moves 23 px per frame, and a paddle is only 14 px
wide. In one frame the ball is in front of the paddle; in the next it's already behind it.
They never overlapped, so no collision is detected. That's **tunnelling**.

The fix used in `pong.py`: split each frame's `dt` into **sub-steps** small enough that
the ball can't jump over anything:

```python fragment
SUBSTEP = 1 / 240

def on_update(self, dt):
    remaining = dt
    while remaining > 0:
        step = min(SUBSTEP, remaining)
        remaining -= step
        ...   # move, then check walls and paddles, for this small step
```

At 1/240 s, even the top speed moves under 6 px per sub-step, less than the ball's radius.

## 6. Serving, randomly but testably

A serve picks a random angle. As in Lesson 4.3, the random generator is **passed in**:
`serve(ball, ..., rng)` with `random.Random()` in the game and `random.Random(7)` in tests,
so a test can check that the same seed gives the same serve.

## 7. The Arcade side

`pong.py` holds two `Paddle`s, a `Ball`, the scores, and the set of held keys (Lesson 5.2).
`on_update` moves the paddles (W/S and ↑/↓, kept on screen), runs the sub-steps, asks
`scored()`, updates the score, and serves again, or shows the winner. `on_draw` draws
rectangles and a circle from the numbers. Every rule it uses is already tested.

## 8. How it's checked

- **W9.1.a**: tutor review of `physics.py`.
- **W9.1.b**: a demo against a friend (or yourself): paddles, scoring, serves, first to 7.
- **W9.1.c**: `/verify W9.1` (17 tests).

**Extras**, if you're enjoying it: a computer opponent that tracks the ball with a reaction
delay; a sound on each hit (`arcade.load_sound(":resources:sounds/hit1.wav")`); a
"serve" key instead of an automatic serve.

## Pitfalls

- `vy = -vy` on a wall hit without pushing the ball back inside: it gets stuck in the wall.
- Bouncing off a paddle the ball is moving away from (the jitter bug).
- One big physics step per frame at high speed (tunnelling).
- `math.sin`/`math.cos` given degrees.
