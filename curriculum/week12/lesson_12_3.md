# Ship It

A game isn't finished when it works; it's finished when someone else can enjoy it. This
last task turns your Pac-Man into a complete, polished game, and closes the course with a
real play-test.

## 1. The game around the game

The tracker asks for these (W12.3.a). Each one reuses something you've built before:

| Feature | How | Seen in |
|---|---|---|
| **Lives** | lose one when an active ghost reaches Pac-Man's tile; reset positions, keep the pellets | Asteroids respawn |
| **Levels** | maze cleared: reload it, raise Pac-Man's and the ghosts' speed, shorten the frightened time | Tetris levels |
| **Fruit bonus** | after 70 and 170 pellets, a fruit appears below the house for ~10 s (100, 300, 500... points) | Snake food |
| **High score** | JSON next to the game, `Path(__file__).parent` | Snake, Lesson 4.1 |
| **States** | ready → playing → dying → level complete → game over | Breakout, Lesson 9.2 |

Use `arcade.View`s or your own state machine for the screens: a "READY!" pause before
play, a short freeze when Pac-Man is caught, and a game-over screen showing the high score.

## 2. One command to run it

Someone downloading your game should need one command. Give the workspace project an
entry point. In `pyproject.toml`:

```toml
[project.scripts]
pacman = "pacman:main"
```

Here `pacman:main` means "the `main` function in `pacman.py`". The code needs to be an
installable package for this to work. At `/grill-me`, decide with the tutor whether to
restructure the folder for it, or settle for `uv run python week12/t12.2-ghosts/pacman.py`. Both
count for W12.3.a, as long as a fresh clone runs with one command and no other setup.

Then check it the way a stranger would: a fresh copy of the folder, `uv sync`, run it. Does it
find `maze.txt` and the high-score file from *any* working directory (Lesson 6.3, section 3)?

## 3. Feel

The difference between "works" and "fun" is usually small and specific:

- **Sound:** `arcade.load_sound(":resources:sounds/coin1.wav")` once, then `arcade.play_sound(sound)`
  on each pellet. Use a different sound for power pellets and for being caught.
- **Pauses:** a 1-second freeze after eating a ghost (show its points where it was) makes it feel like an event.
- **Speed:** the 1980 Pac-Man slows down slightly while eating pellets, so clearing a corridor
  is slower than escaping down an empty one. Try it.
- **Frightened warning:** ghosts flash white for the last two seconds of fright.

## 4. The play-test (W12.3.b)

Play a complete game in the cockpit, from READY! to game over or level 2, while the tutor
watches through your descriptions and questions. Keep a list of everything odd: a ghost
stuck at a corner, a pellet you can't eat, a turn that didn't register. Then fix them
together, bug by bug: **write a failing test first** where you can (this is how professionals
fix bugs), then fix the code until the test passes.

## 5. Your course, in one game

Look at what's in your Pac-Man: text parsing (Week 1), lists, dicts and sets (Week 2),
classes and state (Week 3), files and JSON (Week 4), a game loop (Weeks 5–6), state machines
and collisions (Week 9), grids and ticks (Week 10), vectors (Week 11), and search (this
week). The tutor writes `CERTIFICATE.md` next (the completion item), drawing on everything you've done.

## Pitfalls

- Hard-coded relative paths that only work from one folder.
- Restarting the level from scratch when Pac-Man dies (the pellets eaten so far should stay eaten).
- Reloading sounds inside the update loop instead of once.
- Fixing a play-test bug without a test, then having it come back.
