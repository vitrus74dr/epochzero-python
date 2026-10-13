# Control Flow & Logic

Programs make decisions and repeat work. This lesson covers the two tools for that,
`if` and `while`, and the logic that drives them: booleans, `and`/`or`/`not`, and
**truthiness**.

## 1. Comparisons give booleans

```python
>>> 7 > 3
True
>>> "abc" == "abc"
True
>>> 0 < 5 < 10        # comparisons chain
True
```

`==`, `!=`, `<`, `<=`, `>`, `>=` each give `True` or `False`.

> `=` **assigns**, `==` **compares**. `if x = 5:` is a `SyntaxError`, and Python
> even suggests `==`.

## 2. `and`, `or`, `not`

| `a` | `b` | `a and b` | `a or b` |
|---|---|---|---|
| True | True | True | True |
| True | False | False | True |
| False | True | False | True |
| False | False | False | False |

`not` flips a value: `not True` is `False`.

Python stops as soon as it knows the answer (*short-circuiting*). And `and`/`or` give
back **one of their operands**, not necessarily `True` or `False`:

```python
>>> 0 or "default"
'default'
>>> "" or "stranger"
'stranger'
>>> 3 and 4
4
```

So `name = typed or "stranger"` is a common way to give a default.

## 3. Truthiness

`if` doesn't need a boolean. It asks whether a value is *truthy*. These are
**falsy**; everything else is truthy:

```python fragment
False   None   0   0.0   ""   []   {}   ()   set()
```

Truthy things that surprise people: `"0"`, `" "`, `"False"`, `[0]`. Each is a
non-empty string or list.

```python
items = []
if items:                 # the idiomatic "is the list non-empty?"
    print("got some")
```

## 4. `if` / `elif` / `else`

Python checks the conditions in order and runs **only the first** branch that's true:

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
```

**Order matters.** Put `score >= 70` first and every score from 70 up gets a C.

The classic logic bug:

```python fragment
if answer == "y" or "yes":    # always true!
```

That reads as `(answer == "y") or ("yes")`, and `"yes"` is truthy. Write
`answer == "y" or answer == "yes"`, or `answer in ("y", "yes")`.

## 5. `while` loops

A `while` loop repeats as long as its condition is truthy. Something inside the loop
must eventually make the condition false. That's the **exit condition**.

```python
command = ""
while command != "quit":
    command = input("> ")
    print(f"you typed {command!r}")
```

If you forget to change `command`, the loop runs forever. Stop it with **Ctrl+C** in
the terminal.

When the exit check belongs in the middle of the loop, use `while True:` with `break`:

```python
while True:
    command = input("> ")
    if command == "quit":
        break
    print(f"you typed {command!r}")
```

You'll use exactly this shape in the calculator.

## 6. Your turn (W1.2.a)

Write `week1/t1.2-guess/guess.py`: a number-guessing game.

- The secret number is fixed (say `7`); there's no need for `random` yet.
- Each turn, ask for a guess and answer *too low*, *too high* or *correct*, using
  `if`/`elif`/`else`.
- Stop when the guess is right, **or** when the user types `q`.
- Decide what happens when they type something that isn't a number. You know enough
  from Task 1.1 to spot the problem; Task 1.3 gives you the tool to handle it.

Show it to the tutor when it runs. This item is a tutor check.

## 7. Quiz (W1.2.b)

Five questions on boolean logic and truthiness; you need **4/5**. Take it in the
[quiz view](#/quiz/W1.2.quiz) (keys `1`–`4`, then `Enter`), or run `epochzero-quiz W1.2.quiz`
in the cockpit terminal. Missed questions aren't explained on screen: talk them
through with the tutor, then retake.

## Pitfalls

- A missing `:` after `if`, `elif`, `else` or `while`.
- `=` where you meant `==`.
- `x == 1 or 2` is always truthy (see section 4).
- A `while` loop whose condition never changes.
