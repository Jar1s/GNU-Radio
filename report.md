# Report: Variant B-3 GNU Radio

## Selected Tasks

The assignment required completing 2 out of 3 tasks. The implemented tasks are:

- `B` Automatic delay control
- `C` Hamming `(7,4)` encoder/decoder

These two tasks were selected as the lowest-risk combination with the clearest verification criteria.

## Task B: Automatic Delay Control

The provided flowgraph splits a byte stream into two branches. One branch is delayed by an integer number of samples. The goal was to find this delay automatically and compensate it.

The solution uses an Embedded Python Block named `Auto Delay Compensation`.

Implementation idea:

1. Collect a short training window from both branches.
2. Test all candidate delays from `0` to `100`.
3. Choose the delay with the highest equality score between the delayed stream and the shifted direct stream.
4. Keep a short history of the direct branch and subtract the aligned samples from the delayed branch.

This keeps the original flowgraph simple and avoids adding a more complex feedback/control path.

## Task C: Hamming (7,4)

The provided flowgraph already contained placeholder `Copy` blocks where the Hamming coder and decoder should be added.

The solution replaces these placeholders with two Embedded Python Blocks:

- `Hamming (7,4) Encoder`
- `Hamming (7,4) Decoder`

The encoder takes 4 unpacked data bits and generates a 7-bit codeword:

```text
[p1, p2, d1, p3, d2, d3, d4]
```

Parity equations:

```text
p1 = d1 xor d2 xor d4
p2 = d1 xor d3 xor d4
p3 = d2 xor d3 xor d4
```

The decoder computes the syndrome, detects a single-bit error position, corrects it, and restores the original data bits:

```text
[d1, d2, d3, d4]
```

## Source Code Notes

The complete implementation is embedded directly in the `.grc` files, so the solution is self-contained:

- `flowgraphs/Variant_B_Delay.grc`
- `flowgraphs/Variant_B_Hamming.grc`

This was chosen because the assignment explicitly allows the use of Embedded Python Blocks.

## How To Use

1. Install GNU Radio with Radioconda.
2. Open the corresponding `.grc` file in GNU Radio Companion.
3. Run the flowgraph with the provided settings.
4. Observe the output plots and BER indicators.

## Expected Results

- In Task `B`, the compensated difference should approach zero after the training phase.
- In Task `C`, the Hamming-coded branch should achieve lower BER than the uncoded reference branch.

## Reproducibility

The repository contains:

- the provided flowgraphs,
- the modified implementations,
- a short `README.md`,
- this report draft.

For final submission, screenshots of successful runs should be added after verifying the solution on a machine with GNU Radio installed.
