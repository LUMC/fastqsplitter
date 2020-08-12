.. Checkout the Readthedocs theme for an example structure
.. https://github.com/rtfd/sphinx_rtd_theme/tree/master/docs/demo

=============
fastqsplitter
=============
.. All the documentation will be in one page for now. With navigation on the
.. side to allow quickly going to the section you want. The documentation is
.. not yet big enough to be benefited by a nested structure.

.. contents:: Table of contents

=============
Introduction
=============
A simple application to split FASTQ files.

Fastqsplitter splits a fastq file over the specified output files evenly.
It is similar to the `GNU Coreutils split
<https://manpages.debian.org/buster/coreutils/split.1.en.html>`_ program,
except that it is aware of the FASTQ four lines per record format. (Split
works with one line per record.) It has support for compressed FASTQ files
and can compress splitted FASTQ files on the fly.

Fastqsplitter uses a round-robin method to distribute the FASTQ records evenly
across the output files. Alternatively it can distribute files sequentially,
which is useful for reading from STDIN and the input size is unknown.
Fastqsplitter can split such input in N files with a given maximum size.

This application does not work with multiline fastq sequences.

Fastqsplitter is fast because it only checks if the last record written to a
file is a valid FASTQ record before starting to write to a new file. It
assumes all records before that were valid.
Since all downstream analysis tools (FastQC, cutadapt, BWA etc.) do check
if the input is correct, extensive input checking in fastqsplitter was deemed
redundant.

fastqsplitter uses the excellent `xopen library by @marcelm
<https://github.com/marcelm/xopen>`_. This determines by extension whether the
file is compressed and allows for very fast compression and decompression of
gzip files.


=============
Usage
=============

.. argparse::
    :module: fastqsplitter
    :func: argument_parser
    :prog: fastqsplitter


.. NOTE::

   Fastqsplitter uses a separate process for reading the input file if it is
   compressed, doing the
   splitting as well as one seperate process per compressed output file.
   Fastqsplitter therefore always uses multiple CPU cores when working with
   compressed files.

=======
Example
=======

Round-robin
-----------
With an input file ``input_fastq.gz`` of 2.3 GB.
``fastqsplitter -i input_fastq.gz -n 3 -p split. -o .fq.qz``
This will create ``split.0.fq.gz``, ``split.1.fq.gz`` and ``split.2.fq.gz``.

Fastqsplitter will read ``input_fastq.gz``. The first block of records will go
to ``split.0.fq.gz``, the next block will go to ``split.1.fq.gz``, etc.

This way the fastq reads are evenly distributed, with no positional bias in
each output file.

Sequential
----------
``my_fastq_generating_program | fastqsplitter --max-size 10G -p my_fastq.
-s .fastq.gz``

This will read from STDIN and write files that contain maximum 10GiB bytes.
Note that a ``.gz`` suffix is used. The 10GiB bytes will be compressed and the
output sizes will be smaller than 10 GiB. An unknown number of files will
be generated.

Sequential mode can be forced with ``-S`` or ``--sequential`` flags.

=======================
Performance comparisons
=======================

Following benchmarks were performed with a 5 million record FASTQ file (1.6
GiB) on a system with a Ryzen 5 3600 (6 core 12 threads) cpu with 32GB of
ddr4-3200 ram.

The files were stored and written on a ramdisk created with
``mount -t tmpfs -o size=12G myramdisk ramdisk``. This way IO was bottlenecked
by memory bus speed instead of disk speed.

Benchmarks were performed using `hyperfine
<https://github.com/sharkdp/hyperfine>`_.

Uncompressed
-------------
While uncompressed files are not used often in BioInformatics, they give a
good impression of the speed of an algorithm by eliminating all the
compression overhead. All benchmarks below split the 1.6 GB file in 3 files.

Fastqsplitter round-robin mode

.. code-block::

    $ hyperfine -w 1 -r 10 "fastqsplitter big2.fastq -s .fastq -p test -n 3"
    Benchmark #1: fastqsplitter big2.fastq -s .fastq -p test -n 3 -b 64K
      Time (mean ± σ):     686.7 ms ±   8.9 ms    [User: 174.9 ms, System: 508.5 ms]
      Range (min … max):   671.0 ms … 699.2 ms    10 runs

