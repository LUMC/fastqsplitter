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

import argparse
import contextlib
import io
from pathlib import Path
from typing import List

# xopen opens files as normal files, gzip files, bzip2 files or xz files
# depending on extension.
import xopen

# Choose 1 as default compression level. Speed is more important than filesize
# in this application.
DEFAULT_COMPRESSION_LEVEL = 1
DEFAULT_BUFFER_SIZE = 64 * 1024
# With one thread per file (pigz -p 1) pigz uses way less virtual memory
# (10 vs 300 MB for 4 threads) and total CPU time is also decreased.
# Example: 2.3 gb input file file. Five output files.
# TT=Total cpu time. RT=realtime
# Compression level 1: threads=1 RT=58s TT=3m33, threads=4 RT=57s TT=3m45
# Compression level 5: threads=1 RT=1m48 TT=7m53, threads=4 RT=1m23, TT=8m39
# But this is on a 8 thread machine. When using less threads RT will go towards
# TT. Default compression is 1. So default threads 1 makes the most sense.
DEFAULT_THREADS_PER_FILE = 1


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True,
                        help="The fastq file to be scattered.")
    parser.add_argument("-o", "--output", action="append", type=Path,
                        required=True,
                        help="Scatter over these output files. Multiple -o "
                             "flags can be used. The extensions determine "
                             "which compression algorithm will be used. '.gz' "
                             "for gzip, '.bz2' for bzip2, '.xz' for xz. Other "
                             "extensions will use no compression."
                        )
    parser.add_argument("-c", "--compression-level", type=int,
                        default=DEFAULT_COMPRESSION_LEVEL,
                        help="Only applicable when output files have a '.gz' "
                             "extension. Default={0}"
                        .format(DEFAULT_COMPRESSION_LEVEL))
    parser.add_argument("-t", "--threads-per-file", type=int,
                        default=DEFAULT_THREADS_PER_FILE,
                        help="Set the number of compression threads per output"
                             " file. NOTE: more threads are only useful when "
                             "using a compression level > 1. Default={0}"
                             "".format(DEFAULT_THREADS_PER_FILE))

    # BELOW ARGUMENTS ARE FOR BENCHMARKING AND TESTING PURPOSES
    parser.add_argument("-b", "--buffer-size", type=int,
                        default=DEFAULT_BUFFER_SIZE,
                        help=argparse.SUPPRESS)
    return parser


def filesplitter(input_handle: io.BufferedReader,
                 output_handles: List[io.BufferedWriter],
                 lines_per_record: int = 4,
                 buffer_size: int = 64 * 1024):

    # Make sure inputs are sensible.
    if len(output_handles) < 1:
        raise ValueError("The number of output files should be at least 1.")
    if lines_per_record < 1:
        raise ValueError("The number of lines per record should be at least 1."
                         )
    if buffer_size < 1024:
        # This value is arbitrary, but really low values such as 5 or 30 don't
        # make sense.
        raise ValueError("The buffer size should be at least 1024.")

    group_number = 0
    number_of_output_files = len(output_handles)

    while True:
        read_buffer = input_handle.read(buffer_size)
        if read_buffer == b"":
            return

        newline_count = read_buffer.count(b'\n')

        # The chances are paramount that our buffer does not end with \n.
        # The buffer almost always ends  with an incomplete record. Therefore
        # we read all the missing lines. Please note that if
        # newline_count % lines_per_record == 0. That probably means we still
        # have a start of a record after the last \n.
        extra_newlines = lines_per_record - newline_count % lines_per_record
        completed_record = b"".join(input_handle.readline()
                                    for _ in range(extra_newlines))
        output_handles[group_number].write(read_buffer + completed_record)
        # Set the group number for the next group to be written.
        group_number += 1
        if group_number == number_of_output_files:
            group_number = 0


def split_fastqs(input_file: Path, output_files: List[Path],
                 compression_level: int = DEFAULT_COMPRESSION_LEVEL,
                 buffer_size: int = DEFAULT_BUFFER_SIZE,
                 threads_per_file: int = DEFAULT_THREADS_PER_FILE):
    # contextlib.Exitstack allows us to open multiple files at once which
    # are automatically closed on error.
    # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
    with contextlib.ExitStack() as stack:
        input_file = stack.enter_context(
            xopen.xopen(input_file, mode='rb'))
        # xopen implements __next__ by doing next(self._file). As __iter__
        # it returns itself.
        # However using self._file as iterator is much faster.
        if isinstance(input_file, xopen.PipedGzipReader):
            input_fastq = input_file._file
        else:
            input_fastq = input_file
        output_handles = [
            stack.enter_context(xopen.xopen(
                filename=output_file,
                mode='wb',
                compresslevel=compression_level,
                threads=threads_per_file
            )) for output_file in output_files
        ]  # type: List[io.BufferedWriter]
        filesplitter(input_handle=input_fastq,
                     output_handles=output_handles,
                     buffer_size=buffer_size,
                     lines_per_record=4)


def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()

    split_fastqs(parsed_args.input,
                 parsed_args.output,
                 compression_level=parsed_args.compression_level,
                 threads_per_file=parsed_args.threads_per_file,
                 buffer_size=parsed_args.buffer_size)


if __name__ == "__main__":  # pragma: no cover
    main()
