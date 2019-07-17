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
from pathlib import Path

from .split import split_fastqs, DEFAULT_COMPRESSION_LEVEL, DEFAULT_GROUP_SIZE, DEFAULT_THREADS_PER_FILE

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
    parser.add_argument("-g", "--group-size", type=int,
                        default=DEFAULT_GROUP_SIZE,
                        help=argparse.SUPPRESS
                        # help="Specify the group size. This will set how "
                        #      "fine-grained the fastq distribution will be."
                        #      " Default: {0}".format(DEFAULT_GROUP_SIZE)
                        )

    return parser


def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()

    split_fastqs(parsed_args.input,
                 parsed_args.output,
                 compression_level=parsed_args.compression_level,
                 threads_per_file=parsed_args.threads_per_file
                 )


if __name__ == "__main__":
    main()
