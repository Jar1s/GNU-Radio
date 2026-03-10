"""
Embedded Python block implementing a streaming Hamming (7,4) decoder.
"""

import numpy as np
from gnuradio import gr


class blk(gr.basic_block):
    """Decode unpacked Hamming (7,4) codewords and correct one bit errors."""

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
            s1 = codeword[0] ^ codeword[2] ^ codeword[4] ^ codeword[6]
            s2 = codeword[1] ^ codeword[2] ^ codeword[5] ^ codeword[6]
            s3 = codeword[3] ^ codeword[4] ^ codeword[5] ^ codeword[6]
            error_position = s1 + (s2 << 1) + (s3 << 2)
            if 1 <= error_position <= 7:
                codeword[error_position - 1] ^= 1
            for bit in (codeword[2], codeword[4], codeword[5], codeword[6]):
                out[out_index] = bit
                out_index += 1

        return out_index
