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

# cython: language_level=3

import io
from typing import List

def filesplitter(input_handle: io.BufferedReader,
                 output_handles: List[io.BufferedWriter],
                 lines_per_block = 100):
    # cdef bytes line  # Faster to not type.
    cdef unsigned int blocksize = lines_per_block
    cdef unsigned int i = 0
    cdef unsigned int group_no = 0
    cdef unsigned int number_of_output_files = len(output_handles)
    if number_of_output_files < 1:
        raise ValueError("The number of outputfiles should be at least 1.")

    # for line in handle is the fastest way to read lines in python that I
    # know of. Implementations with next(handle) or handle.readline are
    # slower.
    for line in input_handle:
        if i == 0:
            # Alias write to output function. This gives a massive speedup.
            write_to_output = output_handles[group_no].write
            group_no += 1
            if group_no == number_of_output_files:  # See below for why not modulo.
                group_no = 0
        write_to_output(line)
        i += 1
        if i == blocksize:
            i = 0

        # This works, if blocksize == 100. Then i will be [0, 1, 2, .., 98, 99]
        # which is exactly 100 numbers.

        # The resetting of i at blocksize accomplishes two things:
        # 1. i will never be larger than blocksize. We do not have to keep
        # counting to infinity, which will lead to an integer overflow.
        # 2. We do not have to use modulo (i % blocksize) == 0 to determine
        # whether the blocksize is reached. Direct comparison is faster than
        # modulo.
