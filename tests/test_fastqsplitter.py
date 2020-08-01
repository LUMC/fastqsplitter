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

import sys
import tempfile
from pathlib import Path

from Bio.SeqIO.QualityIO import FastqPhredIterator

from fastqsplitter import main, split_fastqs

import pytest

import xopen

TEST_FILE = Path(__file__).parent / Path("data") / Path("test.fq.gz")
TEST_FILE_INVALID = Path(__file__).parent / Path("data") / Path(
    "test_invalid.fq.gz")


def validate_fastq_gz(fastq: Path) -> int:
    """This function uses the biopython parser to validate a fastq file
    and outputs the number of fastqrecords."""

    number_of_records = 0
    with xopen.xopen(str(fastq), 'rt') as fastq_handle:
        fastq_iterator = FastqPhredIterator(fastq_handle)
        for _ in fastq_iterator:
            number_of_records += 1
    return number_of_records


# This also makes sure we have a valid test file.
RECORDS_IN_TEST_FILE = validate_fastq_gz(TEST_FILE)


def test_invalid_test_file():
    with pytest.raises(ValueError) as error:
        validate_fastq_gz(TEST_FILE_INVALID)
    error.match("Lengths of sequence and quality values differs")


@pytest.mark.parametrize("number_of_splits", list(range(1, 6)))
def test_split_fastqs_perblock(number_of_splits: int):
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq")[1]))
                    for _ in range(number_of_splits)]
    # Use a small buffer size for testing a small file.
    split_fastqs(TEST_FILE, output_files, buffer_size=1024)

    with xopen.xopen(TEST_FILE, "rb") as test_h:
        test_filesize = len(test_h.read())

    expected_file_size = test_filesize // number_of_splits

    for output_file in output_files:
        actual_size = output_file.stat().st_size
        percentage_size = actual_size / expected_file_size
        print(output_file.name, actual_size)
        assert percentage_size >= 0.98
        assert percentage_size <= 1.02
    total_lines = sum(validate_fastq_gz(output_file)
                      for output_file in output_files)
    assert total_lines == RECORDS_IN_TEST_FILE


def test_main():
    number_of_splits = 3
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq.gz")[1]))
                    for _ in range(number_of_splits)]
    args = ["fastqsplitter", "-i", str(TEST_FILE), "-c", "5", "-t", "2"]
    for output_file in output_files:
        args.append("-o")
        args.append(str(output_file))
    sys.argv = args[:]
    main()
    [validate_fastq_gz(output_file) for output_file in output_files]
