# Report: Variant B-3 GNU Radio

## 1. Assignment Overview

The assignment required implementing 2 out of 3 tasks in GNU Radio.  
The selected tasks were:

- `B` Automatic delay control
- `C` Hamming `(7,4)` encoder/decoder

These tasks were selected because they have clear verification criteria and can be implemented directly with Embedded Python Blocks inside the provided flowgraphs.

## 2. Environment

The implementation was tested with GNU Radio installed through Radioconda on macOS.

Project files:

- `flowgraphs/Variant_B_Delay.grc`
- `flowgraphs/Variant_B_Hamming.grc`
- `README.md`

The final repository is intended to be reproducible on another machine with the same GNU Radio installation method.

## 3. Task B: Automatic Delay Control

### 3.1 Goal

In the provided `Variant_B_Delay.grc` flowgraph, the input byte stream is split into two branches. One branch is delayed by an integer number of samples. The goal was to detect this delay automatically and compensate it so that the difference between both aligned signals is approximately zero.

### 3.2 Solution

The solution was implemented as an Embedded Python Block named `Auto Delay Compensation`.

The block:

1. reads both input streams,
2. stores an initial training window,
3. tries all candidate delays from `0` to `100`,
4. selects the delay with the highest equality score,
5. aligns the direct branch internally,
6. outputs the sample-by-sample difference after compensation.

This approach avoids manual tuning and keeps the verification simple.

### 3.3 Source Code with Commentary

Key logic of the delay estimator:

```python
import numpy as np
from collections import deque
from gnuradio import gr


class blk(gr.sync_block):
    def __init__(self, max_delay=100, training_len=256):
        gr.sync_block.__init__(
            self,
            name='Auto Delay Compensation',
            in_sig=[np.int8, np.int8],
            out_sig=[np.float32],
        )
        self.max_delay = int(max_delay)
        self.training_len = int(training_len)
        self._delayed_training = []
        self._direct_training = []
        self._history = deque(maxlen=self.max_delay + 1)
        self._locked = False
        self._delay = 0

    def _try_lock(self):
        # Wait until enough training data is collected from both branches.
        needed = self.training_len + self.max_delay
        if len(self._delayed_training) < needed or len(self._direct_training) < needed:
            return

        delayed = np.asarray(self._delayed_training, dtype=np.int8)
        direct = np.asarray(self._direct_training, dtype=np.int8)
        best_delay = 0
        best_score = -1

        for candidate in range(self.max_delay + 1):
            # Compare each possible shift and keep the one with the best match.
            score = int(np.count_nonzero(
                delayed[candidate:candidate + self.training_len] == direct[:self.training_len]
            ))
            if score > best_score:
                best_score = score
                best_delay = candidate

        self._delay = best_delay
        # Keep only the amount of history needed for aligned subtraction.
        self._history = deque(direct[-(self._delay + 1):], maxlen=self._delay + 1)
        self._locked = True
```

Commentary:

- `training_len` defines how many samples are used for initial estimation.
- Each candidate delay is evaluated by comparing the delayed branch with a shifted version of the direct branch.
- The delay with the highest match score is selected.
- After delay detection, the block keeps a short history buffer and subtracts aligned samples.

## 4. Task C: Hamming (7,4)

### 4.1 Goal

In `Variant_B_Hamming.grc`, the provided placeholders had to be replaced by a Hamming `(7,4)` encoder and decoder. The verification criterion was that the Hamming-coded branch should achieve a lower BER than the uncoded branch.

### 4.2 Solution

Two Embedded Python Blocks were added:

- `Hamming (7,4) Encoder`
- `Hamming (7,4) Decoder`

The encoder transforms every 4 data bits into a 7-bit codeword.  
The decoder computes the syndrome, detects a single-bit error, corrects it, and restores the original 4 information bits.

### 4.3 Source Code with Commentary

Encoder:

```python
import numpy as np
from gnuradio import gr


class blk(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name='Hamming (7,4) Encoder',
            in_sig=[np.int8],
            out_sig=[np.int8],
        )
        self._buffer = []

    def general_work(self, input_items, output_items):
        incoming = input_items[0]
        self._buffer.extend(int(x) & 1 for x in incoming.tolist())
        self.consume_each(len(incoming))

        out = output_items[0]
        blocks = min(len(self._buffer) // 4, len(out) // 7)
        out_index = 0

        for _ in range(blocks):
            # Read 4 information bits.
            d1, d2, d3, d4 = [self._buffer.pop(0) for _ in range(4)]
            # Compute the three Hamming parity bits.
            p1 = d1 ^ d2 ^ d4
            p2 = d1 ^ d3 ^ d4
            p3 = d2 ^ d3 ^ d4
            # Output layout: parity and data bits in Hamming (7,4) order.
            codeword = (p1, p2, d1, p3, d2, d3, d4)
            for bit in codeword:
                out[out_index] = bit
                out_index += 1

        return out_index
```

