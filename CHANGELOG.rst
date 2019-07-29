==========
Changelog
==========

.. Newest changes should be on top.

.. NOTE: This document is user facing. Please word the changes in such a way
.. that users understand how the changes affect the new version.

1.1.0-dev
-----------------
+ Cythonize the splitting algorithm. This reduces the overhead of the application
  up to 30% over the fastest native python implementation.
  This means splitting of uncompressed fastqs will be noticably faster
  (30% faster was achieved during testing). However when splitting compressed
  fastq files into compressed split fastq files this change will not be noticable.
  (I.e. 7 vs 10  second overhead when decompression/compression takes 40 seconds
  -> difference of 47 seconds vs 50 seconds).

1.0.0
-------------
+ Added documentation for fastqsplitter and set up readthedocs page.
+ Added tests for fastqsplitter.
+ Upstream contributions to xopen have improved fastqsplitter speed.
+ Initiated fastqsplitter.