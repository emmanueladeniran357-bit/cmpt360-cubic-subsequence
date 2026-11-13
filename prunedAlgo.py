"""Exact split-and-DP search with region-length pruning.

Run: python3 prunedAlgo.py "atcgtatgcatgca"
"""

import argparse
from time import perf_counter

from fasterAlgo import longest_common_subsequence_three


def longest_cubic_subsequence(sequence: str) -> str:
    """Return a longest cubic subsequence using safe split pruning.

    A common subsequence cannot exceed the shortest region.
    Skip a split if that bound cannot improve the best block.

    Worst-case upper bounds: O(n**5) time and O(n**3) space.
    """
    n = len(sequence)
    best_block = ""

    for i in range(1, n - 1):
        for j in range(i + 1, n):
            upper_bound = min(i, j - i, n - j)
            if upper_bound <= len(best_block):
                continue

            block = longest_common_subsequence_three(
                sequence[:i], sequence[i:j], sequence[j:]
            )
            if len(block) > len(best_block):
                best_block = block

    return best_block * 3


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find a longest cubic subsequence with pruned DP search.",
        epilog="O(n^5) time and O(n^3) space: begin with modest input sizes.",
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
