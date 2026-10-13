# Lists and Iterables

A list holds many values in order. Most real programs are loops over lists: lines
in a file, rows in a table, sprites in a game. This lesson covers building,
slicing and walking lists, then writing those loops more clearly as
**comprehensions**.

## 1. Building lists

```python
scores = [72, 95, 88]
scores.append(61)          # add one item at the end   -> [72, 95, 88, 61]
scores.extend([70, 80])    # add every item from another list
scores.insert(0, 100)      # put 100 at index 0
last = scores.pop()        # remove and return the last item (80)
len(scores)                # 6
```

Indexes start at **0**. Negative indexes count from the end: `scores[-1]` is the
last item.

```python
>>> scores = [72, 95, 88]
>>> scores[3]
IndexError: list index out of range
```

A list of 3 items has indexes 0, 1 and 2. That `IndexError` is on the week's pitfall watch.

## 2. Slicing

`items[start:stop]` gives a **new** list from `start` up to, but not including,
`stop`. Either end can be left out:

```python
letters = ["a", "b", "c", "d", "e"]
letters[1:3]     # ['b', 'c']
letters[:2]      # ['a', 'b']      the first two
letters[-2:]     # ['d', 'e']      the last two
letters[::2]     # ['a', 'c', 'e'] every second item
letters[::-1]    # ['e', 'd', 'c', 'b', 'a']
```

Slicing never raises `IndexError`: `letters[3:100]` is just `['d', 'e']`.

**Try it:** in `uv run python`, make `letters` and predict each slice *before* you
press Enter.

## 3. `for` loops, `enumerate` and `zip`

```python
for score in scores:
    print(score)
```

Need the position too? Don't write `range(len(scores))`; use `enumerate`:

```python
for i, score in enumerate(scores, start=1):
    print(f"{i}. {score}")
```

Walking two lists side by side? `zip` pairs them up, and stops at the shorter one:

```python
names = ["Ada", "Grace", "Linus"]
scores = [95, 88, 72]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

`range` makes the numbers to loop over: `range(5)` is 0–4, `range(2, 10, 2)` is 2, 4, 6, 8.

## 4. Don't change a list while you loop over it

```python
nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)
print(nums)        # [1, 2, 3]: one 2 survived!
```

Removing an item shifts the rest left, so the loop skips the next one. Build a
**new** list instead:

```python
nums = [n for n in nums if n != 2]
```

## 5. List comprehensions

This loop pattern is everywhere:

```python
squares = []
for n in range(10):
    if n % 2 == 0:
        squares.append(n * n)
```

A comprehension says the same thing in one line, in the order you'd say it out loud,
"n squared, for each n in range(10), if n is even":

```python
squares = [n * n for n in range(10) if n % 2 == 0]
```

The shape is `[expression for item in iterable if condition]`; the `if` is optional.
Comprehensions are for *building a list*. If the loop body prints or saves files,
keep a normal `for` loop.

## 6. Your turn

**W2.1.a (tutor check):** in a scratch file, `week2/t2.1-lists/practice.py`, show the
tutor slicing, `append`, a loop with `enumerate`, and one with `zip`.

**W2.1.b (tests):** run `epochzero-tutor scaffold W2.1`. You get:

- `loops.py`: three working functions written as `for` loops. Don't change it.
- `comprehensions.py`: the same three functions as stubs. Rewrite each one as a
  single list comprehension.
- `test_comprehensions.py`: checks that your versions give exactly the same
  output as the loop versions on many inputs, including empty lists.

Run the tests with **Ctrl/Cmd+Shift+Enter**; when they're green, ask for `/verify W2.1`.

## Pitfalls

- `IndexError: list index out of range`: the last index is `len(items) - 1`.
- Modifying a list while iterating over it (section 4).
- Naming a variable `list`: after `list = [1, 2]`, calling `list("abc")` fails.
- `zip` silently drops extras when the lists have different lengths.
