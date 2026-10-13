# Ghosts

The ghosts are why Pac-Man is still studied by game designers. Each one follows a simple
rule, and together they feel like they're hunting you as a team. No ghost "thinks" much at
all. This lesson is about how simple rules make convincing behaviour, plus the algorithm
behind every pathfinder in games: **breadth-first search**.

`pygrid-tutor scaffold W12.2` gives `ghosts.py`: BFS, the targeting rules, the mode timer and
the ghost state machine, as stubs with 13 tests. Fitting them into your game (speeds, the
house, drawing, collisions) is your design at `/grill-me`.

## 1. Breadth-first search

"What's the shortest way from here to there through the maze?" BFS answers it by exploring
outwards in rings: every tile 1 step away, then every tile 2 steps away, and so on. The
first time it reaches the goal, that path is a shortest one.

```python
from collections import deque

def bfs(neighbours, start, goal):
    came_from = {start: None}          # also serves as the "visited" set
    queue = deque([start])
    while queue:
        tile = queue.popleft()         # the oldest first: that's what makes it breadth-first
        if tile == goal:
            break
        for n in neighbours(tile):
            if n not in came_from:
                came_from[n] = tile
                queue.append(n)
    if goal not in came_from:
        return []
    path = []
    while goal != start:               # walk back from the goal
        path.append(goal)
        goal = came_from[goal]
    return path[::-1]
```

Run it on a little grid:

```python
open_tiles = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)}   # a U shape

def neighbours(t):
    c, r = t
    return [n for n in ((c, r - 1), (c - 1, r), (c, r + 1), (c + 1, r)) if n in open_tiles]

bfs(neighbours, (0, 0), (0, 2))     # [(1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
```

`neighbours` is a **function you pass in**, so the same BFS works on any grid, the real
maze or a test grid. Your scaffold's `bfs_path` has this shape. The real game uses BFS for
the *eaten* ghosts: their eyes take the shortest path home.

## 2. How arcade ghosts really choose

Surprisingly, the 1980 ghosts **don't** use BFS to chase you. At every tile they make one
greedy choice:

1. Look at the open directions, **except straight back** (ghosts never reverse on their own).
2. Pick the one whose next tile is closest, in a straight line, to a **target tile**.
3. Break ties in the order up, left, down, right.

That's `choose_direction`. It's cheap, predictable, and occasionally dumb: a ghost will
take a long way round a wall because the first step *looked* closer. Skilled players
exploit exactly that. All the personality comes from **which target tile** each ghost picks.

## 3. Four personalities, four targets

| Ghost | Chase target |
|---|---|
| **Blinky** (red) | Pac-Man's tile. Relentless. |
| **Pinky** (pink) | 4 tiles ahead of Pac-Man. Ambushes from in front. |
| **Inky** (cyan) | Take the tile 2 ahead of Pac-Man; the target is that tile *plus the vector from Blinky to it*. Teams up with Blinky to pincer. |
| **Clyde** (orange) | Chases like Blinky when more than 8 tiles away, retreats to his corner when closer. Shy. |

Inky as vectors (Lesson 11.3): `pivot = pac + 2·dir`, then `target = pivot + (pivot − blinky) = 2·pivot − blinky`.

Comparing distances needs no square roots: if `a² < b²` then `a < b`, so `distance2`
(squared distance) is enough, and it's exact with integers.

## 4. Modes: scatter, chase, frightened

Ghosts alternate between **chase** (use the targets above) and **scatter** (each heads for its
own corner and circles there), on a fixed schedule: scatter 7 s, chase 20 s, scatter 7 s,
chase 20 s, scatter 5 s, chase 20 s, scatter 5 s, then chase for ever. Scatter phases are
breathing room for the player. Ghosts **reverse direction** at every mode change, the one
time they're allowed to: an attentive player can see a switch coming.

Eating a power pellet makes them **frightened** for a few seconds: blue, slow, wandering
randomly, and edible. The schedule **pauses** while they're frightened and resumes
afterwards. That's `ModeTimer`, another accumulator with a table of durations.

## 5. Each ghost's own state

Separately from the global mode, every ghost has a state:

```text
house ──release──▶ active ◀──timeout── frightened
                     │                    │
                     └───────power───────▶│
                                     caught (eaten by Pac-Man)
                                          ▼
house ◀──────────home─────────────────  eaten  (just eyes, racing home by BFS)
```

The same transition-table pattern as Breakout (Lesson 9.2). One thing that trips everyone
up: when the eyes arrive home, the ghost is **in the house**, a place where active ghosts
can't walk. Switch it to `house`, then route it out through the door exactly as at the
start of the level. If you flip it straight to `active`, it's stuck in a room it isn't
allowed to be in. Eating ghosts during one power pellet scores 200, 400, 800, then 1600.

## 6. How it's checked

- **W12.2.a**: `/grill-me W12.2` (speeds per state, release timing, frightened movement,
  collisions, the house).
- **W12.2.b–c**: a demo: the four personalities, visible scatter phases, power pellets, eyes going home.
- **W12.2.d**: `/verify W12.2`: the scaffold's 13 tests, plus the tutor's tests for your integration.
- **W12.2.e**: `walkthrough.md`: explain one ghost's behaviour from rule to screen.

## Pitfalls

- Ghosts reversing whenever it looks shorter (they mustn't, except at a mode change).
- Ties broken in the wrong order: ghosts pick odd routes at crossroads.
- `math.dist` or square roots where squared distance would do, in a hot loop.
- An eaten ghost made active while still inside the house.
- A mode timer that keeps running while the ghosts are frightened.
