# Vectors & Sprite Lists: Review

Before the Pac-Man capstone, a checkpoint on the two big ideas of Weeks 10–11: **vector
maths** for movement, and **managing many objects** that come and go.

## Vectors

| Idea | Code |
|---|---|
| direction from an angle | `(math.cos(math.radians(a)), math.sin(math.radians(a)))` |
| length (speed) | `math.hypot(vx, vy)` |
| scale to length `L` | `vx, vy = vx * L / s, vy * L / s`, where `s` is the current length |
| add (thrust, inherited velocity) | `(vx + ax, vy + ay)` |
| rotate by `a` | `(vx·cos a − vy·sin a, vx·sin a + vy·cos a)` |
| distance between points | `math.hypot(x2 − x1, y2 − y1)` |
| angle towards a point | `math.degrees(math.atan2(y2 − y1, x2 − x1))` |

`math.atan2(dy, dx)` (note: **y first**) gives the angle of a vector, correctly in all four
quadrants, unlike `atan(dy / dx)`. The Asteroids bot in the tests turns towards the nearest
rock with it.

Angles: `math` uses **radians**; maths angles turn **counter-clockwise** from the right;
Arcade's `sprite.angle` turns **clockwise**. Convert deliberately, every time.

## Many objects

- Batch drawing: `SpriteList.draw()`.
- Never remove from a list you're iterating over: iterate a copy (`list(sprites)`), or build a
  new list of survivors (`age_bullets`).
- Everything that's created must eventually be removed: off-screen bullets, expired
  particles, broken bricks. A list that only grows is a slow leak.
- Grids for grid games (`grid[row][col]`, built without aliasing); one shared offset for
  formations; slots and sets for "which are still alive".

## Exercises

1. Write `angle_to(x1, y1, x2, y2)` with `atan2`, and test it for a point in each quadrant.
2. Add a counter to your Asteroids or Invaders game showing how many sprites exist. Play
   for a minute: does it stay bounded?
3. Make a particle burst when a rock breaks: 20 tiny dots flying outwards at random angles,
   each fading and expiring after 0.5 s. Check the counter from exercise 2 afterwards.

## Quiz (W11.3.a)

Five questions; you need 4/5. [Take the quiz](#/quiz/W11.3.quiz), or run `epochzero-quiz W11.3.quiz`.
