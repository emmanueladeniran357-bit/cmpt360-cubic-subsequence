"""Reproducible pilot timing experiment for cubic subsequence algorithms."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
from statistics import median
import sys
from time import perf_counter


# Allow this script to import the algorithms from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from baseline import longest_cubic_subsequence as baseline
from fasterAlgo import longest_cubic_subsequence as split_dp


SEED = 360
LENGTHS = (6, 9, 12, 15, 18)
RANDOM_SAMPLES = 3
REPETITIONS = 3

ALGORITHMS = (
    ("baseline", baseline),
    ("split_dp", split_dp),
)


def generate_cases():
    """Generate identical input cases whenever the seed is unchanged."""
    rng = random.Random(SEED)
    cases = []

    for length in LENGTHS:
        for family, alphabet in (
            ("random_binary", "ab"),
            ("random_eight_symbols", "abcdefgh"),
        ):
            for sample in range(1, RANDOM_SAMPLES + 1):
                sequence = "".join(
                    rng.choice(alphabet) for _ in range(length)
                )
                cases.append((family, sample, sequence))

        cases.append(("single_symbol", 1, "a" * length))

        block = "".join(
            rng.choice("abcdefgh") for _ in range(length // 3)
        )
        cases.append(("three_copies", 1, block * 3))

    return cases


def validate_answer(sequence, answer):
    """Check that the answer is cubic and preserves input order."""
    if not isinstance(answer, str):
        raise ValueError("An algorithm returned a non-string answer.")

    block_length = len(answer) // 3
    if len(answer) % 3 != 0 or answer != answer[:block_length] * 3:
        raise ValueError(f"Answer is not cubic: {answer!r}")

    next_index = 0
    for symbol in sequence:
        if next_index < len(answer) and symbol == answer[next_index]:
            next_index += 1

    if next_index != len(answer):
        raise ValueError(f"Answer is not a subsequence: {answer!r}")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def file_hash(filename):
    contents = (PROJECT_ROOT / filename).read_bytes()
    return hashlib.sha256(contents).hexdigest()


def run_experiment(output_dir):
    # Require a fresh directory so previous results are preserved.
    if output_dir.exists():
        raise FileExistsError(
            f"{output_dir} already exists. Choose a new output directory."
        )

    cases = generate_cases()
    timings = []
    summaries = []

    metadata = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "operating_system": platform.system(),
        "operating_system_release": platform.release(),
        "machine_architecture": platform.machine(),
        "seed": SEED,
        "lengths": list(LENGTHS),
        "random_samples_per_family_per_length": RANDOM_SAMPLES,
        "warmup_runs_per_algorithm_per_case": 1,
        "timed_runs_per_algorithm_per_case": REPETITIONS,
        "case_count": len(cases),
        "timer": "time.perf_counter",
        "measurement": "algorithm call only",
        "source_sha256": {
            filename: file_hash(filename)
            for filename in (
                "baseline.py",
                "fasterAlgo.py",
                "experiments/benchmark.py",
            )
        },
    }

    for case_index, (family, sample, sequence) in enumerate(cases):
        print(
            f"[{case_index + 1}/{len(cases)}] "
            f"{family}, n={len(sequence)}, sample={sample}",
            flush=True,
        )

        # One untimed warm-up per algorithm, also checked for correctness.
        warmup_lengths = []
        warmup_order = (
            ALGORITHMS if case_index % 2 == 0 else ALGORITHMS[::-1]
        )

        for name, algorithm in warmup_order:
            answer = algorithm(sequence)
            validate_answer(sequence, answer)
            warmup_lengths.append(len(answer))

        if warmup_lengths[0] != warmup_lengths[1]:
            raise ValueError(
                f"Algorithms disagree on optimal length for {sequence!r}"
            )

        expected_length = warmup_lengths[0]

        # These two families have a known full-length optimal answer.
        if family in ("single_symbol", "three_copies"):
            if expected_length != len(sequence):
                raise ValueError("Failed a known full-length optimum.")

        samples = {name: [] for name, _ in ALGORITHMS}

        for repetition in range(1, REPETITIONS + 1):
            # Alternate the first algorithm across runs and input cases.
            if (case_index + repetition - 1) % 2 == 0:
                order = ALGORITHMS
            else:
                order = ALGORITHMS[::-1]

            for position, (name, algorithm) in enumerate(order, start=1):
                start = perf_counter()
                answer = algorithm(sequence)
                elapsed = perf_counter() - start

                # Validation happens after timing has stopped.
                validate_answer(sequence, answer)
                if len(answer) != expected_length:
                    raise ValueError(
                        f"{name} returned an unexpected answer length."
                    )

                samples[name].append(elapsed)
                timings.append({
                    "case_id": case_index + 1,
                    "family": family,
                    "length": len(sequence),
                    "sample": sample,
                    "input": sequence,
                    "algorithm": name,
                    "repetition": repetition,
                    "order_in_pair": position,
                    "seconds": elapsed,
                    "answer_length": len(answer),
                })

        for name, _ in ALGORITHMS:
            values = samples[name]
            summaries.append({
                "case_id": case_index + 1,
                "family": family,
                "length": len(sequence),
                "sample": sample,
                "input": sequence,
                "algorithm": name,
                "runs": len(values),
                "minimum_seconds": min(values),
                "median_seconds": median(values),
                "maximum_seconds": max(values),
                "answer_length": expected_length,
            })

    metadata["finished_utc"] = datetime.now(timezone.utc).isoformat()

    output_dir.mkdir(parents=True, exist_ok=False)
    write_csv(output_dir / "timings.csv", timings)
    write_csv(output_dir / "summary.csv", summaries)

    with (output_dir / "metadata.json").open(
        "w", encoding="utf-8"
    ) as output:
        json.dump(metadata, output, indent=2)
        output.write("\n")

    print(f"\nCompleted {len(cases)} input cases.")
    print(f"Saved {len(timings)} timing rows.")
    print(f"Saved {len(summaries)} summary rows.")
    print(f"Results directory: {output_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare the baseline and split-DP algorithms."
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="New directory in which to save experiment results.",
    )
    args = parser.parse_args()

    try:
        run_experiment(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Experiment failed: {error}\n")


if __name__ == "__main__":
    main()
