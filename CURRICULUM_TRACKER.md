# 12-Week Interactive Python Mastery Curriculum

The curriculum: weeks, tasks and items. A learner's ticks are kept in `progress/checked.json`,
not in this file (`epochzero-tutor status` shows both together).

## Rules
- Item IDs (`[W1.1.a]`) are stable. Never renumber or reword an ID.
- An item may be ticked **only** when `progress/verifications.jsonl` has a passing record for it (pytest run, quiz score ≥ pass mark, or a recorded tutor check).
- `[PROJECT]` tasks require `implementation_plan.md` (after `/grill-me`) before coding, and `walkthrough.md` after.
- A week unlocks only when every item in the previous week is ticked.
- Before writing any Arcade or scikit-learn lesson code, check the installed version's official docs.

---

## Week 1: Foundations & Interactive CLI
Focus: variables, types, control flow, terminal I/O.
Pitfalls monitored: missing colons, mixed tabs/spaces, `=` vs `==`, string + int concatenation.

### Task 1.1: Environment & Hello World
- [ ] [W1.1.a] Set up the environment with `uv`, Python 3.12, and a `workspace/week1` folder
- [ ] [W1.1.b] Write a script using `print()` and `input()` that greets the user with an f-string
- [ ] [W1.1.c] Verification: a pytest (monkeypatching `input`) confirms numeric input is converted before arithmetic, with no `TypeError`

### Task 1.2: Control Flow & Logic [QUIZ]
- [ ] [W1.2.a] Implement `if/elif/else` and a `while` loop with a clear exit condition
- [ ] [W1.2.b] Quiz: 5 questions on boolean logic and truthiness, with a score ≥ 4/5

### Task 1.3: The Smart CLI Calculator [PROJECT]
- [ ] [W1.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W1.3.b] `while True:` loop that breaks only on `exit`; parses `a op b`; handles `ZeroDivisionError` and `ValueError`; `pass` used only for intentional stubs
- [ ] [W1.3.c] Verification: pytest feeds edge cases (letters, empty input, `5 / 0`, extra spaces, unknown operator) and the program never crashes
- [ ] [W1.3.d] `walkthrough.md` written

---

## Week 2: Data Structures & Clean Code
Focus: lists, dicts, tuples, functions (DRY).
Pitfalls monitored: index out of range, mutable default arguments, shadowing built-ins (`list`, `str`, `id`), modifying a list while iterating.

### Task 2.1: Lists and Iterables
- [ ] [W2.1.a] Slicing, appending, and `for` loops, including `enumerate` and `zip`
- [ ] [W2.1.b] Refactor three loops into list comprehensions, with tests proving identical output

### Task 2.2: Dictionaries and Data Mapping
- [ ] [W2.2.a] Key-value mapping, `.get()` with defaults, and nested dicts
- [ ] [W2.2.b] Quiz: 5 questions on mutability, `is` vs `==`, and mutable defaults, with a score ≥ 4/5

### Task 2.3: Interactive Terminal Menu [PROJECT]
- [ ] [W2.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W2.3.b] `inquirer` menu navigable with arrow keys; `rich` output (color, bold, a progress bar)
- [ ] [W2.3.c] `KeyboardInterrupt` exits cleanly with a goodbye message, and logic is separated from I/O so it is testable
- [ ] [W2.3.d] Verification: pytest covers the pure functions, and a manual run in the cockpit terminal is recorded
- [ ] [W2.3.e] `walkthrough.md` written

---

## Week 3: Object-Oriented Programming
Focus: classes, inheritance, encapsulation.
Pitfalls monitored: forgetting `self`, class vs instance attributes, mutable class attributes shared across instances.

### Task 3.1: Classes & Instances
- [ ] [W3.1.a] `__init__`, `self`, instance variables, `__repr__`

### Task 3.2: Inheritance & Polymorphism
- [ ] [W3.2.a] Subclasses, method overriding, and `super()`
- [ ] [W3.2.b] Quiz: 5 questions on OOP, with a score ≥ 4/5

### Task 3.3: Leitner Flashcard Engine [PROJECT]
- [ ] [W3.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W3.3.b] `Card`, `Deck`, and `LeitnerSystem` classes; correct answers promote a box and extend the interval; wrong answers reset to box 1 (daily)
- [ ] [W3.3.c] `today` is injected as a parameter (no hidden `date.today()` calls) so scheduling is testable
- [ ] [W3.3.d] State saves to and loads from `data.json`; a round-trip test passes
- [ ] [W3.3.e] Verification: `test_flashcards.py` covers promotion, demotion, due-date logic, and persistence
- [ ] [W3.3.f] `walkthrough.md` written

