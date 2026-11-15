"""Check work counts against small examples with known totals."""

import unittest

from experiments.count_pruning import measure_work


class PruningWorkTests(unittest.TestCase):
    def test_inputs_without_splits(self):
        for sequence in ("", "a", "aa"):
            with self.subTest(sequence=sequence):
                answer, counts = measure_work(sequence)
                self.assertEqual(answer, "")
                self.assertTrue(all(value == 0 for value in counts.values()))

    def test_distinct_symbols_skip_nothing(self):
        answer, counts = measure_work("abcdef")
        self.assertEqual(answer, "")
        self.assertEqual(counts, {
            "total_splits": 10,
            "evaluated_splits": 10,
            "skipped_splits": 0,
            "original_dp_updates": 56,
            "evaluated_dp_updates": 56,
            "avoided_dp_updates": 0,
        })

    def test_repeated_symbol_counts(self):
        answer, counts = measure_work("aaaaaa")
        self.assertEqual(answer, "aaaaaa")
        self.assertEqual(counts, {
            "total_splits": 10,
            "evaluated_splits": 2,
            "skipped_splits": 8,
            "original_dp_updates": 56,
            "evaluated_dp_updates": 12,
            "avoided_dp_updates": 44,
        })


if __name__ == "__main__":
    unittest.main()
