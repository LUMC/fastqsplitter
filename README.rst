.. Badges have empty alts. So nothing shows up if they do not work.

.. image:: https://img.shields.io/pypi/v/fastqsplitter.svg
  :target: https://pypi.org/project/fastqsplitter/
  :alt:

.. image:: https://img.shields.io/conda/v/bioconda/fastqsplitter.svg
  :target: https://anaconda.org/bioconda/fastqsplitter
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

Fastqsplitter reads a fastq
file. It then splits the reads over the designated output files.

This application does NOT work with multiline fastq sequences.

Quickstart
----------

install fastqsplitter:
``pip install fastqsplitter``

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