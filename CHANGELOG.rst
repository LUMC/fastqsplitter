==========
Changelog
==========

.. Newest changes should be on top.

.. NOTE: This document is user facing. Please word the changes in such a way
.. that users understand how the changes affect the new version.

2.0.0-dev
-----------------
+ Redesigned CLI to make it much easier to use with streaming data.
+ Added an algorithm that can handle streaming data with no known input size.
+ Improved speed of the python algorithm. It is now 5 times faster than the
  old python algorithm. It is also 3 times faster than the cython algorithm
  from v1.2.0.
+ The cython parts of the code have been deprecated for easier installation
  and better platform compatibility.

1.2.0
-----------------
+ Enable pure python fallback so package can be installed on all systems.
+ Updated the documentation to reflect changes in speed because of the upstream
  improvements and the cythonizing of the algorithm in 1.1.0.
+ Upstream contributions to `xopen <https://github.com/marcelm/xopen>`_ have
  made the reading of gzipped fastq files significantly faster. Newer
  versions of xopen are now added as a requirement.

1.1.0
-----------------
+ Enable the building of wheels for the project now that Cython extensions
  are used. Thanks to @marcelm  for providing a working build script on
  https://github.com/marcelm/dnaio.
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