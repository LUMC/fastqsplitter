#!/usr/bin/env python3

import argparse
import contextlib
import gzip

from pathlib import Path
from typing import List

DEFAULT_COMPRESSION_LEVEL = 6


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", action="append", type=Path,
                        required=True)
    parser.add_argument("-c", "--compression-level", type=int,
                        default=DEFAULT_COMPRESSION_LEVEL)
    return parser


def split_fastqs(input_file: Path, output_files: List[Path],
                 compression_level: int = DEFAULT_COMPRESSION_LEVEL,
                 group_size: int = 100):
    # Open all the files at once
    # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
    with contextlib.ExitStack() as stack:
        input_fastq = stack.enter_context(
            gzip.open(str(input_file), mode='rb'))  # type: gzip.GzipFile
        output_handles = []  # type: List[gzip.GzipFile]
        for output_file in output_files:
            output_handles.append(
                # Make sure each file is opend as part of the stack. So all
                # files get closed on error.
                stack.enter_context(
                    gzip.open(
                        filename=str(output_file),
                        mode='wb',
                        compresslevel=compression_level
                    )
                ))

        i = 0
        number_of_output_files = len(output_handles)
        fastq_empty = False
        while not fastq_empty:
            # By using modulo we pick one file at a time and make sure all
            # files are written to equally.
            file_to_write = output_handles[i % number_of_output_files]

            # Make sure a multiple of 4 lines is written as each record is
            # 4 lines.
            for j in range(group_size * 4):
                try:
                    file_to_write.write(next(input_fastq))
                except StopIteration:
                    fastq_empty = True
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
