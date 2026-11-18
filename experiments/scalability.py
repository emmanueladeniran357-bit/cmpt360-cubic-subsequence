"""Measure the largest tested input within fixed budgets on macOS or Linux."""

import argparse
import csv
import json
import platform
import random
import resource
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from benchmark import file_hash, validate_answer
from baseline import longest_cubic_subsequence as baseline
from fasterAlgo import longest_cubic_subsequence as split_dp
from prunedAlgo import longest_cubic_subsequence as pruned_dp


SOLVERS = {"baseline": baseline, "split_dp": split_dp, "pruned_dp": pruned_dp}
LENGTHS = (12, 18, 21, 24, 27, 30, 36, 48, 60, 72, 96, 120, 144, 192, 240)
FAMILIES = ("random_binary", "single_symbol", "all_distinct")
SECONDS = 5
MEMORY_MIB = 256
POLL_SECONDS = 0.05
SEED = 360


def make_input(family, n):
    if family == "single_symbol":
        return "a" * n
    if family == "all_distinct":
        return "".join(chr(0x100 + i) for i in range(n))
    rng = random.Random(SEED + n)
    return "".join(rng.choice("ab") for _ in range(n))


def worker(name, family, n):
    sequence = make_input(family, n)
    start = perf_counter()
    answer = SOLVERS[name](sequence)
    seconds = perf_counter() - start
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mib = peak / (1024 ** 2 if sys.platform == "darwin" else 1024)
    print(json.dumps([answer, seconds, peak_mib]))


def trial(name, family, n):
    command = [sys.executable, __file__, "--worker", name, family, str(n)]
    with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as child:
        # Allow two extra seconds for Python startup and returning the answer.
        deadline = perf_counter() + SECONDS + 2
        status = None
        sampled_peak = 0.0
        while child.poll() is None:
            sample = subprocess.run(
                ["ps", "-o", "rss=", "-p", str(child.pid)],
                capture_output=True, text=True,
            )
            if sample.stdout.strip():
                sampled_peak = max(sampled_peak, int(sample.stdout) / 1024)
            elif child.poll() is None and sample.returncode:
                raise RuntimeError("Could not read child memory: " + sample.stderr)
            if sampled_peak > MEMORY_MIB:
                status = "memory_limit"
            elif perf_counter() >= deadline:
                status = "wall_timeout"
            if status:
                child.kill()
                child.wait()
                return status, None, sampled_peak, None
            try:
                child.wait(timeout=POLL_SECONDS)
            except subprocess.TimeoutExpired:
                pass

        output, _ = child.communicate()
        if child.returncode:
            raise RuntimeError(f"{name} failed on {family}, n={n}")
        answer, seconds, peak = json.loads(output)
        peak = max(peak, sampled_peak)
        sequence = make_input(family, n)
        validate_answer(sequence, answer)
        if family == "all_distinct" and answer:
            raise ValueError("Expected an empty answer for distinct symbols.")
        if family == "single_symbol" and len(answer) != 3 * (n // 3):
            raise ValueError("Incorrect answer length for a single symbol.")
        if peak > MEMORY_MIB:
            status = "memory_limit"
        elif seconds > SECONDS:
            status = "time_limit"
        else:
            status = "ok"
        return status, seconds, peak, len(answer)


def run(output):
    if sys.platform != "darwin" and not sys.platform.startswith("linux"):
        raise ValueError("This experiment supports macOS and Linux.")
    output.mkdir(parents=True, exist_ok=False)
    files = ("baseline.py", "fasterAlgo.py", "prunedAlgo.py",
             "experiments/benchmark.py", "experiments/scalability.py")
    metadata = {
        "platform": platform.platform(), "machine": platform.machine(),
        "python": sys.version, "lengths": LENGTHS, "families": FAMILIES,
        "algorithms": list(SOLVERS), "binary_seed": "360 + input length",
        "trials_per_case": 1, "algorithm_seconds_limit": SECONDS,
        "worker_wall_seconds_limit": SECONDS + 2, "rss_limit_mib": MEMORY_MIB,
        "poll_interval_seconds": POLL_SECONDS,
        "source_sha256": {name: file_hash(name) for name in files},
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    fields = ("family", "length", "algorithm", "status", "algorithm_seconds",
              "worker_rss_mib", "answer_length")
    with (output / "trials.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        for family in FAMILIES:
            active = list(SOLVERS)
            for n in LENGTHS:
                expected = None
                for name in active.copy():
                    status, seconds, rss, answer_len = trial(name, family, n)
                    if answer_len is not None:
                        if expected is not None and answer_len != expected:
                            raise ValueError(f"Answer lengths disagree: {family}, n={n}")
                        expected = answer_len
                    writer.writerow((family, n, name, status, seconds, rss, answer_len))
                    stream.flush()
                    print(f"{family}, n={n}, {name}: {status}", flush=True)
                    if status != "ok":
                        active.remove(name)
                if not active:
                    break


if __name__ == "__main__":
    if sys.argv[1:2] == ["--worker"]:
        worker(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--output", type=Path, required=True)
        args = parser.parse_args()
        try:
            run(args.output)
        except (OSError, ValueError, RuntimeError) as error:
            parser.exit(1, f"Experiment failed: {error}\n")
