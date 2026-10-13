"""Three working functions written with plain for loops. Don't edit this file:
test_comprehensions.py uses it as the reference answer."""


def squares_of_evens(nums: list[int]) -> list[int]:
    result = []
    for n in nums:
        if n % 2 == 0:
            result.append(n * n)
    return result


def long_words_upper(words: list[str], min_length: int) -> list[str]:
    result = []
    for word in words:
        if len(word) >= min_length:
            result.append(word.upper())
    return result


def scoreboard(names: list[str], scores: list[int]) -> list[str]:
    result = []
    for rank, (name, score) in enumerate(zip(names, scores), start=1):
        result.append(f"{rank}. {name}: {score}")
    return result
