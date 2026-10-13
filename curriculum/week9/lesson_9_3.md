# Game Loops & Collisions: Review

Before Snake and Tetris, check that the core ideas of Weeks 5–9 are solid. They carry
every game from here to Pac-Man. Read the summary, try the three exercises, then take the quiz.

## The loop

| Callback | Runs | Put here |
|---|---|---|
| `on_update(dt)` | once per frame (frame rate varies) | movement you scale by `dt`, timers |
| `on_fixed_update(dt)` | exactly 60×/s by default | physics engines, anything counted in steps |
| `on_draw()` | once per frame | drawing only; never change the game state here |
| `on_key_press` / `on_key_release` | on input | record the input; act on it in an update |

**Frame-rate independence:** `position += velocity * dt`. Never move a fixed amount per frame.

## Collisions

- **Circle vs rectangle (AABB):** overlap if the circle's box overlaps the rectangle. The
  side hit is the one with the smallest penetration (Lesson 9.2).
- **Tunnelling:** fast object, thin target, big step, missed collision. Fix it with
  sub-steps, or a cap on speed.
- **Moving away:** only respond to a collision when the object is moving *into* the thing
  it hit, or it gets stuck jittering.
- **Removing while iterating:** collect first, remove after; or iterate over a copy.

## Game states

One state value plus a transition table beats a tangle of booleans, and it's testable
arrow by arrow.

## Exercises

1. **Frame-rate check.** Take your Pong ball and step it 0.5 s in one call, and in 300
   calls of 1/600 s. Do they agree? Then break it on purpose (`x += 3` per call) and watch it disagree.
2. **Tunnel on purpose.** In Pong, remove the sub-steps and set the ball's speed to 3,000.
   How often does it pass through a paddle? Put the sub-steps back.
3. **Draw the state machine** for a game you know (a menu with settings, say) as a
   transition table, then write `next_state` and three tests for it.

## Quiz (W9.3.a)

Five questions; you need 4/5. [Take the quiz](#/quiz/W9.3.quiz), or run `epochzero-quiz W9.3.quiz`.