Commentary:

- The input stream is treated as unpacked bits.
- Four input bits are grouped into one block.
- Three parity bits are computed.
- The resulting codeword layout is `[p1, p2, d1, p3, d2, d3, d4]`.

Decoder:

```python
import numpy as np
from gnuradio import gr


class blk(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name='Hamming (7,4) Decoder',
            in_sig=[np.int8],
            out_sig=[np.int8],
        )
        self._buffer = []

    def general_work(self, input_items, output_items):
        incoming = input_items[0]
        self._buffer.extend(int(x) & 1 for x in incoming.tolist())
        self.consume_each(len(incoming))

        out = output_items[0]
        blocks = min(len(self._buffer) // 7, len(out) // 4)
        out_index = 0

        for _ in range(blocks):
            codeword = [self._buffer.pop(0) for _ in range(7)]
            # Compute syndrome bits for single-error detection.
            s1 = codeword[0] ^ codeword[2] ^ codeword[4] ^ codeword[6]
            s2 = codeword[1] ^ codeword[2] ^ codeword[5] ^ codeword[6]
            s3 = codeword[3] ^ codeword[4] ^ codeword[5] ^ codeword[6]
            error_position = s1 + (s2 << 1) + (s3 << 2)
            if 1 <= error_position <= 7:
                # Correct the detected bit error.
                codeword[error_position - 1] ^= 1
            # Extract only the original data bits.
            for bit in (codeword[2], codeword[4], codeword[5], codeword[6]):
                out[out_index] = bit
                out_index += 1

        return out_index
```

Commentary:

- Seven received bits are processed as one Hamming codeword.
- The syndrome bits `s1`, `s2`, and `s3` determine the position of a single-bit error.
- If an error is detected, the corresponding bit is flipped.
- The original data bits are then extracted from the corrected codeword.

## 5. Guide for Downloading and Using the Blocks

### 5.1 Download

Clone the repository:

```bash
git clone https://github.com/Jar1s/GNU-Radio.git
cd GNU-Radio
```

### 5.2 Start GNU Radio

If Radioconda is installed:

```bash
source "$HOME/radioconda/bin/activate"
gnuradio-companion
```

### 5.3 Run Task B

1. Open `flowgraphs/Variant_B_Delay.grc`.
2. Run the flowgraph.
3. Set `Manual Delay` to a non-zero value, for example `19`.
4. Observe the output in the `Compensated Delay` plot.

Expected behavior:

- after startup, the automatic block estimates the delay,
- the output remains close to zero after compensation.

### 5.4 Run Task C

1. Open `flowgraphs/Variant_B_Hamming.grc`.
2. Run the flowgraph.
3. Observe the BER indicators.

Expected behavior:

- the BER of the Hamming-coded branch should be better than the uncoded branch.

## 6. Results

### 6.1 Task B

The delay flowgraph was executed with a non-zero manual delay.  
The output plot remained close to zero after compensation, which confirms that the automatic delay estimation worked correctly.

Screenshot to insert:

- `Task_B_Result.png`

### 6.2 Task C

The Hamming flowgraph was executed successfully.  
The measured BER values showed that the Hamming-coded branch achieved a lower error rate than the uncoded branch.

Observed example:

- without Hamming: approximately `-4.530661`
- with Hamming: approximately `-4.860650`

In this measurement format, the more negative value corresponds to better BER performance, so the coded branch performed better.

Screenshot to insert:

- `Task_C_Result.png`

## 7. Relevant Notes

- The assignment was implemented using Embedded Python Blocks, which is explicitly allowed in the task description.
- The original verification settings of the flowgraphs were preserved as much as possible.
- Only the required implementation points for tasks `B` and `C` were changed.
- The repository keeps the `.grc` flowgraphs as the source of truth; generated runtime helper files are not required for submission.

## 8. Conclusion

Both selected tasks were implemented successfully:

- Task `B` automatically estimates and compensates stream delay.
- Task `C` implements Hamming `(7,4)` coding and improves BER compared to the uncoded branch.

The repository contains the final flowgraphs, documentation, and usage instructions needed to reproduce the solution on another machine with GNU Radio 3.10.