### Task 3.4: Desktop App: Habit Tracker (Tkinter) [PROJECT]
- [ ] [W3.4.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W3.4.b] Tkinter window: add and remove habits, mark one done today, show each streak; the model classes know nothing about Tkinter
- [ ] [W3.4.c] Habits save to and load from JSON; streak logic takes `today` as a parameter
- [ ] [W3.4.d] Verification: pytest covers the model (streaks, gaps, persistence) without opening a window
- [ ] [W3.4.e] `walkthrough.md` written

---

## Week 4: File I/O, APIs, and Error Handling
Focus: files, `requests`, exceptions.
Pitfalls monitored: unclosed files (use `with`), bare `except:`, missing request timeouts.

### Task 4.1: Context Managers
- [ ] [W4.1.a] Read and write text and JSON with `with open(...)`, using an explicit `encoding="utf-8"`

### Task 4.2: Web Requests
- [ ] [W4.2.a] Fetch from a public REST API with `timeout=`, `raise_for_status()`, and JSON parsing

### Task 4.3: CLI Trivia Game [PROJECT]
- [ ] [W4.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W4.3.b] Fetch from Open Trivia DB; check `response_code`; `html.unescape` the text; shuffle the answers
- [ ] [W4.3.c] Track score and show `rich`-formatted feedback
- [ ] [W4.3.d] Handle `ConnectionError` and `Timeout` specifically, with a friendly retry or quit
- [ ] [W4.3.e] Verification: pytest mocks the HTTP layer (success, bad response_code, connection error, timeout)
- [ ] [W4.3.f] `walkthrough.md` written

### Task 4.4: Automation: File Organizer & Log Analyzer
- [ ] [W4.4.a] `organize.py`: an `argparse` CLI that sorts a folder's files into subfolders by type with `pathlib`, with `--dry-run` and safe handling of name clashes
- [ ] [W4.4.b] `logstats.py`: parse a log file with `re` and print a summary (count per level, most common errors, busiest hour)
- [ ] [W4.4.c] Verification: pytest uses `tmp_path` to cover sorting, clashes, dry-run, and log parsing

### Task 4.5: Data App: CSV Report with pandas
- [ ] [W4.5.a] Load a CSV with `pandas`; clean it (column types, missing values, duplicates) in a function that returns a new DataFrame
- [ ] [W4.5.b] Group and aggregate into a summary table, and save at least two `matplotlib` charts to PNG files (no `plt.show()` in the report path)
- [ ] [W4.5.c] Verification: pytest checks the cleaning and aggregation functions on a small DataFrame built inside the test

---

## Week 5: Graphics with Python Arcade
Focus: windows, the game loop, coordinates, drawing.
Pitfalls monitored: forgetting the origin is bottom-left; doing per-frame work in `on_draw` instead of `on_update`; tutorials written for an older Arcade API.

### Task 5.1: Arcade Initialization
- [ ] [W5.1.a] Subclass `arcade.Window`; call `self.clear()` in `on_draw`; understand the bottom-left origin

### Task 5.2: Drawing & Movement
- [ ] [W5.2.a] Draw primitives and load a texture (using current-version function names)
- [ ] [W5.2.b] Move an object with `on_key_press` / `on_key_release` plus `on_update(delta_time)`; start with `arcade.run()`

### Task 5.3: Animated Generative Art [PROJECT]
- [ ] [W5.3.a] `/grill-me` on the geometry (parametric curves, polar coordinates, easing); `implementation_plan.md` explains the math
- [ ] [W5.3.b] Animation driven by `delta_time` (frame-rate independent); at least one keyboard control changes parameters live
- [ ] [W5.3.c] Verification: pytest covers the pure math functions (point generation, color mapping) without opening a window
- [ ] [W5.3.d] `walkthrough.md` written

---

## Week 6: Game Development Capstone
Focus: sprites, collisions, physics.

### Task 6.1: Sprites and SpriteLists
- [ ] [W6.1.a] Create `arcade.Sprite` objects and batch them in a `SpriteList`

### Task 6.2: Physics Engine
- [ ] [W6.2.a] `arcade.PhysicsEnginePlatformer` with gravity, jumping, and wall/platform collisions (`PhysicsEngineSimple` is top-down only)

