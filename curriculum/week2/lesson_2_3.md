# Interactive Terminal Menu

Your second project: a real terminal app with an arrow-key menu, coloured output, a
table and a progress bar. The design lesson underneath matters more than the
colours: **keep the logic apart from the input/output**, so the logic can be tested
and the screen can change freely.

Pick what the app manages at `/grill-me`. Good options:

- **Task list:** add, complete, list, and show progress (done / total)
- **Reading log:** books, pages read, a progress bar per book
- **Gym log:** exercises, sets and reps, a weekly summary table

Below, the examples use a task list.

## 1. Install the libraries

In the cockpit terminal:

```sh
uv add inquirer rich
```

## 2. An arrow-key menu with `inquirer`

```python
import inquirer

choice = inquirer.list_input(
    "What next?",
    choices=["Add task", "List tasks", "Complete a task", "Quit"],
)
```

`list_input` shows the menu, lets the user move with ↑/↓ and choose with Enter, and returns
the chosen string. Free text:

```python
title = inquirer.text(message="Task title")
```

These prompts need a real terminal, so run the app in the cockpit (**Ctrl/Cmd+Enter**),
not through Claude Code's Bash.

## 3. Output with `rich`

```python
from rich.console import Console
from rich.table import Table

console = Console()
console.print("[bold green]Saved![/] 3 tasks left")

table = Table(title="Tasks")
table.add_column("#", justify="right")
table.add_column("Task")
table.add_column("Done")
table.add_row("1", "Write tests", "✓")
console.print(table)
```

The square-bracket markup sets style: `[bold]`, `[red]`, `[dim]`, and `[/]` to close.
For a progress bar over a loop, `rich.progress.track`:

```python
import time
from rich.progress import track

for _ in track(range(20), description="Saving..."):
    time.sleep(0.05)
```

To *show* progress as a fraction (3 of 5 done), a bar made with
`rich.progress.Progress` or a simple `"█" * done + "░" * (total - done)` works fine.

## 4. Separate logic from I/O

This is the heart of the project. Compare two functions:

```python
# Hard to test: it asks, it decides, and it prints, all at once
def complete_task(tasks):
    n = int(input("Which task? "))
    tasks[n - 1]["done"] = True
    print("Done!")

# Easy to test: data in, data out
def complete(tasks: list[dict], index: int) -> list[dict]:
    """Return a new list with task `index` (0-based) marked done.
    Raises IndexError for a bad index."""
    ...
```

The second one is **pure**: no `input()`, no `print()`, and it doesn't change its
argument. A test can call it with any list and check the result. The menu code
becomes a thin layer: ask, call the pure function, show the result.

A good layout:

```text
week2/t2.3-menu/
    tasks.py        pure functions: add, complete, remove, progress
    app.py          the menu loop: inquirer in, rich out
    test_tasks.py   tests for tasks.py only
```

## 5. Ctrl+C: exit cleanly

When the user presses **Ctrl+C**, Python raises `KeyboardInterrupt` wherever the
program happens to be. Without handling it, they see a long traceback. Catch it once,
around the whole loop:

```python
def main() -> None:
    try:
        run_menu()
    except KeyboardInterrupt:
        console.print("\n[dim]Bye![/]")
```

> `inquirer.list_input` and `inquirer.text` pass Ctrl+C on to you as `KeyboardInterrupt`.
> `inquirer.prompt([...])` is different: it catches Ctrl+C itself, prints
> "Cancelled by user" and returns `None`. If you use `prompt`, check for `None`,
> or pass `raise_keyboard_interrupt=True`.

**Try it:** run your app and press Ctrl+C at the menu, then again while typing a title.
Both should say goodbye, with no traceback.

## 6. How it's checked

- **W2.3.a**: `/grill-me W2.3`, then approve the plan.
- **W2.3.b–c** (tutor checks): a demo in the cockpit terminal. Arrow keys work, there's
  colour, a table and a progress bar, and Ctrl+C exits cleanly.
- **W2.3.d**: the tutor writes `test_tasks.py` from your plan (tests first), and
  `/verify W2.3` runs it. The manual run is part of the same check.
- **W2.3.e**: `walkthrough.md`.

## Pitfalls

- `input()` or `print()` inside the pure functions. Then they can't be tested.
- Changing the list passed in instead of returning a new one (see Lesson 2.2 on mutability).
- An index from the user used as-is: people count from 1, lists from 0.
- A bare `except:` around the menu. It catches Ctrl+C *and* your bugs.
