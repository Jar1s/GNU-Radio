# GNU Radio Variant B-3

This repository contains a solution for 2 selected tasks from the assignment:

- `B` Automatic delay control
- `C` Hamming `(7,4)` encoder/decoder

The source of truth is the `.grc` flowgraphs in [`flowgraphs`](./flowgraphs).  
GNU Radio may generate helper Python files locally when the flowgraphs are opened or run, but those generated files are not required in version control.

## Repository Contents

Files included in this repository:

- `flowgraphs/Variant_B_Delay.grc`
- `flowgraphs/Variant_B_Hamming.grc`
- `flowgraphs/Variant_B_Error_Rate.grc`
- `README.md`

The final report is intentionally not stored in this repository and is submitted separately as a Word/PDF document.

Files that should not be relied on in version control:

- generated Python helpers such as `flowgraphs/*.py`
- cache files such as `__pycache__/`
- temporary editor files and backups

## GNU Radio Version

Recommended target:

- GNU Radio `3.10.x`

The flowgraphs were prepared for GNU Radio `3.10.12.0`.  
For best reproducibility, use the same major/minor release.

## Installation

### Option A: Radioconda

Radioconda is the simplest choice for a clean GNU Radio installation.

Reference:

- <https://github.com/radioconda/radioconda-installer>
- <https://github.com/ryanvolz/radioconda/releases/>

After installation, start GNU Radio Companion with:

```bash
source "$HOME/radioconda/bin/activate"
gnuradio-companion
```

### Option B: Existing GNU Radio installation

If GNU Radio `3.10.x` is already installed and GNU Radio Companion can open `.grc` files with Embedded Python Blocks, the repository should run without extra dependencies.

## Cross-Platform Notes

The custom logic is implemented in Embedded Python Blocks and does not use hardcoded machine-specific paths.

Practical expectation:

- macOS: expected to work with GNU Radio `3.10.x`
- Linux: expected to work with GNU Radio `3.10.x`
- Windows: should work if GNU Radio Companion and Embedded Python Blocks are available, but this was not tested directly

If the flowgraph is opened on another machine, GNU Radio may regenerate local helper `.py` files automatically. This is normal.

## How To Run

### Task B

1. Open [`flowgraphs/Variant_B_Delay.grc`](./flowgraphs/Variant_B_Delay.grc).
2. Run the flowgraph.
3. Set `Manual Delay` to a non-zero value, for example `19`.
4. Observe the `Compensated Delay` plot.
5. If the manual delay is changed while running, press `Re-run Auto Delay` to force a new delay search.

Expected result:

- after the initial estimation phase, the output should stay close to zero
- after pressing `Re-run Auto Delay`, the block should converge again for the new delay

### Task C

1. Open [`flowgraphs/Variant_B_Hamming.grc`](./flowgraphs/Variant_B_Hamming.grc).
2. Run the flowgraph.
3. Compare the BER outputs of both branches.

Expected result:

- the Hamming-coded branch should perform better than the uncoded branch

## Report

According to the assignment, the report should contain:

- description of the solution
- source code with commentary
- guide for downloading and using the implemented blocks
- any additional relevant observations

This repository contains only the implementation and usage notes. The final report is prepared separately for submission.

## Verification

Task `B` is correct if:

- the delay is non-zero
- the compensation still drives the difference close to zero

Task `C` is correct if:

- the flowgraph runs without block errors
- the BER result of the coded branch is better than the uncoded branch

## Reproducibility

To make the project reproducible on another machine:

1. clone the repository
2. install GNU Radio `3.10.x`
3. open the `.grc` flowgraphs directly
4. let GNU Radio regenerate any local helper files if needed
5. run the flowgraphs with the provided settings

The important part to preserve is the `.grc` source, not the generated Python helper files.
