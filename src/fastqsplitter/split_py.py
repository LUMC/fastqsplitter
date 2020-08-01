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
                 lines_per_record: int = 4,
                 buffer_size: int = 64 * 1024):

    # Make sure inputs are sensible.
    if len(output_handles) < 1:
        raise ValueError("The number of output files should be at least 1.")
    if lines_per_record < 1:
        raise ValueError("The number of lines per record should be at least 1.")
    if buffer_size < 1:
        raise ValueError("The buffer size should be at least 1.")

    group_number = 0
    number_of_output_files = len(output_handles)
    old_read_buffer = b""
    while True:
        new_reads = input_handle.read(buffer_size)
        read_buffer = old_read_buffer + new_reads

        if new_reads == b"":
            output_handles[group_number].write(read_buffer)
            return

        newline_count = read_buffer.count(b'\n')
        end_newline = read_buffer.rfind(b'\n')
        overshoot_newlines = newline_count % lines_per_record
        for i in range(overshoot_newlines):
            end_newline = read_buffer.rfind(b'\n', 0, end_newline)
        output_handles[group_number].write(read_buffer[:end_newline + 1])
        # Set the group number for the next group to be written.
        group_number += 1
        if group_number == number_of_output_files:
            group_number = 0
        old_read_buffer = read_buffer[end_newline + 1:]
