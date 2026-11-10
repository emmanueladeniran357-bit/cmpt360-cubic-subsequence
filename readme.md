# CMPT 360 — Longest Cubic Subsequence

## Problem

Given a sequence S, find a longest subsequence of the form XXX, where X is a sequence repeated three times. Selected symbols must preserve their order in S, and each position may be used at most once. The block X may be empty.

The output must be an actual longest cubic subsequence, not only its length.

## Project status

The exact exhaustive-search baseline and the first exact split-and-DP algorithm are implemented and tested. Further optimizations, special-case investigations, and scalability experiments are still pending.

## Code files

- `baseline.py`: implemented exact exhaustive-search reference algorithm.
- `fasterAlgo.py`: implemented exact split-and-DP algorithm using three-sequence LCS.
- `tests/test_baseline.py`: supporting baseline correctness tests.
- `tests/test_fasterAlgo.py`: supporting LCS, differential, and command-line tests.

The files under `tests/` are supporting checks, not additional main algorithms.

Requires Python 3 and its standard library only; no packages need installing.

## Run the baseline

From the repository directory:

```bash
python3 baseline.py "atcgtatgcatgca"
python3 baseline.py "abcabcabc"
python3 baseline.py ""
```

Every character is a symbol, including spaces; comparisons are case-sensitive. Quote the input to preserve it as one command-line argument. The empty sequence is passed as `""`.

For the assignment example, the baseline returns `X = atc`, `C = atcatcatc`, and length 9. This differs from the handout's `atgatgatg`, but both are valid optimal answers. The program prints the full cubic subsequence, its repeated block, its length, and elapsed algorithm time. Timings exclude argument parsing and printing.

**Start with short inputs:** this baseline has exponential running time. Correctness checks are not a scalability study, and no largest practical input size has been established yet.

## Baseline algorithm

For each positive candidate length divisible by three, enumerate all increasing tuples of positions of that length using `itertools.combinations`. Build each candidate from those positions, split it into three equal blocks, and retain it if the blocks match and it is longer than the best answer found. Initialize the best answer to the empty string. Generate candidates one at a time.

`itertools.combinations` is a standard-library enumeration utility, not an advanced optimization algorithm. The baseline does not use dynamic programming or claim a novel contribution. When several longest answers exist, it keeps the first one encountered in position enumeration order.

### Correctness argument

1. Every constructed candidate is a subsequence: its positions are distinct and increasing.
2. A candidate is accepted only if its three equal-length blocks are identical. Therefore every stored answer is cubic. The initial empty answer is also valid.
3. Every nonempty cubic subsequence has length divisible by three and some increasing tuple of positions. The loops enumerate that length and tuple, so every feasible nonempty answer is examined. Equal strings arising from different tuples may be examined more than once; this does not affect correctness.
4. After any number of candidates, `best` is a longest valid candidate examined so far, including the empty answer. The update preserves this invariant. Since every feasible answer is examined, the final answer has maximum length.

### Complexity

There are at most `2^n` subsets of the `n` positions. The baseline examines only those with positive size divisible by three. Constructing and checking one candidate takes `O(n)` time, so the running-time upper bound is `O(n * 2^n)` under the usual RAM model. The position iterator, candidate, block slices, and best answer use `O(n)` auxiliary space; all subsequences are never stored at once.

## Run correctness tests

```bash
python3 -m unittest discover -s tests -v
```

The baseline tests contain 15 explicit cases, all 511 strings over `{a,b}` of lengths zero through eight, and command-line checks for the assignment example and empty input. It checks that each returned string is cubic, is a subsequence of the input, and has the expected optimal length.

For exhaustive small-input comparison, an independent oracle enumerates possible repeated blocks over the input alphabet and checks whether three copies occur as a subsequence using a left-to-right scan. It does not reuse the baseline's position-subset enumeration. All three baseline test methods passed during initial validation. These tests support the implementation; the correctness argument establishes the general result.

## Faster algorithm: split-and-DP

Run the new algorithm with the same input format:

```bash
python3 fasterAlgo.py "atcgtatgcatgca"
python3 fasterAlgo.py "abxabyab"
python3 fasterAlgo.py ""
```

The public function in each algorithm file is named `longest_cubic_subsequence(sequence)` and returns the complete cubic subsequence as a string. The command-line output fields match those of the baseline. Different optimal strings are allowed; compare lengths and validity, not exact strings.

### Splitting the input

For each pair of cuts `1 <= i < j <= n - 1`, form three nonempty consecutive regions:

- `A = sequence[:i]`
- `B = sequence[i:j]`
- `C = sequence[j:]`

Find an actual longest common subsequence `X` of these regions and consider `X * 3`. Keep a longest block across all cuts. Inputs shorter than three have no such splits and return the empty string.

For example, `abx | aby | ab` has common subsequence `ab`, yielding the cubic subsequence `ababab`.

### Three-sequence LCS recurrence

Let `D[a][b][c]` be the LCS length of `A[:a]`, `B[:b]`, and `C[:c]`.

