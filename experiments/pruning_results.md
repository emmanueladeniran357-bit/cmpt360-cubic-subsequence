# Region-length pruning experiment

## Setup

The experiment compared the original split-and-DP algorithm with
the region-length pruning variant on an ARM64 Mac using CPython 3.9.6.

It used 65 input cases at lengths 12, 18, 24, 30, and 36.
At each length, there were five random binary inputs, five random
eight-symbol inputs, one single-symbol input, one three-copy input,
and one all-distinct input. Random generation used seed 360.

Each algorithm received one warm-up and six measured runs per input.
Execution order was balanced: each algorithm ran first three times.
Only the algorithm call was timed.

## Speedups

For each input, speedup is the original DP median runtime divided
by the pruned DP median runtime. A value above one indicates that
pruning was faster.

For the random families, the table reports the median of the five
per-input speedups. Each structured family has one input per length.

| Length | Random binary | Random eight symbols | Single symbol | Three copies | All distinct |
|---:|---:|---:|---:|---:|---:|
| 12 | 3.28 | 1.20 | 12.70 | 6.04 | 0.987 |
| 18 | 5.72 | 1.48 | 21.26 | 8.12 | 0.995 |
| 24 | 2.88 | 1.34 | 30.55 | 8.88 | 0.995 |
| 30 | 4.43 | 1.34 | 40.00 | 8.37 | 0.999 |
| 36 | 3.77 | 1.42 | 47.31 | 8.82 | 1.000 |

## Observations

The largest measured gains occurred on single-symbol inputs.
At length 36, the original DP median was 153.389 milliseconds,
compared with 3.242 milliseconds for pruned DP.

The three-copy input at length 36 improved from 208.898 milliseconds
to 23.672 milliseconds.

Random binary inputs benefited more than random eight-symbol inputs
at every tested length when comparing family median speedups.
A possible explanation is that longer common subsequences allow
the pruning bound to reject more splits. The timing experiment did
not count rejected splits, so this explanation needs further checking.

Speedup did not increase monotonically with length for the random
families. Different input strings were used at each length, so these
measurements do not isolate input length from input structure.

All-distinct inputs showed almost no difference. Their best block
remains empty, while every nonempty split has a positive region-length
bound. Consequently, the pruning rule skips no DP calculations.

The pruned version had a lower median runtime on 60 of 65 inputs.
The other five were four all-distinct inputs and one length-12
eight-symbol input. That random input was approximately 0.56% slower.

These win counts describe this run. Small differences near a speedup
of one should not be treated as reliable improvements or regressions
without further measurements.

## Validation

All 130 summary rows were checked against their six raw timing records.
The minimum, median, and maximum values matched.

The recorded answer lengths agreed between algorithms for all 65
inputs. Structured inputs matched their known optimal lengths.

Generated inputs matched the recorded seed and experiment settings.
Each algorithm ran first exactly three times per input.
The source hashes matched GitHub commit
672a0e4e18f53aaf71916796fd98920a6bd6cfc7.

## Limitations and next steps

This experiment used one machine, five random samples per family and
length, and one input per structured family and length. It did not
measure memory use, count skipped splits, or establish the largest
practical input size.

The results demonstrate practical improvements on the tested inputs.
They do not establish a better worst-case bound: the current upper
bounds remain O(n^5) time and O(n^3) auxiliary space.

A useful next step is to count evaluated and skipped splits in a
separate untimed analysis, then compare those counts with the observed
runtime differences.

## Data files

- [Raw timings](../results/mac_pruning/timings.csv)
- [Summary statistics](../results/mac_pruning/summary.csv)
- [Experiment metadata](../results/mac_pruning/metadata.json)
