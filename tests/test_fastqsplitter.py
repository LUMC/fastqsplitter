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

import gzip
import tempfile
from pathlib import Path

from Bio.SeqIO.QualityIO import FastqPhredIterator

from fastqsplitter import split_fastqs

import pytest


TEST_FILE = Path(__file__).parent / Path("data") / Path("test.fq.gz")
TEST_FILE_INVALID = Path(__file__).parent / Path("data") / Path(
    "test_invalid.fq.gz")


def validate_fastq_gz(fastq: Path):
    """Biopython parses fastq files and returns qualities."""
    with gzip.open(fastq, 'rt') as fastq_handle:
        fastq_iterator = FastqPhredIterator(fastq_handle)
        while True:
            try:
                # Parse each record.
                _ = next(fastq_iterator)
            except StopIteration:
                break


# Some sanity checking for the test function
def test_test_file():
    validate_fastq_gz(TEST_FILE)


def test_invalid_test_file():
    with pytest.raises(ValueError) as error:
        validate_fastq_gz(TEST_FILE_INVALID)
    error.match("Lengths of sequence and quality values differs")


@pytest.mark.parametrize("number_of_splits", range(1, 6))
def test_split_fastqs(number_of_splits: int):
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq.gz")[1]))
                    for _ in range(number_of_splits)]
    print(output_files)

    split_fastqs(TEST_FILE, output_files)
    for output_file in output_files:
        validate_fastq_gz(output_file)