- If any index is zero, the value is zero.
- If `A[a-1] == B[b-1] == C[c-1]`, the value is `1 + D[a-1][b-1][c-1]`.
- Otherwise, the value is the maximum of `D[a-1][b][c]`, `D[a][b-1][c]`, and `D[a][b][c-1]`.

Fill the table in increasing index order. Reconstruct a common subsequence by walking backwards: collect a character and decrement all three indices on a match; otherwise move to a predecessor with the same optimal value. Reverse the collected characters at the end. Ties are resolved deterministically by checking the first, then second, then third index.

### Correctness argument

**LCS table.** If a prefix is empty, no nonempty common subsequence exists. If the three final characters match, an optimal common subsequence can align its last character with these three final positions. Removing that character leaves a common subsequence of the three shortened prefixes, and any optimal common subsequence of those prefixes can be extended by the matching character. This gives the diagonal-plus-one recurrence. If the final characters do not all match, a common subsequence cannot use all three final positions; at least one is unused. The three predecessor states cover these possibilities. Induction on the sum of prefix lengths proves the table values optimal. Backtracking follows these same choices and recovers a sequence of that optimal length.

**Feasibility of a cube.** A common subsequence of the three regions can be selected once from each region. Since the regions are disjoint and consecutive, concatenating these selections gives a valid cubic subsequence of the original input.

**Optimality over cuts.** Take a nonempty optimal cube and its chosen positions. Place one cut immediately after the last chosen position of its first copy, and a second after the last chosen position of its second copy. Each copy then lies in a separate region of an enumerated split. Its repeated block is a common subsequence of those three regions, so the LCS for this split is at least as long. Every candidate is feasible, so no candidate can exceed the true optimum. Taking the longest over all splits therefore returns an optimal cube. If no nonempty cube exists, every split has empty LCS and the empty answer is correct.

### Complexity and limitations

There are `(n-1)(n-2)/2 = O(n^2)` splits for `n >= 3`. For a split with positive region lengths `p, q, r`, its DP table takes `O(p*q*r)` time and space. Reconstructing the block takes `O(p+q+r)` time. Slicing the input also takes `O(n)` per split.

Each split therefore takes at most `O(n^3)` time, giving an overall `O(n^5)` upper bound. Only one split's DP table is retained at a time, so auxiliary space is `O(n^3)`, not `O(n^5)`. Bounds count table entries under the usual RAM model; Python objects add practical overhead.

This is a polynomial-time improvement over the exponential baseline, but fifth-degree growth and cubic space still limit scalability. It is not guaranteed to be faster on every small input. This first version recomputes the LCS table for every split and does not yet prune cuts or reuse tables.

The recurrence and exhaustive enumeration of cuts are straightforward applications of standard techniques. They are the starting implementation, not a claim of original research. Project-specific improvements and special cases remain to be investigated and supported by evidence.

### DP validation

Run the full suite using the existing command:

```bash
python3 -m unittest discover -s tests -v
```

All nine test methods passed after adding the DP algorithm. In addition to the original baseline checks, the new tests cover:

- 3,375 triples of binary strings of lengths zero through three, checking LCS length against independent subsequence enumeration and checking reconstruction in all three inputs.
- All 511 binary inputs of lengths zero through eight, comparing cubic answer lengths against the exact baseline and checking validity.
- 120 reproducible random inputs over `abcd`, with lengths zero through fourteen and seed 360, compared against the baseline.
- The same 15 explicit cases used for the baseline, including the assignment example, ties, case-sensitive symbols, Unicode, and spaces.
- Two length-36 inputs with known full-length cubic answers.
- Command-line checks for the assignment example, empty input, and a sequence containing spaces.

These are correctness checks, not a completed timing or memory study.

## Development milestones

1. Implement the exact baseline and explain its correctness and complexity.
2. Verify small examples and edge cases.
3. Develop and cross-check a faster approach against the baseline.
4. Investigate improvements and special cases, recording successful and unsuccessful attempts.
5. Compare performance on reproducible inputs and interpret the results.
6. Prepare the report, appendix, and submission ZIP.

## Initial correctness checks

- Empty input.
- All distinct symbols.
- No symbol occurring three times.
- A single repeated symbol.
- Three consecutive copies of a block.
- Repeated blocks separated by extra symbols.
- Inputs with several equally long optimal answers.

When optimal answers are not unique, compare their lengths and validity rather than requiring identical output strings.

## Experimental plan

Compare both algorithms on identical inputs. Record input length, alphabet size, input structure, elapsed time, and output length. Record the machine, Python version, random seeds, repetition count, and resource limits used for experiments.

Check correctness before larger timing experiments. Keep observations distinct from predictions and theoretical bounds.

## Report and development evidence

The main report is limited to five pages, with additional evidence in the appendix. Preserve meaningful incremental commits, experimental results, and debugging observations throughout development.

Record standard techniques, project-specific insights, and relevant AI assistance accurately. I drafted the initial README and plan, both algorithm implementations, supporting tests, and the algorithm explanations. The baseline is standard exhaustive search, and the first faster version applies standard three-sequence LCS to all pairs of cuts; neither is presented as an original research contribution. Correctness checks were run for both implementations. Further improvements and scalability experiments are still pending. Update this record as the project develops.
