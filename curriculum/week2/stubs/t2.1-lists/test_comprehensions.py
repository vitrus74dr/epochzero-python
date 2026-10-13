"""W2.1.b: each comprehension gives exactly the same output as its loop."""

import ast
import inspect

import pytest

import comprehensions
import loops

NUMS = [[], [1], [2], [1, 2, 3, 4, 5, 6], [-4, -3, 0, 7, 10], list(range(50))]
WORDS = [([], 3), (["a", "bb", "ccc"], 2), (["Python", "is", "fun"], 3), (["x"], 0), (["same", "size"], 4)]
BOARDS = [([], []), (["Ada"], [95]), (["Ada", "Grace", "Linus"], [95, 88, 72]), (["A", "B"], [1])]


@pytest.mark.parametrize("nums", NUMS)
def test_squares_of_evens(nums):
    assert comprehensions.squares_of_evens(nums) == loops.squares_of_evens(nums)


@pytest.mark.parametrize("words,n", WORDS)
def test_long_words_upper(words, n):
    assert comprehensions.long_words_upper(words, n) == loops.long_words_upper(words, n)


@pytest.mark.parametrize("names,scores", BOARDS)
def test_scoreboard(names, scores):
    assert comprehensions.scoreboard(names, scores) == loops.scoreboard(names, scores)


@pytest.mark.parametrize("name", ["squares_of_evens", "long_words_upper", "scoreboard"])
def test_written_as_a_comprehension(name):
    """No for-loop statements: the work happens inside a list comprehension."""
    tree = ast.parse(inspect.getsource(getattr(comprehensions, name)))
    assert not any(isinstance(n, ast.For) for n in ast.walk(tree)), "use a comprehension, not a for loop"
    assert any(isinstance(n, ast.ListComp) for n in ast.walk(tree)), "no list comprehension found"
