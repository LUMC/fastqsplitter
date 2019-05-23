[![](https://travis-ci.org/LUMC/fastqsplitter.svg?branch=develop)](
https://travis-ci.org/LUMC/fastqsplitter)

# fastqsplitter

A simple application to split FASTQ files.

Fastqsplitter reads a fastq
file. It then splits the reads over the designated output files.

This application does NOT work with multiline fastq sequences.

### Quickstart

install fastqsplitter:
```pip install fastqsplitter```

To split an input file `input_fastq.gz` into 3 different files.
`fastqsplitter -i input_fastq.gz 
-o split.1.fq.gz -o split.2.fq.gz -o split.3.fq.gz`

fastqsplitter uses the excellent [xopen library by @marcelm](
-https://github.com/marcelm/xopen). Therefore the input and output files 
compression is determined by the extension. Use ``.gz`` if output files should
be gzip compressed. 

### Documentation

More information on fastqsplitter can be found [on our readthedocs page](
https://fastqsplitter.readthedocs.io/).