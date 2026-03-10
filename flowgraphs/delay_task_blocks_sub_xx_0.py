"""
Embedded Python Blocks:

Auto-generated placeholder replaced with an automatic delay estimator.
"""

import numpy as np
from collections import deque
from gnuradio import gr


class blk(gr.sync_block):
    """Estimate a fixed integer delay and output the aligned stream difference."""

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
        if self._locked:
            return
        needed = self.training_len + self.max_delay
        if len(self._delayed_training) < needed or len(self._direct_training) < needed:
            return

        delayed = np.asarray(self._delayed_training, dtype=np.int8)
        direct = np.asarray(self._direct_training, dtype=np.int8)
        window = min(self.training_len, len(direct), len(delayed) - self.max_delay)
        if window <= 0:
            return

        best_delay = 0
        best_score = -1
        for candidate in range(self.max_delay + 1):
            score = int(np.count_nonzero(delayed[candidate:candidate + window] == direct[:window]))
            if score > best_score:
                best_score = score
                best_delay = candidate

        self._delay = best_delay
        self._history = deque(direct[-(self._delay + 1):], maxlen=self._delay + 1)
        self._delayed_training = []
        self._direct_training = []
        self._locked = True

    def work(self, input_items, output_items):
        delayed = input_items[0]
        direct = input_items[1]
        out = output_items[0]

        if not self._locked:
            self._delayed_training.extend(int(x) for x in delayed.tolist())
            self._direct_training.extend(int(x) for x in direct.tolist())
            max_cache = self.training_len + self.max_delay + 32
            if len(self._delayed_training) > max_cache:
                self._delayed_training = self._delayed_training[-max_cache:]
                self._direct_training = self._direct_training[-max_cache:]
            self._try_lock()
            out[:] = 0.0
            return len(out)

        for index, sample in enumerate(direct):
            self._history.append(int(sample))
            if len(self._history) < self._delay + 1:
                out[index] = 0.0
            else:
                out[index] = float(int(delayed[index]) - int(self._history[0]))
        return len(out)