### Task 6.3: 2D Platformer [PROJECT]
- [ ] [W6.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W6.3.b] Player jumps, collides with walls, and collects coins that update the score
- [ ] [W6.3.c] At least 2 levels, enemies, and a win state
- [ ] [W6.3.d] Verification: pytest asserts every asset path resolves from `Path(__file__).parent` and that the level-loading logic is correct
- [ ] [W6.3.e] `walkthrough.md` written

---

## Week 7: Machine Learning Fundamentals (scikit-learn)
Focus: arrays, datasets, classification.

### Task 7.1: Datasets
- [ ] [W7.1.a] `load_iris()`: inspect `X`, `y`, shapes, and feature/target names

### Task 7.2: Basic Classifiers
- [ ] [W7.2.a] Train KNN or a Decision Tree with `train_test_split` (`random_state` and `stratify` set)
- [ ] [W7.2.b] Quiz: 5 questions on data leakage and train/test discipline, with a score ≥ 4/5

### Task 7.3: Handwritten Digit Recognizer [PROJECT]
- [ ] [W7.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W7.3.b] Train on `load_digits()`; scaling (if any) lives inside a `Pipeline`
- [ ] [W7.3.c] Classification report and confusion matrix printed as `rich` tables
- [ ] [W7.3.d] Verification: pytest asserts test accuracy beats a `DummyClassifier` by a clear margin
- [ ] [W7.3.e] `walkthrough.md` written

---

## Week 8: ML Pipelines
Focus: preprocessing, `ColumnTransformer`, `Pipeline`, tuning.

### Task 8.1: The Preprocessing Problem
- [ ] [W8.1.a] `StandardScaler` for numeric and `OneHotEncoder(handle_unknown="ignore")` for categorical data, on a small mixed-type DataFrame

### Task 8.2: Building the Pipeline
- [ ] [W8.2.a] `ColumnTransformer`, including understanding `remainder="passthrough"` vs `"drop"`
- [ ] [W8.2.b] Chain the preprocessor and estimator with `Pipeline` / `make_pipeline`

### Task 8.3: Health Predictor (Diabetes) [PROJECT]
- [ ] [W8.3.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W8.3.b] `load_diabetes(scaled=False, as_frame=True)`; `sex` one-hot encoded and the other features scaled, via `ColumnTransformer`
- [ ] [W8.3.c] `GridSearchCV` over the pipeline (e.g. `ridge__alpha`), fit on training data only
- [ ] [W8.3.d] Verification: the script runs end-to-end, and held-out R² is positive and beats a `DummyRegressor` baseline
- [ ] [W8.3.e] `walkthrough.md` written

### Task 8.4: Web App: Prediction Service (FastAPI + SQLite) [PROJECT]
- [ ] [W8.4.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W8.4.b] FastAPI app serving the saved Week 8 model: an HTML form page and a `POST /api/predict` JSON endpoint with a Pydantic request model
- [ ] [W8.4.c] Every prediction is stored in SQLite with parameterized queries (`?` placeholders, never f-strings); a history page lists the latest ones
- [ ] [W8.4.d] Verification: pytest uses FastAPI's `TestClient` to cover the form, the API (including invalid input → 422) and the database
- [ ] [W8.4.e] `walkthrough.md` written

---

## Week 9: Arcade Classics I: Pong & Breakout
Focus: the game loop, velocity, collisions, game states.
Pitfalls monitored: movement not scaled by `delta_time`; a fast ball tunnelling through a paddle; removing sprites from a `SpriteList` while iterating over it.

### Task 9.1: Pong
- [ ] [W9.1.a] Pure `physics.py`: ball motion scaled by `delta_time`, wall bounces, and a paddle bounce whose angle depends on where the ball hits
- [ ] [W9.1.b] Arcade game: two paddles (W/S and ↑/↓), a score, a serve after each point, and first to 7 wins
- [ ] [W9.1.c] Verification: pytest covers movement, bounces, scoring, and serving without opening a window

### Task 9.2: Breakout [PROJECT]
- [ ] [W9.2.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W9.2.b] Bricks built from a text level layout; paddle, lives, and at least 2 levels; the ball speeds up as bricks fall
- [ ] [W9.2.c] Game states (title, playing, paused, game over) as a class whose transitions are tested
- [ ] [W9.2.d] Verification: pytest covers which side of a brick was hit, brick removal, and level progression
- [ ] [W9.2.e] `walkthrough.md` written

