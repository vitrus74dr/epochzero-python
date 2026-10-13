# Dictionaries and Data Mapping

A dictionary maps **keys** to **values**: a word to its count, a username to a
profile, a country to its capital. Looking up a key is fast however big the dict
gets. This lesson also covers the idea behind half of all beginner bugs:
**mutability**, and what it means for two names to refer to the same object.

## 1. Basics

```python
capitals = {"France": "Paris", "Japan": "Tokyo"}
capitals["Peru"] = "Lima"          # add or replace
capitals["Japan"]                  # 'Tokyo'
"Peru" in capitals                 # True  (checks keys)
del capitals["France"]
len(capitals)                      # 2
```

A missing key raises `KeyError`. When a missing key is normal, use `.get()` with a default:

```python
>>> capitals["Chile"]
KeyError: 'Chile'
>>> capitals.get("Chile", "unknown")
'unknown'
```

Loop over the pairs with `.items()`:

```python
for country, city in capitals.items():
    print(f"{city} is the capital of {country}")
```

## 2. Counting with a dict

The classic: count words.

```python
text = "the cat and the hat"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
# {'the': 2, 'cat': 1, 'and': 1, 'hat': 1}
```

`counts.get(word, 0)` means "the count so far, or 0 the first time we see it".

## 3. Nested data

Real data is dicts inside lists inside dicts. JSON from a web API (Week 4) looks exactly like this:

```python
library = {
    "owner": "Ada",
    "books": [
        {"title": "Dune", "year": 1965, "tags": ["sci-fi"]},
        {"title": "Emma", "year": 1815, "tags": ["classic", "romance"]},
    ],
}
library["books"][1]["tags"][0]            # 'classic'
[b["title"] for b in library["books"] if b["year"] > 1900]   # ['Dune']
```

Read a long lookup from left to right, one step at a time: the dict, then its
`"books"` list, then item 1, then its `"tags"`, then item 0.

## 4. Names point at objects

`b = a` doesn't copy anything. It makes `b` a second name for the **same** object:

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)        # [1, 2, 3, 4]: there is only one list
```

Lists, dicts and sets are **mutable**: they can change in place. Strings, numbers
and tuples are **immutable**: "changing" one makes a new object, so this surprise
can't happen with them.

To get an independent copy, ask for one: `a.copy()`, `list(a)` or `a[:]`. For
nested data use `copy.deepcopy`, because a plain copy shares the inner lists.

## 5. `is` vs `==`

- `==` asks: **equal values?**
- `is` asks: **the very same object?**

```python
>>> a = [1, 2]
>>> b = [1, 2]
>>> a == b
True
>>> a is b
False
```

Use `is` only for `None` (`if result is None:`). For everything else use `==`.

## 6. The mutable default argument

This looks innocent:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

add_item("apple")     # ['apple']
add_item("pear")      # ['apple', 'pear']  ← where did the apple come from?
```

The default `[]` is created **once**, when Python reads the `def`, and then shared by
every call. Use `None` as the default and make a new list inside:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket
```

**Try it:** paste the first version into `uv run python` and call it three times.
Then fix it.

## 7. Your turn

**W2.2.a (tutor check):** write `week2/t2.2-dicts/wordcount.py`. Read a paragraph with
`input()`, count the words (lower-case them and strip `.,!?`), and print the five most
common, most common first. Hint: `sorted(counts.items(), key=..., reverse=True)`;
look up what `key=` takes. Show the tutor the output and talk through how you used `.get()`.

**W2.2.b (quiz):** five questions on mutability, `is` vs `==` and mutable defaults. You
need 4/5. Take it in the [quiz view](#/quiz/W2.2.quiz) or with `epochzero-quiz W2.2.quiz`.

## Pitfalls

- `KeyError` on a key that might be missing: use `.get()` or `in`.
- Mutable default arguments (section 6).
- `is` used for strings or numbers. It can *seem* to work, which makes the bug worse.
- Shadowing built-ins: a variable called `dict`, `id` or `str` breaks the built-in.
