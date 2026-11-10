"""Exact split-and-DP algorithm for the Longest Cubic Subsequence problem.

Run: python3 fasterAlgo.py "atcgtatgcatgca"
Uses three-sequence LCS for every pair of cuts.
"""

import argparse
from time import perf_counter


def longest_common_subsequence_three(first: str, second: str, third: str) -> str:
    """Return one longest common subsequence of three strings.

    dp[a][b][c] stores the LCS length of first[:a], second[:b], third[:c].
    Retain the full table to reconstruct an actual subsequence.
    For nonempty inputs of lengths p, q, r: O(p*q*r) time and space.
    """
    p, q, r = len(first), len(second), len(third)
    if not first or not second or not third:
        return ""

    # Separate list objects are needed for every row and layer.
    dp = [
        [[0 for _ in range(r + 1)] for _ in range(q + 1)]
        for _ in range(p + 1)
    ]

    for a in range(1, p + 1):
        for b in range(1, q + 1):
            for c in range(1, r + 1):
                if first[a - 1] == second[b - 1] == third[c - 1]:
                    dp[a][b][c] = dp[a - 1][b - 1][c - 1] + 1
                else:
                    dp[a][b][c] = max(
                        dp[a - 1][b][c],
                        dp[a][b - 1][c],
                        dp[a][b][c - 1],
                    )

    # Walk backwards through optimal states, collecting matched characters.
    a, b, c = p, q, r
    reversed_block = []
    while a > 0 and b > 0 and c > 0:
        if first[a - 1] == second[b - 1] == third[c - 1]:
            reversed_block.append(first[a - 1])
            a -= 1
            b -= 1
            c -= 1
        elif dp[a][b][c] == dp[a - 1][b][c]:
            a -= 1
        elif dp[a][b][c] == dp[a][b - 1][c]:
            b -= 1
        else:
            c -= 1

    return "".join(reversed(reversed_block))


def longest_cubic_subsequence(sequence: str) -> str:
    """Return a longest cubic subsequence using all nonempty three-way splits.

    Worst-case bounds: O(n**5) time and O(n**3) auxiliary space.
    Only one split's DP table exists at a time.
    """
    n = len(sequence)
    best_block = ""

    # A nonempty cube needs three nonempty, consecutive regions.
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            block = longest_common_subsequence_three(
                sequence[:i], sequence[i:j], sequence[j:]
            )
            if len(block) > len(best_block):
                best_block = block

    return best_block * 3


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find a longest cubic subsequence with split-and-DP search.",
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
