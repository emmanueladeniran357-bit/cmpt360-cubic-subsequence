"""Correctness and CLI checks using only the Python standard library."""

from itertools import product
from pathlib import Path
import subprocess
import sys
import unittest

from baseline import longest_cubic_subsequence


def is_subsequence(candidate, sequence):
    """Check order and distinct positions with a left-to-right scan."""
    index = 0
    for symbol in sequence:
        if index < len(candidate) and candidate[index] == symbol:
            index += 1
    return index == len(candidate)


def oracle_length(sequence):
    """Independent small-input oracle: enumerate blocks, not position subsets."""
    alphabet = sorted(set(sequence))
    best = 0
    for block_length in range(1, len(sequence) // 3 + 1):
        for symbols in product(alphabet, repeat=block_length):
            cube = "".join(symbols) * 3
            if is_subsequence(cube, sequence):
                best = max(best, len(cube))
    return best


class BaselineTests(unittest.TestCase):
    def check_answer(self, sequence, expected_length):
        answer = longest_cubic_subsequence(sequence)
        self.assertEqual(len(answer), expected_length)
        self.assertEqual(len(answer) % 3, 0)
        block_length = len(answer) // 3
        self.assertEqual(answer, answer[:block_length] * 3)
        self.assertTrue(is_subsequence(answer, sequence))
        return answer

    def test_known_cases(self):
        cases = [
            ("", 0),
            ("a", 0),
            ("aa", 0),
            ("abcdef", 0),
            ("aabbcc", 0),
            ("aaa", 3),
            ("aaaaa", 3),
            ("aaaaaa", 6),
            ("abcabcabc", 9),
            ("abxabyab", 6),
            ("aaabbb", 3),
            ("atcgtatgcatgca", 9),
            ("AaAaAa", 6),
            ("ééé", 3),
            ("a a a ", 6),
        ]
        for sequence, expected in cases:
            with self.subTest(sequence=sequence):
                self.check_answer(sequence, expected)

    def test_every_binary_input_up_to_length_eight(self):
        # 1 + 2 + ... + 2**8 = 511 distinct inputs.
        for length in range(9):
            for symbols in product("ab", repeat=length):
                sequence = "".join(symbols)
                with self.subTest(sequence=sequence):
                    self.check_answer(sequence, oracle_length(sequence))

    def test_cli_example_and_empty_input(self):
        script = Path(__file__).resolve().parents[1] / "baseline.py"
        for sequence, expected_length in [("atcgtatgcatgca", 9), ("", 0)]:
            with self.subTest(sequence=sequence):
                result = subprocess.run(
                    [sys.executable, str(script), sequence],
                    capture_output=True, text=True, check=True,
                )
                self.assertIn(f"Length: {expected_length}\n", result.stdout)
                self.assertIn("Cubic subsequence C:", result.stdout)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
