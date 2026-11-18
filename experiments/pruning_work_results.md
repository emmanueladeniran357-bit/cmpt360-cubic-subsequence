# Work avoided by region-length pruning

## Method

The counting script analyzed the same 65 inputs used in the Mac
pruning experiment. This was a separate untimed analysis.

It counted calls to the existing LCS helper without duplicating
the pruning rule. For each evaluated split with region lengths
p, q, and r, it counted p*q*r DP recurrence updates.

These counts exclude table initialization, slicing, reconstruction,
and pruning checks. They are not measurements of memory use or time.

## Results at input length 36

For random families, each percentage is the median across five inputs.
Each structured family contains one input at this length.

| Input family | Splits skipped | DP updates avoided |
|---|---:|---:|
| Random binary | 82.02% | 71.12% |
| Random eight symbols | 47.39% | 25.94% |
| Single symbol | 97.98% | 97.76% |
| Three copies | 87.39% | 87.32% |
| All distinct | 0.00% | 0.00% |

Every length-36 input has 595 possible splits. The original algorithm
performs 501,942 recurrence updates across those splits.

For the single-symbol input, pruning evaluated 12 splits and performed
11,232 updates. For the three-copy input, it evaluated 75 splits and
performed 63,638 updates.

The all-distinct input evaluated all 595 splits and performed all
501,942 updates.

## Interpretation

The work counts support the observed timing differences.
At length 36, single-symbol and three-copy inputs avoided much more
DP work than random eight-symbol inputs.

Random binary inputs also avoided a larger fraction of DP updates
than random eight-symbol inputs, consistent with their larger
measured median speedup at this length.

The all-distinct case explains a limitation: the best block remains
empty, so the region-length rule cannot reject any nonempty split.
The algorithm performs the original DP work plus pruning checks.

Counting skipped splits alone can overstate the work reduction.
For random eight-symbol inputs at length 36, the median skipped-split
fraction was 47.39%, but the median avoided-update fraction was
25.94%. Different splits require different amounts of DP work.

Update-reduction factors need not equal runtime speedups because
other operations and timing variation also affect execution time.

## Validation and limitations

All 65 returned answers passed cubic-structure and subsequence checks
and matched the answer lengths saved in the timing summary.

The supporting tests passed for inputs without splits, a distinct
input with no pruning, and a repeated-symbol input with known counts.

The CSV records hashes of the input summary, both algorithm source
files, and the counting script.

The counts are deterministic for these inputs and this implementation.
They do not establish a better worst-case complexity bound or show
that the tested inputs represent all possible inputs.

## Supporting files

- [Work counts](../results/mac_pruning_counts.csv)
- [Timing analysis](pruning_results.md)
- [Counting script](count_pruning.py)
