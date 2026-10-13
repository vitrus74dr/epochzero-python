# 8-Week Interactive Python Mastery Curriculum

Source of truth for curriculum state. Read at the start of every session.

## Rules
- Item IDs (`[W1.1.a]`) are stable. Never renumber or reword an ID.
- An item may be ticked **only** when `progress/verifications.json` has a passing record for it (pytest run, quiz score ≥ pass mark, or a recorded tutor check).
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

---

## Completion
- [ ] [W8.Z.a] Tutor writes `CERTIFICATE.md`: the learner's journey, strengths, weak spots seen in quizzes and reviews, and next steps
