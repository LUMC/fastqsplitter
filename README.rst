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

Quickstart
----------

install fastqsplitter:
``pip install fastqsplitter``

Or with conda and an activated bioconda channel:
``conda install fastqsplitter``

The conda install is recommended because it will install dependencies which
make decompression and compression faster for `.gz` files.

To split an input file ``input_fastq.gz`` into 3 different files.
``fastqsplitter input.fastq.gz -n 3 --prefix split.`` 
This will create ``split.0.fastq.gz``, ``split.1.fastq.gz`` and ``split.2.fastq.gz``.

fastqsplitter uses the excellent `xopen library by @marcelm
<https://github.com/marcelm/xopen>`_. Therefore, the input and output files
compression is determined by the extension. Use ``.gz`` if output files should
be gzip compressed. 

Documentation
-------------

More information on fastqsplitter can be found `on our readthedocs page
<https://fastqsplitter.readthedocs.io/>`_.
