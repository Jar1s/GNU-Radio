"""
Embedded Python block implementing a streaming Hamming (7,4) encoder.
"""

import numpy as np
from gnuradio import gr


class blk(gr.basic_block):
    """Encode unpacked input bits using Hamming (7,4)."""

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
            d1, d2, d3, d4 = [self._buffer.pop(0) for _ in range(4)]
            p1 = d1 ^ d2 ^ d4
            p2 = d1 ^ d3 ^ d4
            p3 = d2 ^ d3 ^ d4
            codeword = (p1, p2, d1, p3, d2, d3, d4)
            for bit in codeword:
                out[out_index] = bit
                out_index += 1

        return out_index
