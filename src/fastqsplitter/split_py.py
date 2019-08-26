#!/usr/bin/env python3

# Copyright (c) 2019 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
from typing import List


def filesplitter(input_handle: io.BufferedReader,
                 output_handles: List[io.BufferedWriter],
                 lines_per_block=100):

    # Make sure inputs are sensible.
    if len(output_handles) < 1:
        raise ValueError("The number of output files should be at least 1.")
    if lines_per_block < 1:
        raise ValueError("The number of lines per block should be at least 1.")

    group_number = 0
    number_of_output_files = len(output_handles)
    fastq_iterator = iter(input_handle)
    readline = fastq_iterator.__next__
    not_at_end_of_file = True

    while not_at_end_of_file:
        block = []
        for j in range(lines_per_block):
            try:
                # next(handle) equals handle.readline() but throws a
                # StopIteration error if the lines is ''.
                block.append(readline())
            except StopIteration:
                not_at_end_of_file = False
                break

        output_handles[group_number].write(b"".join(block))
        group_number += 1
        if group_number == number_of_output_files:
            group_number = 0
