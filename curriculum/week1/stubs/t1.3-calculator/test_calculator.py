"""W1.3.c: the calculator never crashes, whatever the user types.

Each test drives main() with a fake input() that returns the given lines and
then "exit". If main() raises anything, or asks for input after "exit", the
test fails. Results may print as 5 or 5.0; how errors are worded is up to you.

After /grill-me, add your own tests for the functions in your plan.
"""

import re

import pytest

import calculator


def run(monkeypatch, capsys, *lines):
    replies = iter([*lines, "exit"])
    asked = 0

    def _input(prompt=""):
        nonlocal asked
        asked += 1
        try:
            return next(replies)
        except StopIteration:
            raise AssertionError("main() kept asking for input after 'exit'") from None

    monkeypatch.setattr("builtins.input", _input)
    calculator.main()
    assert asked == len(lines) + 1, "main() should read every line, up to and including 'exit'"
    return capsys.readouterr().out


def shows(out, number):
    """True if `number` appears as a whole number in the output (5 or 5.0)."""
    return re.search(rf"(?<![\d.]){re.escape(number)}(\.0+)?(?![\d.])", out) is not None


def test_exit_ends_the_loop(monkeypatch, capsys):
    run(monkeypatch, capsys)


@pytest.mark.parametrize("line,result", [
    ("2 + 3", "5"),
    ("7 - 10", "-3"),
    ("4 * 2.5", "10"),
    ("9 / 2", "4.5"),
])
def test_arithmetic(monkeypatch, capsys, line, result):
    assert shows(run(monkeypatch, capsys, line), result)


def test_extra_spaces(monkeypatch, capsys):
    assert shows(run(monkeypatch, capsys, "   2    +   3  "), "5")


@pytest.mark.parametrize("line", [
    "abc",          # letters
    "two + 3",      # a word for a number
    "",             # empty input
    "    ",         # only spaces
    "5 / 0",        # division by zero
    "2 ^ 3",        # unknown operator
    "2 +",          # missing operand
    "1 + 2 + 3",    # more than `a op b` (support it or reject it, but don't crash)
])
def test_bad_input_never_crashes(monkeypatch, capsys, line):
    out = run(monkeypatch, capsys, line, "20 + 22")
    assert shows(out, "42"), "after bad input the loop should carry on to the next line"


def test_division_by_zero_says_something(monkeypatch, capsys):
    assert run(monkeypatch, capsys, "5 / 0").strip(), "tell the user what went wrong"
