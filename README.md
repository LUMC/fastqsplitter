# fastqsplitter

A simple application to split FASTQ files.

The algorithm is a reimplementation from [biopet-fastqsplitter](
https://github.com/biopet/fastqsplitter). Fastqsplitter reads a fastq
file. It then splits the reads over the designated output files.

fastqsplitter uses the excellent [xopen library by @marcelm](
https://github.com/marcelm/xopen). This determines by extension whether the 
file is compressed. If the output files for fastqsplitter end with '.gz' they 
will be gzip compressed automatically. The default compression level is 1 and
can be changed by using the `-c` flag.

### Example

With an input file `input_fastq.gz` of 2.3 GB. 
`fastqsplitter -i input_fastq.gz 
-o split.1.fq.gz -o split.2.fq.gz -o split.3.fq.gz`

Fastqsplitter will read `input_fastq.gz`. The first 100 reads will go
to `split.1.fq.gz`, read 101-200 will go to `split.2.fq.gz`, read
`201-300` will go to `split.3.fq.gz`, read 301-400 will go to `split.1.fq.gz`,
 etc. 

This way the fastq reads are evenly distributed, with a difference of maximum
100 reads between outputfiles.


