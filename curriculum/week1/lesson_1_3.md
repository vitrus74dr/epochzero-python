# The Smart CLI Calculator

Your first project: a calculator that runs in the terminal, reads lines like `2 + 3`,
prints the answer, and keeps going until you type `exit`. The "smart" part is that
**nothing the user types can crash it**.

```text
> 2 + 3
5
> 10 / 4
2.5
> 5 / 0
can't divide by zero
> two + 3
'two' isn't a number
> exit
bye
```

How it's worded is up to you; the behaviour isn't.

## How a project runs here

1. **Design first.** Run `/grill-me W1.3` with the tutor. You answer 4–6 questions
   about your design, and the tutor writes `implementation_plan.md` from *your*
   answers. Read it via the `[ plan ]` link on the dashboard, then approve it.
2. **Tests first.** `pygrid-tutor scaffold W1.3` gives you `calculator.py` (just a
   stub) and `test_calculator.py`. The tutor adds tests for the functions in your plan.
3. **You write the code.** Run the tests often (**Ctrl/Cmd+Shift+Enter**). Red is
   normal while you work.
4. **Verify.** When everything is green, the tutor runs `/verify W1.3`, then `/checkoff`.
5. **Explain it.** The tutor writes `walkthrough.md`, and you explain one part of it
   back in your own words.

## New tools

### `str.split()`

```python
>>> "  2   +  3 ".split()
['2', '+', '3']
>>> "  2   +  3 ".split(" ")
['', '', '2', '', '', '+', '', '3', '']
```

With no argument, `split()` splits on any run of whitespace and drops the ends.
Unpacking checks the count for you, and complains if it's wrong:

```python
>>> a, op, b = "2 + 3".split()
>>> a, op, b = "2 +".split()
ValueError: not enough values to unpack (expected 3, got 2)
```

### Exceptions: `try` / `except`

Some operations fail at run time, and Python *raises* an exception:

```python
>>> float("abc")
ValueError: could not convert string to float: 'abc'
>>> 5 / 0
ZeroDivisionError: division by zero
```

You can catch the ones you expect, and carry on:

```python
text = "abc"
try:
    x = float(text)
except ValueError:
    print(f"{text!r} isn't a number")
```

Rules of thumb:

- **Catch specific exceptions.** A bare `except:` also swallows typos (`NameError`)
  and Ctrl+C (`KeyboardInterrupt`), which hides real bugs. It's on the pitfall watch.
- **Keep the `try` block small**, just the line that can fail. Then you know which
  failure you're handling.

### `pass`

`pass` is a statement that does nothing. It's for an *intentional* stub, like the
`main()` you'll start from. It is **not** for `except ValueError: pass`, which makes
an error vanish silently.

## Questions to think about before `/grill-me`

- `int` or `float`? What should `7 / 2` show? And `4 / 2`: `2` or `2.0`?
- Where does *parsing* end and *calculating* begin? Could one function take
  `"2 + 3"` and **return** the answer without printing anything? Why would that make
  it easier to test?
- What exactly does the user see for each kind of bad input?
- What about `exit ` with a trailing space, or `EXIT`?
- What about `1 + 2 + 3`: support it, or reject it with a helpful message?

## What the tests feed it

`test_calculator.py` drives your `main()` with a fake `input()`:

- `2 + 3`, `7 - 10`, `4 * 2.5`, `9 / 2`, and `   2    +   3  ` (extra spaces)
- letters (`abc`), a word for a number (`two + 3`), an empty line, only spaces
- `5 / 0`, an unknown operator (`2 ^ 3`), a missing operand (`2 +`), and `1 + 2 + 3`

After each bad line it sends `20 + 22` and expects to see `42`: the loop must carry
on. Then it sends `exit`, and `main()` must return without asking for anything else.

## Pitfalls

- A bare `except:`, or `except Exception: pass`.
- Putting the whole loop inside one giant `try`. One bad line then ends the program.
- `if op == "+" or "-":` (from Task 1.2: always truthy).
- `op is "+"` instead of `op == "+"`. Python warns about it (`SyntaxWarning`), because `is`
  asks "the same object?", not "the same text?". It can be `False` for equal strings.
  Use `is` only for `None`.
