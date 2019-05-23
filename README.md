# fastqsplitter

A simple application to split FASTQ files.

The algorithm is a reimplementation from [biopet-fastqsplitter](
https://github.com/biopet/fastqsplitter). Fastqsplitter reads a fastq
file. It then splits the reads over the designated output files.

This application does NOT work with multiline fastq sequences.

fastqsplitter uses the excellent [xopen library by @marcelm](
https://github.com/marcelm/xopen). This determines by extension whether the 
file is compressed. If the output files for fastqsplitter end with '.gz' they 
will be gzip compressed automatically. The default compression level is 1 and
can be changed by using the `-c` flag. 

Because of xopen the output files will be compressed using pigz (parallel gzip).
The number of threads can be set with the `-t` flag. The default is 1. 

### Example

With an input file `input_fastq.gz` of 2.3 GB. 
`fastqsplitter -i input_fastq.gz 
-o split.1.fq.gz -o split.2.fq.gz -o split.3.fq.gz`

Fastqsplitter will read `input_fastq.gz`. The first 100 reads will go
to `split.1.fq.gz`, read 101-200 will go to `split.2.fq.gz`, read
`201-300` will go to `split.3.fq.gz`, read 301-400 will go to `split.1.fq.gz`,
 etc. 

This way the fastq reads are evenly distributed, with a difference of maximum
100 reads between output files.


### Comparisons

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

The used test machine had 32 GB memory (2x16GB 2133mhz), a Intel core i7-6700
(4 cores, 8 threads) and a Sandisk X400 500gb SSD.

|                       | fastqsplitter (defaults) | fastqsplitter -t 4 -c 5 |  biopet-fastqsplitter |
| --------------------  | ------------------------ | ----------------------- | --------------------- |
|real time              | 0m50.932s                | 1m28.153s               | 1m41.385s             |
|total cpu time         | 3m7.116s                 | 7m55.436s               | 8m20.304s             |
|max mem                | 24 MB                    | 32MB                    | 400MB                 |
|max vmem               | 110 MB                   | 1.6 GB                  | 11.0 GB               |
|output files total size| 2290 MB                  | 2025 MB                 | 2025 MB               |

The outcomes for multiple runs were fairly consistent with a max +-3 second difference between runs.