### Task 9.3: Game Loops & Collisions [QUIZ]
- [ ] [W9.3.a] Quiz: 5 questions on `delta_time`, collision detection, and game states, with a score ≥ 4/5

---

## Week 10: Arcade Classics II: Snake & Tetris
Focus: grid games, fixed-tick updates, 2D lists, rotation.
Pitfalls monitored: mixing up (x, y) and (row, col); `[[0] * w] * h` aliasing every row; reversing into yourself within one tick.

### Task 10.1: Snake
- [ ] [W10.1.a] Pure grid model: the body as a `deque`, queued turns with no 180° reversal, growth, and wall and self collisions
- [ ] [W10.1.b] Arcade front end on a fixed tick independent of frame rate; food never spawns on the snake (the random generator is injected); the high score is saved to JSON
- [ ] [W10.1.c] Verification: pytest covers movement, turning rules, growth, collisions, and food placement

### Task 10.2: Tetris [PROJECT]
- [ ] [W10.2.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W10.2.b] Board and tetromino model: movement, rotation with simple wall kicks, collision, locking, and line clearing with scoring
- [ ] [W10.2.c] A 7-bag randomizer with an injected random generator; gravity speeds up per level; hard drop and a next-piece preview
- [ ] [W10.2.d] Verification: pytest covers rotation, kicks, single and multiple line clears, and game over
- [ ] [W10.2.e] `walkthrough.md` written

---

## Week 11: Arcade Classics III: Space Invaders & Asteroids
Focus: sprite lists, spawning and removal, vectors, screen wrap.
Pitfalls monitored: degrees vs radians; bullet lists that grow forever; removing sprites while iterating.

### Task 11.1: Space Invaders
- [ ] [W11.1.a] Pure formation logic: the march, the step down at an edge, and speeding up as invaders die
- [ ] [W11.1.b] Arcade game: player cannon with one bullet on screen at a time, invader bombs, shields that wear away, and waves
- [ ] [W11.1.c] Verification: pytest covers the march, edge turns, speed-up, and wave reset

### Task 11.2: Asteroids [PROJECT]
- [ ] [W11.2.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W11.2.b] Ship with rotation, thrust, and inertia using vector maths (`math.cos`/`math.sin` in radians), with wrap-around at the screen edges
- [ ] [W11.2.c] Asteroids split large → medium → small; bullets expire; lives, and a short invulnerability after respawning
- [ ] [W11.2.d] Verification: pytest covers vector motion, wrap-around, splitting, and bullet lifetime
- [ ] [W11.2.e] `walkthrough.md` written

### Task 11.3: Vectors & Sprite Lists [QUIZ]
- [ ] [W11.3.a] Quiz: 5 questions on vectors, angles, and sprite-list management, with a score ≥ 4/5

---

## Week 12: Capstone: Pac-Man
Focus: tile maps, pathfinding, state machines, game AI.
Pitfalls monitored: off-by-one between tile and pixel coordinates; turning when not centred on a tile; ghosts reversing through each other's logic.

### Task 12.1: The Maze & Pac-Man
- [ ] [W12.1.a] Load the maze from a text map: walls, pellets, power pellets, the ghost house, and the side tunnel; convert between tile and pixel coordinates
- [ ] [W12.1.b] Pac-Man moves tile to tile with a buffered next turn, eats pellets for points, and wraps through the tunnel
- [ ] [W12.1.c] Verification: pytest covers map loading, coordinate conversion, buffered turns, and pellet eating

### Task 12.2: Ghosts [PROJECT]
- [ ] [W12.2.a] `/grill-me` held and `implementation_plan.md` approved
- [ ] [W12.2.b] Breadth-first search over the maze, and the four ghost targeting rules (Blinky, Pinky, Inky, Clyde)
- [ ] [W12.2.c] Ghost modes as a state machine: scatter/chase timers, frightened after a power pellet, eaten → return to the house
- [ ] [W12.2.d] Verification: pytest covers shortest paths, each ghost's target tile, and mode transitions
- [ ] [W12.2.e] `walkthrough.md` written

### Task 12.3: Ship It
- [ ] [W12.3.a] Lives, levels that speed up, fruit bonus, and a saved high score; the game starts with one `uv run` command
- [ ] [W12.3.b] Playtest with the tutor: demo a full game in the cockpit, then fix the bugs you found together

---

## Completion
- [ ] [W8.Z.a] Tutor writes `CERTIFICATE.md`: the learner's journey, strengths, weak spots seen in quizzes and reviews, and next steps
