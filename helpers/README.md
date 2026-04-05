
## Pre-generated Relations

Use the following script to convert UniProt to Pfam data, downloaded from
UniProt, to our detected TSV format.

The second argument should be a list of SwissProt IDs present in the AlphaFold
SwissProt database. That argument is just a file with list of accessions from
the first file to keep.

```
gzcat protein2ipr.dat.gz| awk -F'\t' '$4 ~ "PF"' - > protein-pfam.txt
python3 helpers/ipr-pfam.py protein-pfam.txt afdb-swissprot.ids.txt uniprot-pfam.tsv.gz
```
