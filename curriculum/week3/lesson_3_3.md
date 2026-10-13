# Leitner Flashcard Engine

A flashcard app that schedules reviews the way memory actually works: cards you know
come back rarely, cards you miss come back tomorrow. It's the first project where
**time** is part of the logic, and that raises a testing problem worth solving properly.

## 1. The Leitner system

Cards live in numbered boxes. Each box has a review interval:

| Box | Review every |
|---|---|
| 1 | 1 day |
| 2 | 2 days |
| 3 | 4 days |
| 4 | 8 days |
| 5 | 16 days |

- Answer **correctly**: the card moves up one box (it stays in 5 if it's already
  there), and its next review is `today + interval`.
- Answer **wrong**: the card goes back to box 1, due tomorrow.
- A card is **due** when its due date is on or before today.

(You choose the exact intervals at `/grill-me`; doubling is a common choice.)

## 2. Dates in Python

```python
from datetime import date, timedelta

today = date(2026, 10, 13)
today + timedelta(days=4)          # datetime.date(2026, 10, 17)
date(2026, 10, 17) <= today        # False
date.fromisoformat("2026-10-17")   # back from a string
today.isoformat()                  # '2026-10-13', for saving to JSON
```

## 3. The testing problem: hidden `date.today()`

```python fragment
def is_due(self):
    return self.due <= date.today()     # ⚠ depends on when you run the test
```

A test for this passes today and fails next week, and you can't test "what happens in
8 days" without waiting 8 days. The fix: **inject** the date. The caller passes it in:

```python fragment
def is_due(self, today: date) -> bool:
    return self.due <= today
```

Now a test can ask about any day it likes:

```python fragment
def test_promoted_card_waits_two_days():
    system = LeitnerSystem(...)
    day1 = date(2026, 1, 1)
    system.answer(card, correct=True, today=day1)
    assert not card.is_due(day1 + timedelta(days=1))
    assert card.is_due(day1 + timedelta(days=2))
```

Only the outermost layer, the part that talks to the user, calls `date.today()` once
and passes it down. This is W3.3.c.

## 4. Three classes, three jobs

The tracker asks for `Card`, `Deck` and `LeitnerSystem`. One reasonable split, to
argue about at `/grill-me`:

- `Card`: front, back, box, due date. Knows if it's due.
- `Deck`: a named collection of cards. Add, remove, find due cards.
- `LeitnerSystem`: the rules. Promote, demote, schedule; saving and loading.

Ask yourself for each method: *which class has the data it needs?* That's usually
where it belongs.

## 5. Saving with JSON

`json` can't store a `date` or a `Card` directly. Convert to plain dicts and strings on
the way out, and back again on the way in:

```python
import json
from datetime import date

card = {"front": "hola", "back": "hello", "box": 2, "due": date(2026, 10, 15).isoformat()}
text = json.dumps([card], indent=2)
loaded = json.loads(text)
date.fromisoformat(loaded[0]["due"])     # a date again
```

A common pattern is a `to_dict()` method plus a `from_dict()` *class method*:

```python fragment
class Card:
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        return cls(data["front"], data["back"], box=data["box"],
                   due=date.fromisoformat(data["due"]))
```

A **round-trip test** saves, loads, and checks that nothing changed (W3.3.d). Use
pytest's `tmp_path` fixture, so the test writes to a throwaway folder and not to your real `data.json`.

## 6. How it's checked

- **W3.3.a**: `/grill-me W3.3`.
- **W3.3.b–d**: tutor review of the classes, the injected `today`, and persistence.
- **W3.3.e**: `test_flashcards.py`, written by the tutor from your plan before you code.
  It covers promotion, demotion, due dates, and a save/load round-trip.
- **W3.3.f**: `walkthrough.md`.

A small CLI to review the due cards (with `rich` from Week 2) makes it real, but the
tests are about the classes.

## Pitfalls

- `date.today()` anywhere except the outermost layer.
- A class attribute `cards = []` on `Deck`, shared by every deck (Lesson 3.1, section 4).
- Comparing dates as strings (`"2026-10-9" > "2026-10-10"` is `True`!). Compare `date` objects.
- Opening `data.json` without `with` and `encoding="utf-8"`.
