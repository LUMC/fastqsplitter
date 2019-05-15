#!/usr/bin/env python3

import argparse
import contextlib
import gzip

from pathlib import Path
from typing import Iterable, List


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", action="append", type=Path,
                        required=True)
    return parser


def split_fastqs(input_file: Path, output_files: List[Path]):

    # Open all the files at once
    # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
    with contextlib.ExitStack() as stack:
        input_fastq = stack.enter_context(
            gzip.open(str(input_file), mode='rb'))  # type: gzip.GzipFile
        output_handles = [
            stack.enter_context(gzip.open(str(output_file), mode='wb'))
            for output_file in output_files]  # type: List[gzip.GzipFile]

        i = 0
        number_of_output_files = len(output_handles)
        fastq_empty = False
        while not fastq_empty:
            # By using modulo we basically pick one file at a time.
            file_to_write = output_handles[i % number_of_output_files]
            for j in range(100 * 4):
                try:
                    file_to_write.write(next(input_fastq))
                except StopIteration:
                    fastq_empty = True
                    break
            i += 1


def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()
    split_fastqs(parsed_args.input, parsed_args.output)


if __name__ == "__main__":
    main()
