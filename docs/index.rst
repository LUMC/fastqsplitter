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

The algorithm is a reimplementation from `biopet-fastqsplitter
<https://github.com/biopet/fastqsplitter>`_. Fastqsplitter reads a fastq
file. It then splits the reads over the designated output files.

This application does NOT work with multiline fastq sequences.

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

   Fastqsplitter uses a separate process for reading the input file, doing the
   splitting as well as one seperate process per output file. Fastqsplitter
   therefore always uses multiple CPU cores.

=======
Example
=======
With an input file ``input_fastq.gz`` of 2.3 GB.
``fastqsplitter -i input_fastq.gz -o split.1.fq.gz -o split.2.fq.gz -o split.3.fq.gz``

Fastqsplitter will read ``input_fastq.gz``. The first 100 reads will go
to ``split.1.fq.gz``, read 101-200 will go to ``split.2.fq.gz``, read
201-300 will go to ``split.3.fq.gz``, read 301-400 will go to ``split.1.fq.gz``,
etc.

This way the fastq reads are evenly distributed, with a difference of maximum
100 reads between output files, and no positional bias in each output file.


=======================
Performance comparisons
=======================

Comparing different modes of fastqsplitter and biopet-fastqsplitter.
Biopet-fastqsplitter has only one mode: compression level 5, and an unknown number
of threads per file.

Fastqsplitter runs with 1 thread per output file and compression level 1 by default.
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

======================== ========================== ========================= =======================
measurement              fastqsplitter (defaults)   fastqsplitter -t 4 -c 5    biopet-fastqsplitter
======================== ========================== ========================= =======================
real time                 44.423s                    77.778s                   102.300s
user time                 159.089s                   459.051s                  509.594s
sys time                  9.437s                     11.078s                   8.411s
max mem                   24 MB                      42 MB                     665 MB
max vmem                  207 MB                     2.0 GB                    11.0 GB
output files total size   2290 MB                    2025 MB                   2025 MB               
======================== ========================== ========================= =======================


The outcomes for the runs were fairly consistent with a +-3 second real time (wall clock) difference between runs.

.. include:: CHANGELOG.rst