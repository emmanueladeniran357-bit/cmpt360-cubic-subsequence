# CMPT 360 — Longest Cubic Subsequence

## Problem

Given a sequence S, find a longest subsequence of the form XXX, where X is a sequence repeated three times. Selected symbols must preserve their order in S, and each position may be used at most once. The block X may be empty.

The output must be an actual longest cubic subsequence, not only its length.

## Project status

The exact exhaustive-search baseline is implemented and tested. The faster algorithm and scalability experiments are still pending.

## Code files

- `baseline.py`: implemented exact exhaustive-search reference algorithm.
- `fasterAlgo.py`: planned improved algorithm; not implemented yet.
- `tests/test_baseline.py`: supporting correctness tests, not a separate main algorithm.

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

The suite contains 15 explicit cases, all 511 strings over `{a,b}` of lengths zero through eight, and command-line checks for the assignment example and empty input. It checks that each returned string is cubic, is a subsequence of the input, and has the expected optimal length.

For exhaustive small-input comparison, an independent oracle enumerates possible repeated blocks over the input alphabet and checks whether three copies occur as a subsequence using a left-to-right scan. It does not reuse the baseline's position-subset enumeration. All three test methods passed during initial validation. These tests support the implementation; the correctness argument establishes the general result.

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

Record standard techniques, project-specific insights, and relevant AI assistance accurately. ChatGPT drafted the initial README and plan, the baseline implementation, supporting tests, and the baseline explanation. The implemented baseline is standard exhaustive search, not an original algorithmic contribution. Small-input correctness checks were run; faster-algorithm design and scalability experiments are still pending. Update this record as the project develops.
