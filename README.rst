.. Badges have empty alts. So nothing shows up if they do not work.

.. image:: https://img.shields.io/pypi/v/fastqsplitter.svg
  :target: https://pypi.org/project/fastqsplitter/
  :alt:

.. image:: https://img.shields.io/conda/v/bioconda/fastqsplitter.svg
  :target: http://bioconda.github.io/recipes/fastqsplitter/README.html
  :alt:

.. image:: https://img.shields.io/pypi/pyversions/fastqsplitter.svg
  :target: https://pypi.org/project/fastqsplitter/
  :alt:

.. image:: https://img.shields.io/pypi/l/fastqsplitter.svg
  :target: https://github.com/LUMC/fastqsplitter/blob/master/LICENSE
  :alt:

.. image:: https://travis-ci.org/LUMC/fastqsplitter.svg?branch=develop
  :target: https://travis-ci.org/LUMC/fastqsplitter
  :alt:

.. image:: https://codecov.io/gh/LUMC/fastqsplitter/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/LUMC/fastqsplitter
  :alt:

fastqsplitter
=============

A simple application to split FASTQ files.

Fastqsplitter splits a fastq file over the specified output files evenly.
Fastqsplitter will read groups of a 100 fastq files.
For example if 3 output files are specified record 1-100 will go to file 1,
101-200 to file 2, 201-300 to file 3 , 301-400 to file 1 again etc.
This ensures the output fastq files are of equal size with no positional bias
in the output files.

Fastqsplitter is fast because it assumes each record is 4 lines. As a
consequence this application does NOT work with multiline fastq sequences.
Also input fastq records are NOT checked for being proper fastq records.
Since all downstream analysis tools (FastQC, cutadapt, BWA etc.) do check
if the input is correct, another input check in fastqsplitter was deemed
redundant.

Quickstart
----------

install fastqsplitter:
``pip install fastqsplitter``

If installation does not work because no C compiler is installed on your system
try: ``NO_CYTHON=True pip install fastqsplitter``

To split an input file ``input_fastq.gz`` into 3 different files.
``fastqsplitter -i input_fastq.gz
-o split.1.fq.gz -o split.2.fq.gz -o split.3.fq.gz``

fastqsplitter uses the excellent `xopen library by @marcelm
<https://github.com/marcelm/xopen>`_. Therefore, the input and output files
compression is determined by the extension. Use ``.gz`` if output files should
be gzip compressed. 

Documentation
-------------

More information on fastqsplitter can be found `on our readthedocs page
<https://fastqsplitter.readthedocs.io/>`_.
