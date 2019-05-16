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

from pathlib import Path
from typing import List

# xopen opens files as normal files, gzip files, bzip2 files or xz files
# depending on extension.
import xopen

# Choose 1 as default compression level. Speed is more important than filesize
# in this application.
DEFAULT_COMPRESSION_LEVEL = 1


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
    return parser


def split_fastqs(input_file: Path, output_files: List[Path],
                 compression_level: int = DEFAULT_COMPRESSION_LEVEL,
                 group_size: int = 100):
    # contextlib.Exitstack allows us to open multiple files at once which
    # are automatically closed on error.
    # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
    with contextlib.ExitStack() as stack:
        input_fastq = stack.enter_context(
            xopen.xopen(input_file, mode='rb'))  # type: xopen.PipedGzipReader
        output_handles = [
            stack.enter_context(xopen.xopen(
                filename=output_file,
                mode='wb',
                compresslevel=compression_level
            )) for output_file in output_files
        ]  # type: List[xopen.PipedGzipWriter]

        i = 0
        number_of_output_files = len(output_handles)
        fastq_eof_reached = False
        while not fastq_eof_reached:
            # By using modulo we pick one file at a time and make sure all
            # files are written to equally.
            file_to_write = output_handles[i % number_of_output_files]

            # Make sure a multiple of 4 lines is written as each record is
            # 4 lines.
            for j in range(group_size * 4):
                try:
                    # next(handle) equals handle.readline() but throws a
                    # StopIteration error if the lines is ''.
                    file_to_write.write(next(input_fastq))
                except StopIteration:
                    fastq_eof_reached = True
                    break
            i += 1


def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()
    split_fastqs(parsed_args.input,
                 parsed_args.output,
                 compression_level=parsed_args.compression_level)


if __name__ == "__main__":
    main()
