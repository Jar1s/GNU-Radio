# GNU Radio Variant B-3

This repository implements the easiest two required tasks from the assignment:

- `B` Automatic delay control
- `C` Hamming `(7,4)` encoder/decoder

The provided flowgraphs are stored in [`flowgraphs`](./flowgraphs).

## Environment

Recommended installation is Radioconda:

```bash
curl -fsSL https://raw.githubusercontent.com/ryanvolz/radioconda-installer/main/install-radioconda.sh | bash
source "$HOME/radioconda/etc/profile.d/conda.sh"
conda activate base
conda install gnuradio
gnuradio-companion
```

The assignment PDF recommends the Radioconda installer:
https://github.com/radioconda/radioconda-installer

## What Was Implemented

### Task B

[`flowgraphs/Variant_B_Delay.grc`](./flowgraphs/Variant_B_Delay.grc) now contains an Embedded Python Block called `Auto Delay Compensation`.

It:
- observes the delayed stream and the direct stream,
- estimates a fixed integer delay from the training samples,
- aligns the direct stream internally,
- outputs the compensated difference.

Expected result:
- set `Manual Delay` to a non-zero value,
- run the flowgraph,
- after the initial training period the output should settle close to zero.

### Task C

[`flowgraphs/Variant_B_Hamming.grc`](./flowgraphs/Variant_B_Hamming.grc) now replaces the two placeholder `Copy` blocks with:

- `Hamming (7,4) Encoder`
- `Hamming (7,4) Decoder`

Both blocks operate on unpacked bit streams:
- encoder maps every 4 data bits to 7 coded bits,
- decoder corrects a single-bit error in each 7-bit codeword and restores the original 4 data bits.

Expected result:
- run the flowgraph,
- compare the BER indicators,
- the Hamming branch should show fewer errors than the uncoded branch.

## How To Run

1. Open `gnuradio-companion`.
2. Open [`flowgraphs/Variant_B_Delay.grc`](./flowgraphs/Variant_B_Delay.grc) and run it.
3. Open [`flowgraphs/Variant_B_Hamming.grc`](./flowgraphs/Variant_B_Hamming.grc) and run it.

GNU Radio generates embedded Python helper files automatically when saving or running the flowgraph.

## Verification Checklist

- `Variant_B_Delay.grc`
  - set non-zero system delay,
  - run the flowgraph,
  - confirm that the compensated output approaches zero.

- `Variant_B_Hamming.grc`
  - run the flowgraph with the provided settings,
  - confirm that the Hamming-coded branch reports lower BER than the uncoded branch.

## Current Limitation

Runtime verification was not completed in this repository because GNU Radio is not installed in the current environment.
