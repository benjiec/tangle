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


## Environment/Directory Setup

Point the TANGLE_WORLD environment variable to a root directory. This is where
all tangle files are located.

Set the TANGLE_AREA environment variable to name of a focus area, e.g. "coral".

`scripts/world` scripts will maintain files under TANGLE_WORLD. `scripts/area`
scripts will maintain files under the focus area.


## World Scripts

Download files related to an NCBI genome accession

```
python3 scripts/world/ncbi-download.py <accession>
```

Download various KEGG files

```
python3 scripts/world/kegg-download.sh
```


## Area Scripts

Genomes to be used for an area should be manually curated in the `genomes.csv`
file under the area directory. This CSV should follow the schema outlined in
`tangle.genomes.GenomeAccessionList` table.

To get list of genomes, then filter by those requiring protein detection, and
those with NCBI curated proteins, respectively, use these scripts

```
python3 scripts/area/genome-list.py
python3 scripts/area/genome-list.py -d
python3 scripts/area/genome-list.py -n
```

You can use this with the `ncbi-download.py` script, e.g.

```
python3 scripts/area/genome-list.py | python3 scripts/world/ncbi-download.py -
```

And to fetch taxonomy metadata - note that the taxonomy files are kept in
"world", and shared across areas.

```
python3 scripts/area/genome-list.py | python3 scripts/world/ncbi-genome-metadata.py -
```
