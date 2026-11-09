# CMPT 360 — Longest Cubic Subsequence

## Problem

Given a sequence S, find a longest subsequence of the form XXX, where X is a sequence repeated three times. Selected symbols must preserve their order in S, and each position may be used at most once. The block X may be empty.

The output must be an actual longest cubic subsequence, not only its length.

## Project status

Initial project setup. Neither algorithm has been implemented yet.

## Planned code files

- `baseline.py`: a straightforward exact reference algorithm.
- `fasterAlgo.py`: an improved algorithm using techniques understandable from the course.

Python 3 and its standard library are the planned implementation environment. Exact run commands will be added when implementations are available.

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

Record standard techniques, project-specific insights, and relevant AI assistance accurately. This initial README and project plan were drafted with ChatGPT assistance; algorithm implementations and experiments are still pending.
