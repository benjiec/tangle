# filter genome's protein collection by another detection list

import shutil
from pathlib import Path
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict
from tangle.models import CSVSource
from tangle.detected import DetectedTable
from collections import defaultdict


def filter(tsv_fn, fasta_fn, accessions_to_keep, keep_original=True):

    source = CSVSource(DetectedTable, tsv_fn)
    rows = source.values()
    seqs = read_fasta_as_dict(fasta_fn)

    rows = [row for row in rows if row["target_accession"] in accessions_to_keep]
    seqs = {k:v for k,v in seqs.items() if k in accessions_to_keep}

    if keep_original:
        orig_fn = tsv_fn+".orig"
        shutil.copy(tsv_fn, orig_fn)
        orig_fn = fasta_fn+".orig"
        shutil.copy(fasta_fn, orig_fn)

    DetectedTable.write_tsv(tsv_fn, rows)
    write_fasta_from_dict(seqs, fasta_fn)


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--forget-original", action="store_true", default=False)
ap.add_argument("--fasta-filename", default="proteins.faa")
ap.add_argument("--tsv-filename", default="proteins.tsv")
ap.add_argument("--filter-targets-with-queries-from", required=True)
ap.add_argument("genome_dirs", nargs="+")
args = ap.parse_args()

filter_tsv = CSVSource(DetectedTable, args.filter_targets_with_queries_from)
keep_accessions = defaultdict(set)
for row in filter_tsv.values():
    db = row["query_database"]
    acc = row["query_accession"]
    keep_accessions[db].add(acc)

for genome_dir in args.genome_dirs:
    genome_path = Path(genome_dir)
    genome_acc = str(genome_path.name)
    if genome_acc not in keep_accessions:
        print(f"{genome_dir}: genome accession {genome_acc} not in filter file {args.filter_targets_with_queries_from}, skip")
        continue

    tsv_fn = str(genome_path / args.tsv_filename)
    faa_fn = str(genome_path / args.fasta_filename)
    keep = keep_accessions[genome_acc]
    filter(tsv_fn, faa_fn, keep, not args.forget_original)
    print(genome_dir)