Fastqsplitter sequential mode

.. code-block::

    $ hyperfine -w 1 -r 10 "fastqsplitter big2.fastq -s .fastq -p test -m 600M -S"
    Benchmark #1: fastqsplitter big2.fastq -s .fastq -p test -m 600M -S -b 64K
      Time (mean ± σ):     559.9 ms ±   5.7 ms    [User: 57.7 ms, System: 499.4 ms]
      Range (min … max):   550.7 ms … 570.2 ms    10 runs

GNU Coreutils split can also do sequential mode and give correct FASTQ records
when a line number is chosen that is divisable by 4. The line number 7512140
gives also a 600M result file. So results are comparable.

.. code-block::

    $ hyperfine -w 1 -r 10 'split -l 7512140 big2.fastq'
    Benchmark #1: split -l 7512140 big2.fastq
      Time (mean ± σ):     615.9 ms ±   6.9 ms    [User: 116.9 ms, System: 497.8 ms]
      Range (min … max):   607.8 ms … 630.5 ms    10 runs

Note that system times are within 10ms of each other. This signifies the time
needed to write the files to the tmps and to read the input. User time is
probably closer to the time spent in the algorithm.

The score is as follows:
+ Fastqsplitter round-robin: 174.9 ms user time.
+ Fastqsplitter sequential: 57.7 ms user time.
+ Gnu Coreutils split: 116.9 ms user time.

Comparing different modes of fastqsplitter and biopet-fastqsplitter.
Biopet-fastqsplitter has only one mode: compression level 5, and an unknown number
of threads per file.

Fastqsplitter runs with 1 thread per output file and compression level 1 by default.
A comparison between default cython mode and python mode is in the table.
For fair comparison with biopet-fastqsplitter, fastqsplitter was run with 4
threads per file (xopen default) and compression level 5. Since fastqsplitter
starts several pigz and one gzip process the memory usage of these processes
are included in the results.

This test case was run with  a 2.3 GB input fastq file zipped.
This was split over 5 output files.

The used test machine had 32 GB memory (2x16GB 2133mhz), an Intel core i7-6700
(4 cores, 8 threads) and a Sandisk X400 500gb SSD. Operating system: Debian 10.

The following table shows the average over 10 runs.

+ real time = wall clock time
+ user time = total cpu seconds spent by the application (useful to see the resource usage of multithreading)
+ sys time = total cpu seconds spent by the kernel (for IO and other sys calls)

======================== ========================== ========================== ========================= =======================
measurement              fastqsplitter (defaults)   fastqsplitter (python)     fastqsplitter -t 4 -c 5    biopet-fastqsplitter
======================== ========================== ========================== ========================= =======================
real time                 44.787s                    45.702s                   77.778s                   102.300s
user time                 162.272s                   169.238s                  459.051s                  509.594s
sys time                  9.825s                     9.825s                    11.078s                   8.411s
max mem                   24 MB                      24 MB                     42 MB                     665 MB
max vmem                  207 MB                     207 MB                    2.0 GB                    11.0 GB
output files total size   2290 MB                    2290 MB                   2025 MB                   2025 MB
======================== ========================== ========================== ========================= =======================

The outcomes for the runs were fairly consistent with a +-3 second real time (wall clock) difference between runs.

Uncompressed
-------------

When splitting a 6.3 Gb uncompressed fastq file into 3 files which are written
to /dev/null to eliminate I/O limitations the cython algorithm generates less
overhead than the python algorithm.

However in most cases files will be split from compressed to compressed files
making the difference much smaller (see table above.)

======================== ========================== ==========================
measurement              fastqsplitter (cython)     fastqsplitter (python)
======================== ========================== ==========================
real time                 6.045s                    10.345s
user time                 4.907s                    9.200s
sys time                  1.137s                    1.145s
======================== ========================== ==========================

.. include:: CHANGELOG.rst