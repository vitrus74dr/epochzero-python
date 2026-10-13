"""W1.1.c: numeric input is converted before arithmetic.

These tests fake the keyboard. `monkeypatch` swaps the built-in input() for a
function that hands back the answers in the list, one per call, and `capsys`
captures what main() prints.
"""

import pytest

import hello


def fake_input(monkeypatch, answers):
    replies = iter(answers)
    prompts = []

    def _input(prompt=""):
        prompts.append(prompt)
        try:
            return next(replies)
        except StopIteration:
            raise AssertionError(f"input() was called more often than expected: {prompt!r}") from None

    monkeypatch.setattr("builtins.input", _input)
    return prompts


def test_asks_twice_and_greets_by_name(monkeypatch, capsys):
    prompts = fake_input(monkeypatch, ["Ada", "36"])
    hello.main()
    assert len(prompts) == 2, "ask for the name, then the age"
    assert "Ada" in capsys.readouterr().out


def test_age_is_converted_before_adding(monkeypatch, capsys):
    fake_input(monkeypatch, ["Ada", "36"])
    hello.main()  # a TypeError here means the age is still a str
    out = capsys.readouterr().out
    assert "361" not in out, "that's string concatenation: '36' + '1'"
    assert "37" in out


@pytest.mark.parametrize("age,next_year", [("0", "1"), ("99", "100"), (" 7 ", "8")])
def test_other_ages(monkeypatch, capsys, age, next_year):
    fake_input(monkeypatch, ["Grace", age])
    hello.main()
    assert next_year in capsys.readouterr().out
