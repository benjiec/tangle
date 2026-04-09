import os
import shutil
import itertools
import subprocess
from pathlib import Path
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict
from tangle.models import CSVSource
from tangle.detected import DetectedTable
from collections import defaultdict


def cluster_proteins(faa_fn, cluster_script):
    cluster_fn = faa_fn+"_clusters_cluster.tsv"

    cmd = ["python3", cluster_script,
           "--coverage", "0.95", "--min-seq-id", "0.95",
           faa_fn]
    subprocess.run(cmd)

    os.unlink(faa_fn+"_clusters_all_seqs.fasta")
    os.unlink(faa_fn+"_clusters_rep_seq.fasta")
    return cluster_fn


def load_clusters(cluster_fn):
    clusters = defaultdict(list)
    with open(cluster_fn, "r") as f:
        for line in f:
            repr, member = line.strip().split("\t")
            clusters[repr].append(member)
    return clusters


# locus is (contig, query_left, query_right, strand)
def get_target_loci(rows):

    target_accession_locus = {}
    group_fn = lambda row: row["target_accession"]
    rows = sorted(rows, key=group_fn)
    for tacc, group in itertools.groupby(rows, group_fn):
        group = list(group)
        query_left = min([min(row["query_start"], row["query_end"]) for row in group])
        query_right = max([max(row["query_start"], row["query_end"]) for row in group])
        strand = 1 if group[0]["query_start"] < group[0]["query_end"] else -1
        locus = (group[0]["query_accession"], query_left, query_right, strand)
        target_accession_locus[group[0]["target_accession"]] = locus

        query_left = min([min(row["query_start"], row["query_end"]) for row in group])
        query_right = max([max(row["query_start"], row["query_end"]) for row in group])
        strand = 1 if group[0]["query_start"] < group[0]["query_end"] else -1
        locus = (group[0]["query_accession"], query_left, query_right, strand)
        target_accession_locus[tacc] = locus

    return target_accession_locus


def get_best_ko_match(acc, matches):
    matches = [row for row in matches if row["query_accession"] == acc]

    # smallest is above threshold AND lowest evalue
    matches = sorted(matches, key=lambda row: (0 if row["bitscore"] > row["bitscore_threshold"] else 1, row["evalue"]))
    return matches[0]["target_accession"], matches[0]["evalue"]


def same_loci(a, b, buffer=100):
    # sort by query_left
    a, b = sorted([a, b], key=lambda locus: locus[1])
    # since sorted above, a.query_left is already less than or equal to b.query_left
    return a[0] == b[0] and a[3] == b[3] and b[2]-buffer < a[2]


def filter(tsv_fn, fasta_fn, cluster_fn, matches, keep_original=True):
    source = CSVSource(DetectedTable, tsv_fn)
    rows = source.values()
    seqs = read_fasta_as_dict(fasta_fn)
    clusters = load_clusters(cluster_fn)

    target_loci = get_target_loci(rows)
    target_ko_eval = {acc:get_best_ko_match(acc, matches) for acc in target_loci.keys()}

    to_keep = []

    for cluster, members in clusters.items():
        # print("cluster", cluster)

	# sort members by (ko, evalue), so we encounter the best match first
        members = sorted(members, key=lambda acc: target_ko_eval[acc])

        to_keep_in_cluster = {}
        for member in members:
            ko = target_ko_eval[member][0]
            locus = target_loci[member]

            found_match = False
            for kept_acc, (kept_ko, kept_locus) in to_keep_in_cluster.items():
                if ko == kept_ko and same_loci(locus, kept_locus):
                    found_match = True
                    break
            if not found_match:
                to_keep_in_cluster[member] = (ko, locus)
                # print("  keep", member, ko, locus)
            else:
                # print("  skip", member, ko, locus)
                pass

        to_keep.extend(list(to_keep_in_cluster.keys()))

    if keep_original:
        orig_fn = tsv_fn+".pre_cluster_filter"
        shutil.copy(tsv_fn, orig_fn)
        orig_fn = fasta_fn+".pre_cluster_filter"
        shutil.copy(fasta_fn, orig_fn)

    rows = [row for row in rows if row["target_accession"] in to_keep]
    seqs = {k:v for k,v in seqs.items() if k in to_keep}

    DetectedTable.write_tsv(tsv_fn, rows)
    write_fasta_from_dict(seqs, fasta_fn)


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--forget-original", action="store_true", default=False)
ap.add_argument("--fasta-filename", default="proteins.faa")
ap.add_argument("--tsv-filename", default="proteins.tsv")
ap.add_argument("--cluster-script", default="tangle/scripts/mmseqs-cluster.py")
ap.add_argument("--ko-classification-tsv", required=True)
ap.add_argument("genome_dirs", nargs="+")
args = ap.parse_args()

filter_tsv = CSVSource(DetectedTable, args.ko_classification_tsv)
matches_by_db = defaultdict(list)
for row in filter_tsv.values():
    db = row["query_database"]
    matches_by_db[db].append(row)

for genome_dir in args.genome_dirs:
    genome_path = Path(genome_dir)
    genome_acc = str(genome_path.name)
    if genome_acc not in matches_by_db:
        print(f"{genome_dir}: genome accession {genome_acc} not in filter file {args.ko_classification_tsv}, skip")
        continue

    tsv_fn = str(genome_path / args.tsv_filename)
    faa_fn = str(genome_path / args.fasta_filename)
    cluster_fn = cluster_proteins(faa_fn, args.cluster_script)

    matches = matches_by_db[genome_acc]
    filter(tsv_fn, faa_fn, cluster_fn, matches, not args.forget_original)
    os.unlink(cluster_fn)
    print(genome_dir)
