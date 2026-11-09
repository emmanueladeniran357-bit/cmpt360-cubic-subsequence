"""Exact exhaustive-search baseline for the Longest Cubic Subsequence problem.

Run: python3 baseline.py "atcgtatgcatgca"
Each character is one symbol; comparisons are case-sensitive.
"""

import argparse
from itertools import combinations
from time import perf_counter


def longest_cubic_subsequence(sequence: str) -> str:
    """Return a longest subsequence of the form X + X + X.

    Enumerate increasing position tuples of every positive length divisible
    by three. Keep a longest candidate whose three blocks are equal.
    The empty string is the answer when no nonempty cube exists.

    Worst-case upper bounds: O(n * 2**n) time and O(n) auxiliary space.
    Candidates are generated one at a time, not stored together.
    """
    n = len(sequence)
    best = ""

    for length in range(3, n + 1, 3):
        block_length = length // 3
        for positions in combinations(range(n), length):
            candidate = "".join(sequence[i] for i in positions)
            first = candidate[:block_length]
            second = candidate[block_length:2 * block_length]
            third = candidate[2 * block_length:]

            if first == second == third and length > len(best):
                best = candidate

    return best


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find a longest cubic subsequence by exhaustive search.",
        epilog="Exponential running time: start with short inputs.",
    )
    parser.add_argument(
        "sequence",
        help='Input sequence; quote it, and use "" for the empty sequence.',
    )
    args = parser.parse_args()

    start = perf_counter()
    cubic = longest_cubic_subsequence(args.sequence)
    elapsed = perf_counter() - start
    block = cubic[:len(cubic) // 3]

    print(f"Input: {args.sequence!r}")
    print(f"Repeated block X: {block!r}")
    print(f"Cubic subsequence C: {cubic!r}")
    print(f"Length: {len(cubic)}")
    print(f"Elapsed seconds: {elapsed:.6f}")


if __name__ == "__main__":
    main()
