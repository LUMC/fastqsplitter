#!/usr/bin/env python3

import argparse
import contextlib
import gzip

from collections import namedtuple
from pathlib import Path
from typing import Optional, Iterable, List, Any
from functools import reduce


class SimpleFastqParser(object):
    """
    An iterator returning SimpleFastqRecord objects

    :arg handle: Any iterator returning lines of strings, preferable an open file handle
    :return SimpleFastqRecord objects
    """

    def __init__(self, handle):
        self.__handle = handle
        self.__bucket = [None, None, None, None]

    def __iter__(self):
        return self

    def __next__(self):
        i = 0
        while i < 4:
            line = next(self.__handle)
            self.__bucket[i] = line
            i += 1
        read = self.__bucket[:]
        self.__bucket = [None, None, None, None]
        return read

    def next(self):  # python 2 compatibility
        return self.__next__()

    def close(self):
        self.__handle.close()


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", nargs="+", type=Path, required=True)
    return parser


def fastq_reader(fastq_file: Path) -> Iterable:
    with gzip.open(fastq_file, mode='rt') as fastq_handle:
        fastq_parser = SimpleFastqParser(fastq_handle)
    return fastq_parser


def split_fastqs(input_file: Path, output_files: List[Path]):
    with gzip.open(str(input_file), mode='rt') as input_fastq:
        fastq_parser = SimpleFastqParser(input_fastq)
    with contextlib.ExitStack as stack:
        # Open all the files at once
        # https://stackoverflow.com/questions/19412376/open-a-list-of-files-using-with-as-context-manager
        output_handles = [
            stack.enter_context(gzip.open(str(output_file), mode='wb'))
            for output_file in output_files]  # type: List[gzip.GzipFile]

    i = 0
    number_of_output_files = len(output_handles)
    while True:
        # By using modulo we basically pick one file at a time.
        file_to_write = output_handles[i % number_of_output_files]
        for j in range(100):
            try:
                file_to_write.write(fastq_parser.next())
            except StopIteration:
                break
        i += 1


def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()
    print(parsed_args.output)


if __name__ == "__main__":
    main()
