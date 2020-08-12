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

from fastqsplitter import human_readable_to_int, main, \
    split_fastqs_round_robin, split_fastqs_sequentially

import pytest

import xopen

TEST_FILE = Path(__file__).parent / "data" / "test.fq.gz"
TEST_FILE_INVALID = Path(__file__).parent / "data" / "test_invalid.fq.gz"


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
with xopen.xopen(TEST_FILE, "rb") as fastq_handle:
    BYTES_IN_TEST_FILE = len(fastq_handle.read())


def test_invalid_test_file():
    # We need to make sure our test function indeed fails when a fastq file is
    # invalid.
    with pytest.raises(ValueError) as error:
        validate_fastq_gz(TEST_FILE_INVALID)
    error.match("Lengths of sequence and quality values differs")


@pytest.mark.parametrize(["input", "expected"],
                         [("1252", 1252),
                          ("64K", 64*1024),
                          ("64M", 64*1024*1024),
                          ("64G", 64*1024*1024*1024)]
                         )
def test_human_readable_to_int(input: str, expected: int):
    assert human_readable_to_int(input) == expected


def test_split_fastq_buffer_size_to_low():
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq")[1]))
                    for _ in range(3)]
    with pytest.raises(ValueError) as error:
        split_fastqs_round_robin(TEST_FILE, output_files, buffer_size=512)
    error.match("at least 1024")


def test_split_fastq_no_output_files():
    with pytest.raises(ValueError) as error:
        split_fastqs_round_robin(TEST_FILE, [], buffer_size=512)
    error.match("at least 1")


@pytest.mark.parametrize("number_of_splits", list(range(1, 6)))
def test_split_fastqs_perblock(number_of_splits: int):
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq")[1]))
                    for _ in range(number_of_splits)]
    # Use a small buffer size for testing a small file.
    split_fastqs_round_robin(TEST_FILE, output_files, buffer_size=1024)

    expected_number_of_records = RECORDS_IN_TEST_FILE // number_of_splits

    total_records = 0
    for output_file in output_files:
        actual_records = validate_fastq_gz(output_file)
        total_records += actual_records
        # Check if distribution is even across output files.
        percentage_size = actual_records / expected_number_of_records
        assert percentage_size >= 0.98
        assert percentage_size <= 1.02
    assert total_records == RECORDS_IN_TEST_FILE


@pytest.mark.parametrize("max_size", [16*1024, 32*1024, 64*1024, 128*1024])
def test_fastq_split_on_size(max_size: int):
    prefix = tempfile.mktemp()
    buffer_size = 1024
    expected_length = BYTES_IN_TEST_FILE // (max_size - buffer_size) + 1
    split_files = split_fastqs_sequentially(TEST_FILE,
                                            max_size=max_size,
                                            prefix=prefix,
                                            suffix=".fastq",
                                            buffer_size=buffer_size)
    assert len(split_files) == expected_length
    for file in split_files:
        validate_fastq_gz(file)
        assert Path(file).stat().st_size <= max_size
        Path(file).unlink()  # cleanup


def test_main():
    number_of_splits = 3
    output_files = [Path(str(tempfile.mkstemp(suffix=".fq.gz")[1]))
                    for _ in range(number_of_splits)]
    args = ["fastqsplitter", str(TEST_FILE), "-c", "5", "-t", "2"]
    for output_file in output_files:
        args.append("-o")
        args.append(str(output_file))
    sys.argv = args[:]
    main()
    [validate_fastq_gz(output_file) for output_file in output_files]
