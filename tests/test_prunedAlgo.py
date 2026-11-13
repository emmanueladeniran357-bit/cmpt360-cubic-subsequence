"""Check the pruned algorithm against exhaustive search and known optima."""

from itertools import product
from pathlib import Path
import random
import subprocess
import sys
import unittest

from baseline import longest_cubic_subsequence as baseline
from prunedAlgo import longest_cubic_subsequence


def is_subsequence(candidate, sequence):
    next_index = 0
    for symbol in sequence:
        if next_index < len(candidate) and symbol == candidate[next_index]:
            next_index += 1
    return next_index == len(candidate)


class PrunedAlgorithmTests(unittest.TestCase):
    def check_cube(self, sequence, expected_length):
        answer = longest_cubic_subsequence(sequence)
        self.assertEqual(len(answer), expected_length)
        self.assertEqual(len(answer) % 3, 0)
        self.assertEqual(answer, answer[:len(answer) // 3] * 3)
        self.assertTrue(is_subsequence(answer, sequence))

    def test_every_binary_input_up_to_length_eight(self):
        for length in range(9):
            for symbols in product("ab", repeat=length):
                sequence = "".join(symbols)
                with self.subTest(sequence=sequence):
                    self.check_cube(sequence, len(baseline(sequence)))

    def test_seeded_random_inputs(self):
        rng = random.Random(361)
        for case in range(120):
            length = rng.randrange(15)
            sequence = "".join(rng.choice("abcd") for _ in range(length))
            with self.subTest(case=case, sequence=sequence):
                self.check_cube(sequence, len(baseline(sequence)))

    def test_known_cases(self):
        cases = [
            ("", 0),
            ("a", 0),
            ("aa", 0),
            ("abcdef", 0),
            ("aabbcc", 0),
            ("aaaaa", 3),
            ("aaabbb", 3),
            ("abxabyab", 6),
            ("atcgtatgcatgca", 9),
            ("AaAaAa", 6),
            ("ééé", 3),
            ("a a a ", 6),
            ("a" * 36, 36),
            ("abcd" * 9, 36),
        ]
        for sequence, expected in cases:
            with self.subTest(sequence=sequence):
                self.check_cube(sequence, expected)

    def test_command_line(self):
        script = Path(__file__).resolve().parents[1] / "prunedAlgo.py"
        for sequence in ("atcgtatgcatgca", "", "a a a "):
            with self.subTest(sequence=sequence):
                result = subprocess.run(
                    [sys.executable, str(script), sequence],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertIn(
                    f"Length: {len(baseline(sequence))}\n", result.stdout
                )
                self.assertIn("Cubic subsequence C:", result.stdout)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
