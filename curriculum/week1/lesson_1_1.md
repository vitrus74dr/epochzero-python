# Environment & Hello World

You'll set up a Python project, write your first interactive script, and meet the bug
that catches every beginner: text that looks like a number but isn't one.

## 1. A project for your work

Everything you write lives in `workspace/`. Make it a **uv** project pinned to
Python 3.12, with pytest available for tests. Open the cockpit terminal
(workbench ▸ shell; it starts in `workspace/`) and run:

```sh
uv init --bare --no-workspace --python 3.12
uv add --dev pytest
uv run python --version
```

- `uv init --bare` writes a `pyproject.toml` that describes the project.
  `--no-workspace` keeps it separate from PYGRID's own project in the folder above. Without
  it, uv would join the two, and your packages would be installed into the cockpit itself.
- `uv add --dev pytest` installs pytest into the project's own environment, not
  into your system Python.
- The last line should print `Python 3.12.x`.

Each task gets its own folder, named after the task. This one is `week1/t1.1-hello/`.
Ask the tutor to set it up (`pygrid-tutor scaffold W1.1` copies in the starter file
and its tests), then open `hello.py` in the workbench.

## 2. Talking to the user: `print()` and `input()`

```python
name = input("What's your name? ")
print("Hello,", name)
```

`input()` shows its prompt, waits for the user to press Enter, and gives back what
they typed. `print()` writes its arguments separated by spaces.

> `input()` **always** gives back a string, even when the user types `36`.
> Remember this; section 4 is about it.

## 3. f-strings

An f-string puts values straight into text. Prefix the quote with `f`, then put any
expression in braces:

```python
name = "Ada"
print(f"Hello, {name}!")             # Hello, Ada!
print(f"{name.upper()} has {len(name)} letters")   # ADA has 3 letters
print(f"2 + 3 = {2 + 3}")            # 2 + 3 = 5
```

## 4. Types: the classic bug

```python
age = input("How old are you? ")   # you type 36
print(age + 1)
```

```text
TypeError: can only concatenate str (not "int") to str
```

`age` is the string `"36"`, not the number `36`. Python won't guess whether you
meant text or arithmetic, so it refuses. Ask Python what you've got with `type()`:

```python
>>> age = "36"          # what input() gave back
>>> type(age)
<class 'str'>
>>> type(int(age))
<class 'int'>
```

Convert **before** doing arithmetic:

| Expression | Result | Why |
|---|---|---|
| `"3" + "4"` | `"34"` | `+` on strings joins them |
| `3 + 4` | `7` | `+` on numbers adds |
| `int("3") + 4` | `7` | converted first |
| `"3" * 2` | `"33"` | `*` on a string repeats it |
| `int("three")` | `ValueError` | not a number; Task 1.3 deals with this |

The sneakiest version raises no error at all: `"36" + "1"` happily gives `"361"`.

**Try it** in the terminal: run `uv run python` and type each line from the table.
Type `exit()` to leave.

## 5. Your script

Fill in `main()` in `hello.py` so a run looks like this:

```text
What's your name? Ada
How old are you? 36
Hello, Ada! Next year you'll be 37.
```

Run it with **Ctrl/Cmd+Enter**. The file ends with:

```python
if __name__ == "__main__":
    main()
```

This calls `main()` when you *run* the file, but not when the tests *import* it.
The tests need to call `main()` themselves, with a fake keyboard.

## 6. How this task is checked

- **W1.1.a**: show the tutor `uv run python --version` and your `week1/` folder.
- **W1.1.b**: the tutor reads `hello.py`: `print()`, `input()`, an f-string.
- **W1.1.c**: `test_hello.py` replaces `input()` with a fake that answers `"Ada"`
  and `"36"`, then checks your output says `37` and never `361`. Run the tests
  yourself with **Ctrl/Cmd+Shift+Enter**. When they pass, ask the tutor to `/verify W1.1`.

## Pitfalls

- **Missing colon:** `def main()` without `:` is a `SyntaxError`.
- **Tabs and spaces mixed:** the editor indents with 4 spaces. Pasted code may bring
  tabs, which gives `TabError`.
- **Shadowing a built-in:** `input = input("Name? ")` works once. After that,
  `input` is a string and the next `input(...)` call fails with
  `TypeError: 'str' object is not callable`. Don't name variables `input`, `str`,
  `list` or `sum`.
