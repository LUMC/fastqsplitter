#!/usr/bin/env python3

"""
This fastqsplitter module provides a program to split fastq files. It
implements two algorithms to do so, one round-robin and one sequential
algorith.
"""

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
import os
from typing import List, Optional

# xopen opens files as normal files, gzip files, bzip2 files or xz files
# depending on extension.
import xopen

# Choose 1 as default compression level. Speed is more important than filesize
# in this application.
DEFAULT_COMPRESSION_LEVEL = 1
# 64K seems a good default. See docs/benchmark_results.txt.
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
DEFAULT_SUFFIX = ".fastq.gz"
STDIN = "/dev/stdin" if os.name == "posix" else None
SIZE_SUFFIXES = {"K": 1024 ** 1, "M": 1024 ** 2, "G": 1024 ** 3}


def argument_parser() -> argparse.ArgumentParser:
    """Argument parser for the fastqsplitter application"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, default=STDIN, nargs="?",
                        help="The fastq file to be scattered.")
    parser.add_argument("-p", "--prefix", type=str,
                        help="The prefix for the output files.")
    parser.add_argument("-s", "--suffix", type=str, default=DEFAULT_SUFFIX,
                        help="The default suffix for the output files. The "
                             "extension determines which compression is used. "
                             "'.gz' for gzip, '.bz2' for bzip2, '.xz' for xz. "
                             "Other extensions will use no compression.")
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("-n", "--number", type=int,
                              help="Specify the number of output files which "
                                   "to split over. Fastq records will be "
                                   "distributed using a round-robin method.")
    output_group.add_argument(
        "-o", "--output", action="append", type=str,
        help="Scatter over these output files. Multiple -o flags can be used. "
             "The extensions determine which compression algorithm will be "
             "used. '.gz' for gzip, '.bz2' for bzip2, '.xz' for xz. Other "
             "extensions will use no compression. Fastq records will be "
             "distributed using a round-robin method.")
    output_group.add_argument(
        "-m", "--max-size", type=str,
        help="In round robin mode, determines the number of output files by "
             "dividing the input size "
             "by max size and distribute the fastq records in a round robin "
             "fashion over these files. WARNING: if compression differs "
             "between input and output files, this will not work properly. "
             "In sequential mode this is the maximum number of bytes written "
             "to each output file. NOTE: This is the size *before* "
             "compression (if applied). As a rule of thumb multiply by 0.38 "
             "to get the actual filesize when using gzip compression.")

    # What is a good one-letter symbol for --no-round-robin?
    parser.add_argument("-k", "--no-round-robin", action="store_false",
                        dest="round_robin",
                        help="Do not use round-robin but create output files "
                             "sequentially instead. Default when using "
                             "stdin. Max size should be set.")
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
    parser.add_argument("-P", "--print", action="store_true",
                        help="Print output files to stdout for easier usage "
                             "in scripts.")

    # BELOW ARGUMENTS ARE FOR BENCHMARKING AND TESTING PURPOSES
    parser.add_argument("-b", "--buffer-size", type=str,
                        default=str(DEFAULT_BUFFER_SIZE),
                        help=argparse.SUPPRESS)
    return parser


def human_readable_to_int(number_string: str) -> int:
    """
    Convert a string such as '64K' or '128M' to an integer.
    64K == 64 * 1024. Integers without suffix are converted as is.
    """
    for suffix, multiplier in SIZE_SUFFIXES.items():
        if number_string.endswith(suffix):
            return int(number_string.strip(suffix)) * multiplier
    return int(number_string)


def _read_until_new_fastq_record(input_handle: io.BufferedReader) -> bytes:
    """
    Reads the input handle until the start of a fastq record or has
    reached the EOF. This ensures the input handle is at the position of a new
    record. Returns the bytes read until the position.
    :param input_handle: an io.BufferedReader or similar object.
    :return: All bytes that have been read up to the start of the new fastq
    record
    """
    missing_record_lines = []  # type: List[bytes]
    while True:
        line = input_handle.readline()
        if line == b"":  # EOF
            return b"".join(missing_record_lines)
        missing_record_lines.append(line)
        # Both @ and + can occur in the quality line while they also indicate
        # the start of the record and the middle respectively.
        # Checks below ensure at least one complete record is returned.
        if line.startswith(b"@"):
            sequence_line = input_handle.readline()
            missing_record_lines.append(sequence_line)
            if sequence_line.strip().isalpha():  # Valid sequence line
                plus_line = input_handle.readline()
                missing_record_lines.append(plus_line)
                if plus_line.startswith(b"+"):
                    quality_line = input_handle.readline()
                    missing_record_lines.append(quality_line)
                    lengths_match = len(quality_line) == len(sequence_line)
                    # Peek returns a variable number of characters (but at
                    # least 1 in the case below). So we check with startswith.
                    new_record_start = input_handle.peek(1).startswith(b"@")
                    if lengths_match and new_record_start:
                        return b"".join(missing_record_lines)


def split_fastqs_round_robin(
        input_file: str, output_files: List[str],
        compression_level: int = DEFAULT_COMPRESSION_LEVEL,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        threads_per_file: int = DEFAULT_THREADS_PER_FILE) -> None:
    """
    Split a fastq file over multiple output files in a round robin fashion.
    :param input_file: The file to be split.
    :param output_files: The files receiving the split parts
    :param compression_level: Which compression level to use if applicable
    :param buffer_size: The buffer size. The granularity at which fastq records
    are distributed.
    :param threads_per_file: How many threads xopen should use to open the
    file.
    """
    if len(output_files) < 1:
        raise ValueError("The number of output files should be at least 1.")
    if buffer_size < 1024:
        # This value is arbitrary, but really low values such as 5 or 30 don't
        # make sense.
        raise ValueError("The buffer size should be at least 1024.")

    # contextlib.Exitstack allows us to open multiple files at once which
    # are automatically closed on error.
    # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
    with contextlib.ExitStack() as stack:
        input_handle = stack.enter_context(xopen.xopen(input_file, mode='rb'))
        output_handles = [stack.enter_context(xopen.xopen(
                filename=output_file,
                mode='wb',
                compresslevel=compression_level,
                threads=threads_per_file
            )) for output_file in output_files
        ]  # type: List[io.BufferedWriter]

        group_number = 0
        number_of_output_files = len(output_files)

        while True:
            read_buffer = input_handle.read(buffer_size)
            if read_buffer == b"":
                return

            # Read the input until the start of a new record.
            completed_record = _read_until_new_fastq_record(input_handle)
            output_handles[group_number].write(read_buffer + completed_record)
            # Set the group number for the next group to be written.
            group_number += 1
            # cycle back to the start when we have written the last file.
            if group_number == number_of_output_files:
                group_number = 0


def _sequential_splitter(input_handle: io.BufferedReader,
                         output_handle: io.BufferedReader,
                         max_size: int,
                         buffer_size: int = DEFAULT_BUFFER_SIZE) -> int:
    """
    Reads max_size bytes from an input_handle and writes it to output_handle
    reading buffer_size bytes at the time. Ensures a complete fastq record
    is at the end of each file.
    :return: The number of bytes written.
    """
    target_size = max_size - buffer_size
    total_size = 0
    while True:
        read_buffer = input_handle.read(buffer_size)
        if read_buffer == b"":
            return total_size
        output_handle.write(read_buffer)
        total_size += buffer_size
        if total_size >= target_size:
            # Complete the record
            completed_record = _read_until_new_fastq_record(input_handle)
            output_handle.write(completed_record)
            return total_size + len(completed_record)


def split_fastqs_sequentially(
        input_file: str,
        max_size: int,
        prefix: str = "split.",
        suffix: str = DEFAULT_SUFFIX,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        compression_level: int = DEFAULT_COMPRESSION_LEVEL,
        threads_per_file: int = DEFAULT_THREADS_PER_FILE):
    if max_size < buffer_size:
        raise ValueError("Maximum size {0} should be larger than buffer size "
                         "{1}.".format(max_size, buffer_size))

    with xopen.xopen(input_file, mode="rb") as input_fastq:
        group_number = 0
        written_files: List[str] = []
        while True:
            if input_fastq.peek(0) == b"":  # Quit if there are no bytes left
                return written_files
            filename = prefix + str(group_number) + suffix
            group_number += 1  # Increase group_number for the next file
            with xopen.xopen(filename, mode="wb",
                             compresslevel=compression_level,
                             threads=threads_per_file) as output_fastq:
                _sequential_splitter(input_fastq, output_fastq,
                                     max_size,
                                     buffer_size=buffer_size)
                written_files.append(filename)


def fastqsplitter(input: str,
                  output: Optional[List[str]] = None,
                  number: Optional[int] = None,
                  max_size: Optional[int] = None,
                  prefix: Optional[str] = None,
                  suffix: str = DEFAULT_SUFFIX,
                  buffer_size: int = DEFAULT_BUFFER_SIZE,
                  compression_level: int = DEFAULT_COMPRESSION_LEVEL,
                  threads_per_file: int = DEFAULT_THREADS_PER_FILE,
                  round_robin: bool = True) -> List[str]:
    """
    Splits fastq files sequentially or round_robin depending on the given
    parameters. Creates files of the from <prefix><number><suffix>.
    :param input: The input fastq file.
    :param output: An optional list of output files if filenames should be
    determined before hand.
    :param number: Optional number of output files.
    :param max_size: Try to determine the number of output files by the size
    of the input file and the maximum size. Or if round_robin = false this is
    the maximum amount of bytes written.
    :param prefix: The prefix for the output files.
    :param suffix: The suffix for the output files. ".gz" files are gzip
    compressed, ".xz" xz compressed and ".bzip2" bzip2 compressed.
    :param buffer_size: The granularity with which the fastq files should be
    distributed.
    :param compression_level: The compression level to use, if applicable.
    :param threads_per_file: The amount of threads xopen should use to open
    the file.
    :param round_robin: If set to false will force the sequential method if
    a file is given.
    :return: The list of output files written.
    """
    default_prefix = os.path.basename(
        input).rstrip(".gz").rstrip(".fastq").rstrip(".fq") + "."
    prefix = prefix if prefix is not None else default_prefix

    if not round_robin or (input == STDIN and max_size is not None):
        if max_size is None:
            raise ValueError("Maximum size must be set when splitting files "
                             "sequentially (not using round-robin).")
        return split_fastqs_sequentially(
            input_file=input,
            max_size=max_size,
            prefix=prefix,
            suffix=suffix,
            buffer_size=buffer_size,
            compression_level=compression_level,
            threads_per_file=threads_per_file)

    if output:
        output_files = output
    else:
        if max_size is not None:
            input_size = os.stat(input).st_size
            if input_size == 0:
                raise OSError("Cannot determine size of input file or "
                              "empty input file: {0}.".format(input))
            number = input_size // max_size + 1
        elif not number:
            raise ValueError("Either a maximum size or a number of files or "
                             "a list of output files must be defined.")
        output_files = [prefix + str(i) + suffix for i in range(number)]

    split_fastqs_round_robin(input, output_files,
                             compression_level=compression_level,
                             threads_per_file=threads_per_file,
                             buffer_size=buffer_size)
    return output_files


def main():
    """Fastqsplitter program"""
    parser = argument_parser()
    # convert argparse.Namespace to dictionary
    kwargs = vars(parser.parse_args())
    max_size = kwargs.pop("max_size")
    if max_size is not None:
        max_size = human_readable_to_int(max_size)
    buffer_size = human_readable_to_int(kwargs.pop("buffer_size"))
    print_to_stdout = kwargs.pop("print")
    # kwargs correspond to fastqsplitter function inputs.
    output_files = fastqsplitter(max_size=max_size,
                                 buffer_size=buffer_size,
                                 **kwargs)
    if print_to_stdout:
        print("\n".join(output_files))


if __name__ == "__main__":  # pragma: no cover
    main()
