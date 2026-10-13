# CLI Trivia Game

A trivia quiz in the terminal, with fresh questions from the internet every game. It
brings together everything since Week 1: loops, dicts, functions, `rich` output, and
network error handling. It adds one new skill that professionals use daily: **testing
code that talks to the network, without the network**.

## 1. The API

```text
https://opentdb.com/api.php?amount=5&type=multiple
```

```json
{
  "response_code": 0,
  "results": [
    {
      "type": "multiple",
      "difficulty": "medium",
      "category": "Science &amp; Nature",
      "question": "What are the smallest blood vessels in the human body?",
      "correct_answer": "Capillaries",
      "incorrect_answers": ["Arterioles", "Veinules", "Lymphatics"]
    }
  ]
}
```

Things the API does that your code must handle:

- **`response_code`** (Lesson 4.2): check it first. 1 means not enough questions,
  2 a bad parameter, 5 rate limited.
- **HTML entities**: text arrives as `Science &amp; Nature` and `Luigi&#039;s Mansion`.
  `html.unescape` turns those back into `&` and `'`.
- **`amount` is capped at 50**; ask for more and you silently get 50.
- Without `type=multiple`, some questions are true/false (`"type": "boolean"`) with a
  single incorrect answer.

```python
>>> import html
>>> html.unescape("Luigi&#039;s Mansion &amp; &quot;Pok&eacute;mon&quot;")
'Luigi\'s Mansion & "Pokémon"'
```

## 2. Shuffling the answers

The correct answer arrives separately. Combine it with the wrong ones and shuffle:

```python
import random

choices = ["Arterioles", "Veinules", "Lymphatics"] + ["Capillaries"]
random.shuffle(choices)          # shuffles in place, returns None
```

For tests you'll want the shuffle to be predictable. Accept a `random.Random`
instance as a parameter: `rng.shuffle(choices)`, with `random.Random(42)` in tests.
It's the same idea as injecting `today` in Lesson 3.3.

## 3. Structure: three layers

```text
week4/t4.3-trivia/
    api.py        fetch_questions(amount, session=requests) -> list[Question]
                  checks response_code, unescapes, raises TriviaError
    game.py       pure: shuffle choices, check an answer, keep score
    cli.py        rich + input: the only file that prints
    test_api.py   network mocked
    test_game.py
```

`/grill-me` will press you on this. In particular: what should `fetch_questions` do
when `response_code` isn't 0, return an empty list or raise? One clean answer is a
custom exception:

```python
class TriviaError(Exception):
    """The trivia API couldn't give us questions."""
```

`cli.py` catches `TriviaError`, `requests.Timeout` and `requests.ConnectionError`, and
offers to retry or quit (W4.3.d).

## 4. Testing without the network

Tests that hit the real API are slow, they fail when you're offline, and they can't
produce a timeout on demand. So the tests **replace** the network call. The trick is to
make it replaceable: `fetch_questions` takes the HTTP client as a parameter, which
defaults to the real `requests`:

```python fragment
def fetch_questions(amount: int, session=requests) -> list[dict]:
    response = session.get(URL, params={"amount": amount, "type": "multiple"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    ...
```

In a test, pass a fake that behaves like `requests` but returns whatever the test needs:

```python
import pytest
import requests


class FakeResponse:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response, self.error = response, error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response
```

```python fragment
def test_timeout_is_passed_on():
    session = FakeSession(error=requests.Timeout())
    with pytest.raises(requests.Timeout):
        fetch_questions(5, session=session)

def test_every_request_has_a_timeout():
    session = FakeSession(FakeResponse({"response_code": 0, "results": []}))
    fetch_questions(5, session=session)
    assert session.calls[0]["timeout"]
```

The tests W4.3.e needs: success (unescaped text), each bad `response_code`, a
connection error, and a timeout. pytest's `monkeypatch.setattr(requests, "get", fake)`
is another way to do this, but passing the session in keeps the dependency visible.

## 5. How it's checked

- **W4.3.a**: `/grill-me W4.3`.
- **W4.3.b–d**: tutor review and a demo: real questions, `rich` feedback and a running
  score, then unplug the network and show the friendly retry.
- **W4.3.e**: `/verify W4.3` on the mocked tests.
- **W4.3.f**: `walkthrough.md`.

## Pitfalls

- Reading `data["results"]` before checking `response_code`.
- Forgetting `html.unescape`. You'll show players `&quot;` before you notice.
- `random.shuffle` returns `None`: `choices = random.shuffle(choices)` loses your list.
- Tests that call the real API.
