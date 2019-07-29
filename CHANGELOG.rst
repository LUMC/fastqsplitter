==========
Changelog
==========

.. Newest changes should be on top.

.. NOTE: This document is user facing. Please word the changes in such a way
.. that users understand how the changes affect the new version.

1.1.0-dev
-----------------
+ Cythonize the splitting algorithm. This reduces the overhead of the application
  up to 50% over the fastest native python implementation. Overhead is all the
  allocated cpu time that is not system time.

  This means splitting of uncompressed fastqs will be noticably faster
  (30% faster was achieved during testing). When splitting compressed
  fastq files into compressed split fastq files this change will not be much faster
  since all the gzip process will be run in a separate thread. Still when splitting
  a 2.3 gb gzipped fastq file into 3 gzipped split fastq files the speedup from
  the fastest python implementation was 14% in total cpu seconds. (Due to the
  multithreaded nature of the application wall clock time was reduced by only 3%).

1.0.0
-------------
+ Added documentation for fastqsplitter and set up readthedocs page.
+ Added tests for fastqsplitter.
+ Upstream contributions to xopen have improved fastqsplitter speed.
+ Initiated fastqsplitter.