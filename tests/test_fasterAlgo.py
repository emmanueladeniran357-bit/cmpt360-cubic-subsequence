"""Validate the DP helper, full algorithm, and command-line interface."""

from itertools import combinations, product
from pathlib import Path
import random
import subprocess
import sys
import unittest

from baseline import longest_cubic_subsequence as baseline
from fasterAlgo import (
    longest_common_subsequence_three,
    longest_cubic_subsequence,
)


def is_subsequence(candidate, sequence):
    next_index = 0
    for symbol in sequence:
        if next_index < len(candidate) and symbol == candidate[next_index]:
            next_index += 1
    return next_index == len(candidate)


def brute_lcs_length(first, second, third):
    """Independent oracle: enumerate subsequences of the shortest input."""
    shortest = min((first, second, third), key=len)
    for length in range(len(shortest), -1, -1):
        for positions in combinations(range(len(shortest)), length):
            candidate = "".join(shortest[i] for i in positions)
            if all(is_subsequence(candidate, s) for s in (first, second, third)):
                return length
    return 0


class FasterAlgorithmTests(unittest.TestCase):
    def check_cube(self, sequence, expected_length):
        answer = longest_cubic_subsequence(sequence)
        self.assertEqual(len(answer), expected_length)
        self.assertEqual(len(answer) % 3, 0)
        self.assertEqual(answer, answer[:len(answer) // 3] * 3)
        self.assertTrue(is_subsequence(answer, sequence))

    def test_lcs_helper_against_exhaustive_oracle(self):
        # 15 binary strings of lengths 0..3, hence 15**3 = 3375 triples.
        strings = [
            "".join(symbols)
            for length in range(4)
            for symbols in product("ab", repeat=length)
        ]
        for first, second, third in product(strings, repeat=3):
            with self.subTest(first=first, second=second, third=third):
                answer = longest_common_subsequence_three(first, second, third)
                self.assertEqual(len(answer), brute_lcs_length(first, second, third))
                for sequence in (first, second, third):
                    self.assertTrue(is_subsequence(answer, sequence))

    def test_known_cases(self):
        cases = [
            ("", 0), ("a", 0), ("aa", 0), ("abcdef", 0), ("aabbcc", 0),
            ("aaa", 3), ("aaaaa", 3), ("aaaaaa", 6), ("abcabcabc", 9),
            ("abxabyab", 6), ("aaabbb", 3), ("atcgtatgcatgca", 9),
            ("AaAaAa", 6), ("ééé", 3), ("a a a ", 6),
        ]
        for sequence, expected in cases:
            with self.subTest(sequence=sequence):
                self.check_cube(sequence, expected)

    def test_every_binary_input_up_to_length_eight_matches_baseline(self):
        for length in range(9):
            for symbols in product("ab", repeat=length):
                sequence = "".join(symbols)
                with self.subTest(sequence=sequence):
                    self.check_cube(sequence, len(baseline(sequence)))

    def test_seeded_random_inputs_match_baseline(self):
        rng = random.Random(360)
        for case in range(120):
            length = rng.randrange(15)
            sequence = "".join(rng.choice("abcd") for _ in range(length))
            with self.subTest(case=case, sequence=sequence):
                self.check_cube(sequence, len(baseline(sequence)))

    def test_larger_inputs_with_known_optima(self):
        # Full-length cubes meet the upper bound of n, without a slow oracle.
        for sequence in ("a" * 36, "abcd" * 9):
            with self.subTest(sequence=sequence):
                self.check_cube(sequence, len(sequence))

    def test_cli_example_empty_and_spaced_input(self):
        script = Path(__file__).resolve().parents[1] / "fasterAlgo.py"
        for sequence in ("atcgtatgcatgca", "", "a a a "):
            with self.subTest(sequence=sequence):
                result = subprocess.run(
                    [sys.executable, str(script), sequence],
                    capture_output=True, text=True, check=True,
                )
                self.assertIn(f"Length: {len(baseline(sequence))}\n", result.stdout)
                self.assertIn("Cubic subsequence C:", result.stdout)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
