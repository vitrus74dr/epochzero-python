# Classes & Instances

So far your data has been lists and dicts, with separate functions that work on
them. A **class** bundles the data and the functions that belong to it into one
thing, an object. Every game sprite you'll make in Weeks 5–12 is an object.

## 1. A first class

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def birthday(self):
        self.age += 1
        return f"Happy birthday, {self.name}! Now {self.age}."


rex = Dog("Rex", 3)
fido = Dog("Fido", 7)
rex.birthday()       # 'Happy birthday, Rex! Now 4.'
fido.age             # 7: each dog has its own age
```

- `class Dog:` defines a new type. `Dog("Rex", 3)` makes an **instance** of it.
- `__init__` runs when the instance is created, and sets up its starting data.
- `self` is the instance itself. `rex.birthday()` is really `Dog.birthday(rex)`, so
  inside the method `self` *is* `rex`.
- `self.name = name` creates an **instance attribute**: data stored on this one object.

## 2. Forgetting `self`

```python
class Counter:
    def __init__(self):
        self.count = 0

    def add(self):
        count += 1        # forgot self.
```

```text
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

Inside a method, a bare `count` is a local variable. The object's data is always
`self.count`. And if you leave `self` out of the `def` line itself, calling the method
gives `TypeError: Counter.add() takes 0 positional arguments but 1 was given`, because
Python always passes the instance as the first argument.

## 3. `__repr__`: how an object shows itself

```python fragment
>>> rex
<__main__.Dog object at 0x7f3a...>
```

That's not much help when debugging. Add a `__repr__` method that returns a string:

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Dog(name={self.name!r}, age={self.age})"
```

```python
>>> Dog("Rex", 3)
Dog(name='Rex', age=3)
```

`!r` inside an f-string uses `repr()`, so strings show their quotes. A good `__repr__`
looks like the code that would recreate the object.

## 4. Class attributes vs instance attributes

An attribute set in the class body is shared by **every** instance:

```python
class Dog:
    species = "Canis familiaris"     # class attribute: one copy, shared
    tricks = []                      # ⚠ also shared!

    def __init__(self, name):
        self.name = name             # instance attribute: one per dog

    def learn(self, trick):
        self.tricks.append(trick)


a = Dog("Rex")
b = Dog("Fido")
a.learn("sit")
print(b.tricks)        # ['sit']: Fido "learned" it too
```

`self.tricks.append(...)` finds `tricks` on the *class*, because the instance doesn't
have its own. A shared list is the same bug as Week 2's mutable default argument. Fix
it by giving each instance its own list in `__init__`: `self.tricks = []`.

Rule of thumb: constants can live on the class; anything that changes goes in `__init__`.

## 5. Your turn (W3.1.a)

Write `week3/t3.1-classes/bank.py` with a `BankAccount` class:

- `__init__(self, owner, balance=0)`
- `deposit(amount)` and `withdraw(amount)`. Withdrawing more than the balance raises
  `ValueError("insufficient funds")`, and so does a negative amount.
- `__repr__` returning something like `BankAccount(owner='Ada', balance=50)`
- a `history` list of every transaction, one per account (section 4!)

Try it in the terminal (`uv run python -i bank.py` drops you into Python with your
class loaded). Then show the tutor two accounts proving their histories are separate.

## Pitfalls

- Forgetting `self.` in front of attributes, or `self` in the `def` line.
- Mutable class attributes shared across instances (section 4).
- Naming a class in lower case. `Dog`, not `dog`: classes are CapWords by convention.
