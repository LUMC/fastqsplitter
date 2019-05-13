#!/usr/bin/env python3

import argparse
import contextlib
import gzip

from collections import namedtuple
from pathlib import Path
from typing import Optional, Iterable
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
    with gzip.open(fastq_file, mode ='rt') as fastq_handle:
        fastq_parser = SimpleFastqParser(fastq_handle)
    return fastq_parser


def split_fastqs(input_file: Path, output_files: List[Path]):
    with gzip.open(str(input_file), mode='rt') as input_fastq:
        fastq_parser = SimpleFastqParser(input_fastq)




def main():
    parser = argument_parser()
    parsed_args = parser.parse_args()
    print(parsed_args.output)


if __name__ == "__main__":
    main()