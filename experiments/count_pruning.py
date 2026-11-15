"""Count split evaluations and DP updates on saved experiment inputs."""

import argparse
import csv
import hashlib
from pathlib import Path
import sys
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import prunedAlgo


def measure_work(sequence):
    """Return the answer and deterministic work counts, without timing."""
    n = len(sequence)
    total_splits = 0
    original_updates = 0

    for i in range(1, n - 1):
        for j in range(i + 1, n):
            total_splits += 1
            original_updates += i * (j - i) * (n - j)

    evaluated_splits = 0
    evaluated_updates = 0
    original_lcs = prunedAlgo.longest_common_subsequence_three

    def counted_lcs(first, second, third):
        nonlocal evaluated_splits, evaluated_updates
        evaluated_splits += 1
        evaluated_updates += len(first) * len(second) * len(third)
        return original_lcs(first, second, third)

    with patch.object(
        prunedAlgo,
        "longest_common_subsequence_three",
        new=counted_lcs,
    ):
        answer = prunedAlgo.longest_cubic_subsequence(sequence)

    counts = {
        "total_splits": total_splits,
        "evaluated_splits": evaluated_splits,
        "skipped_splits": total_splits - evaluated_splits,
        "original_dp_updates": original_updates,
        "evaluated_dp_updates": evaluated_updates,
        "avoided_dp_updates": original_updates - evaluated_updates,
    }
    return answer, counts


def analyze(summary_path, output_path):
    if output_path.exists():
        raise FileExistsError(
            f"{output_path} already exists. Choose a new output file."
        )

    with summary_path.open(newline="", encoding="utf-8") as source:
        cases = [
            row for row in csv.DictReader(source)
            if row["algorithm"] == "pruned_dp"
        ]

    if not cases:
        raise ValueError("No pruned_dp rows found in the summary.")

    source_hashes = {
        "summary_sha256": hashlib.sha256(
            summary_path.read_bytes()
        ).hexdigest(),
        "pruned_source_sha256": hashlib.sha256(
            (PROJECT_ROOT / "prunedAlgo.py").read_bytes()
        ).hexdigest(),
        "lcs_source_sha256": hashlib.sha256(
            (PROJECT_ROOT / "fasterAlgo.py").read_bytes()
        ).hexdigest(),
        "analysis_source_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
    }

    rows = []
    seen = set()

    for case in cases:
        case_id = case["case_id"]
        if case_id in seen:
            raise ValueError(f"Duplicate pruned case ID: {case_id}")
        seen.add(case_id)

        sequence = case["input"]
        if len(sequence) != int(case["length"]):
            raise ValueError(f"Input length mismatch for case {case_id}.")

        answer, counts = measure_work(sequence)
        if len(answer) != int(case["answer_length"]):
            raise ValueError(f"Answer length mismatch for case {case_id}.")

        block_length = len(answer) // 3
        if len(answer) % 3 or answer != answer[:block_length] * 3:
            raise ValueError(f"Invalid cubic answer for case {case_id}.")

        remaining = iter(sequence)
        if not all(symbol in remaining for symbol in answer):
            raise ValueError(f"Invalid subsequence for case {case_id}.")

        rows.append({
            "case_id": case_id,
            "family": case["family"],
            "length": len(sequence),
            "sample": case["sample"],
            "input": sequence,
            "answer_length": len(answer),
            **counts,
            **source_hashes,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Analyzed {len(rows)} input cases.")
    print(f"Saved work counts: {output_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Count pruning work on saved experiment inputs."
    )
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        analyze(args.summary, args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Analysis failed: {error}\n")


if __name__ == "__main__":
    main()
