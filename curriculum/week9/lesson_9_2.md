# Breakout

Atari, 1976: Pong turned on its side, with a wall of bricks to smash. It adds three ideas
to Pong: collision with **many** objects (and knowing which *side* you hit), **levels**,
and **game states**: title screen, playing, paused, game over.

`epochzero-tutor scaffold W9.2` gives `bricks.py`: the collision maths and brick bookkeeping,
as stubs with a contract and tests. The rest is your design at `/grill-me`.

## 1. Bricks from a layout

Levels are text again (Lesson 6.3), with a digit for how many hits a brick takes:

```text
3333333333
2222222222
1111111111
```

Colour by hits left (3 = red, 2 = orange, 1 = yellow), so a brick visibly weakens as you hit it.

## 2. Which side did I hit?

Bouncing off a brick's *bottom* flips `vy`; off its *side*, `vx`. Get it wrong and the
ball skates along the bricks or sinks into the wall. How do you know which side?

When a ball overlaps a rectangle, measure how far it has pushed in past each edge. The
side with the **smallest penetration** is the one it came through: it has only just
crossed that edge, while it's deep past the others.

```text
                 top
          ┌─────────────────┐
     left │                 │ right
          │       ▓▓        │
          └───────▓▓────────┘
                 bottom          ← ball pushed in 2 px here, 30+ px past every other edge
```

```python
def penetration(x, y, r, left, bottom, right, top):
    return {
        "bottom": (y + r) - bottom,
        "top": top - (y - r),
        "left": (x + r) - left,
        "right": right - (x - r),
    }

depths = penetration(130, 195, 8, 100, 200, 160, 220)
depths                         # {'bottom': 3, 'top': 33, 'left': 38, 'right': 38}
min(depths, key=depths.get)    # 'bottom'
```

`min(d, key=d.get)` finds the key with the smallest value. `hit_side` in the scaffold
adds the "no overlap" case and the tie rule. Pong's sub-stepping (Lesson 9.1, section 5)
keeps penetrations small, which keeps this reliable.

**Hit only one brick per sub-step.** If the ball touches two bricks at once and you
bounce for each, the two flips cancel out and it ploughs straight through. Bounce off the
first, `break`, and let the next sub-step sort out the rest.

## 3. Removing bricks safely

The ball hits a brick, the brick breaks: remove it from the list. Not while you're looping
over that same list (Lesson 2.1, section 4). Find the brick first, `break` out of the loop,
*then* call `damage()`, which removes it. With `SpriteList`s it's the same rule
(Lesson 6.1, section 3).

## 4. Game states: a state machine

A Breakout session moves through **states**, and only certain moves are allowed:

```text
 TITLE ──space──▶ PLAYING ──p──▶ PAUSED
   ▲                │  ▲           │
   │                │  └─────p─────┘
   │          lives = 0
   │                ▼
   └─────any key── GAME_OVER
```

That diagram is a **state machine**. In code, the current state is one value, and a
method decides what each input does *in that state*:

```python
from enum import Enum, auto


class State(Enum):
    TITLE = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


TRANSITIONS = {
    (State.TITLE, "space"): State.PLAYING,
    (State.PLAYING, "p"): State.PAUSED,
    (State.PAUSED, "p"): State.PLAYING,
}

def next_state(state, event):
    return TRANSITIONS.get((state, event), state)     # anything else: stay put

next_state(State.TITLE, "p")            # <State.TITLE: 1>: pausing the title does nothing
```

A table of allowed moves is easy to read, and easy to **test** (W9.2.c): every arrow in
the diagram is one assertion, and so is every *missing* arrow. Arcade's `View`s
(Lesson 6.3) are another way to build the same thing; at `/grill-me`, decide which you'll
use and why.

## 5. Levels and difficulty

When `level_cleared(bricks)` is true, load the next layout, reset the ball, and maybe
speed it up. The tracker asks for at least two levels and a ball that speeds up as bricks
fall. One approach is `speed = base * (1 + 0.02 * bricks_broken)`, with a cap.

## 6. How it's checked

- **W9.2.a**: `/grill-me W9.2` (states vs Views, level data, speed curve, lives).
- **W9.2.b**: a demo: two levels, lives, the speed-up.
- **W9.2.c–d**: `/verify W9.2`: the scaffold's 18 tests, plus the tutor's tests for your
  state machine and level progression.
- **W9.2.e**: `walkthrough.md`.

## Pitfalls

- Flipping `vy` for every hit regardless of side: the ball skates across the bricks.
- Bouncing off two bricks in one step (the flips cancel).
- Removing bricks while iterating over the list.
- States as a tangle of booleans (`paused and not game_over and started`) instead of one state value.
