# Pilot experiment results

## Setup

The experiment ran on an ARM64 Mac using CPython 3.9.6.

It compared the exhaustive-search baseline with the initial
split-and-DP algorithm on 40 input cases of lengths 6, 9, 12, 15,
and 18.

The input families were random binary strings, random strings over
eight symbols, single-symbol strings, and three copies of a generated
block. Random generation used seed 360.

Each algorithm received one warm-up run and three measured runs per
input. The experiment produced 240 timing records and 80 summaries.

The source files and experiment settings are identified in
../results/mac_pilot/metadata.json.

## Runtime comparison

The following values are in milliseconds. Each value is the median
of the eight per-input median runtimes at that length.

| Input length | Baseline (ms) | Split-DP (ms) |
|---:|---:|---:|
| 6 | 0.014 | 0.081 |
| 9 | 0.114 | 0.416 |
| 12 | 0.994 | 1.391 |
| 15 | 8.866 | 3.777 |
| 18 | 77.637 | 8.479 |

The baseline was faster on every tested input at lengths 6, 9,
and 12. Split-DP was faster on every tested input at lengths 15
and 18.

Dividing the aggregate baseline median by the aggregate split-DP
median gives speedups of approximately 2.35 at length 15 and
9.16 at length 18.

## Observations

The baseline performs well on very small inputs, where the overhead
of repeatedly building DP tables outweighs the benefit of the
polynomial-time approach.

As input length increases, the baseline runtime rises much more
quickly. These measurements are consistent with the algorithms'
complexity analyses, but experiments alone do not prove asymptotic
bounds.

Input structure also affects practical runtime. At length 18,
split-DP took approximately 6.59 ms on the single-symbol input,
compared with family medians of 8.38 ms for random binary inputs
and 8.56 ms for random eight-symbol inputs.

A possible explanation is that matching characters use the simpler
diagonal update rather than the maximum of three predecessor values.
Further experiments would be needed to isolate this effect.

## Validation and limitations

All summary minimum, median, and maximum values were checked against
the raw timing records. Stored answer lengths agreed between the
algorithms, and the recorded source hashes matched the repository
files at the time of analysis.

This is a preliminary experiment with three measured repetitions
and a small number of inputs per family. It does not identify the
exact crossover length, measure memory consumption, or establish
the largest practical input size.

The next investigation is to skip splits whose shortest region
cannot support a repeated block longer than the best block already
found. The current results provide a reference for evaluating that
change.

## Data files

- ../results/mac_pilot/timings.csv
- ../results/mac_pilot/summary.csv
- ../results/mac_pilot/metadata.json
