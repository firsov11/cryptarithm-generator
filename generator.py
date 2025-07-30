import itertools
import random
import time

def solve_cryptarithm(words, result, require_unique=True, max_solutions=2):
    letters = set("".join(words + [result]))
    if len(letters) > 10:
        return None

    letters = list(letters)
    first_letters = {w[0] for w in words + [result]}
    expr_template = " + ".join(words) + " == " + result
    solutions = []

    for perm in itertools.permutations(range(10), len(letters)):
        letter_digit = dict(zip(letters, perm))
        if any(letter_digit[l] == 0 for l in first_letters):
            continue

        def word_value(word):
            return sum(letter_digit[ch] * (10 ** i) for i, ch in enumerate(reversed(word)))

        try:
            if sum(word_value(w) for w in words) == word_value(result):
                solutions.append(letter_digit)
                if not require_unique:
                    return letter_digit
                if len(solutions) >= max_solutions:
                    return None  # Не уникальное решение
        except:
            continue

    return solutions[0] if solutions else None


def generate_cryptarithm(wordlist, mode="first", max_tries=1000, progress_callback=None):
    for i in range(1, max_tries + 1):
        if progress_callback and i % 100 == 0:
            progress_callback(i)

        w1 = random.choice(wordlist)
        w2 = random.choice(wordlist)
        result = random.choice(wordlist)

        if len(result) < max(len(w1), len(w2)):
            continue

        all_letters = set(w1 + w2 + result)
        if len(all_letters) > 10:
            continue

        words = [w1, w2]
        solution = solve_cryptarithm(
            words,
            result,
            require_unique=(mode == "all"),
            max_solutions=2
        )

        if solution:
            expr = f"{w1} + {w2} = {result}"
            return [(expr, solution)] if mode == "first" else [(expr, solution)]

    return None


def generate_cryptarithm_with_progress(wordlist, mode="first", max_tries=1000, progress_callback=None):
    results = []
    start_time = time.time()

    for i in range(1, max_tries + 1):
        if progress_callback and i % 100 == 0:
            elapsed = time.time() - start_time
            progress_callback(i)

        w1 = random.choice(wordlist)
        w2 = random.choice(wordlist)
        result = random.choice(wordlist)

        if len(result) < max(len(w1), len(w2)):
            continue

        all_letters = set(w1 + w2 + result)
        if len(all_letters) > 10:
            continue

        words = [w1, w2]

        if mode == "first":
            solution = solve_cryptarithm(words, result, require_unique=False)
            if solution:
                expr = f"{w1} + {w2} = {result}"
                return [(expr, solution)]

        elif mode == "all":
            solution = solve_cryptarithm(words, result, require_unique=True, max_solutions=2)
            if solution:
                expr = f"{w1} + {w2} = {result}"
                results.append((expr, solution))

    return results if results else None
