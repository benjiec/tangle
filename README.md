# Tangle

Tangle is a platform / ecosystem of tools to help curate / classify proteins
and transcripts across species.

There are several repositories in this project

  * `tangle`: (this repository) core data models, core libraries, scripts to download public data
  * `heap`: tools to annotate proteins and transcripts, by structure or sequence similarity
  * `needle`: HMM based detection of protein sequences from genomic sequences, by-passing gene prediction
  * `pile`: tools to work with RNAseq data, including assembly, searching, comparison, and quantification


## Setup

If another "consumer" repository depends on this repository, add the following
to the consumer repository's `pyproject.toml` or `requirements.txt` file

```
tangle @ git+https://github.com/benjiec/tangle.git@<hash>
```

