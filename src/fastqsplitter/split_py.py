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
    # An input handle should be an iterable, but since this package uses xopen
    # we cannot be sure.
    fastq_iterator = iter(input_handle)
    # Alias the readline method for extra speed.
    # next(handle) equals handle.readline() but throws a
    # StopIteration error if the lines is ''.
    readline = fastq_iterator.__next__
    not_at_end_of_file = True

    while not_at_end_of_file:
        block = []
        # This is the fastest way to read blocks of lines in pure python.
        # The method used in split_cy is slower in pure python because it
        # stores the counting integer as a PyObject.
        for j in range(lines_per_block):
            try:
                block.append(readline())
            # Readline should throw a StopIteration at EOF
            except StopIteration:
                not_at_end_of_file = False
                break

        # Select the output handle and write the block to it.
        output_handles[group_number].write(b"".join(block))

        # Set the group number for the next group to be written.
        group_number += 1
        if group_number == number_of_output_files:
            group_number = 0
