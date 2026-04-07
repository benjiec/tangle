# demultiplex multiple genome's faa and TSV outputs, from using
# genome_accession|contig in fasta, to listing genome_accesss as query and
# target databases

import argparse
from pathlib import Path
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict
from tangle.models import CSVSource
from tangle.detected import DetectedTable

ap = argparse.ArgumentParser()
ap.add_argument("tsv_fn")
ap.add_argument("modified_tsv_fn")
ap.add_argument("--pooled-target-fasta", default=None)
ap.add_argument("--demuxed-fasta-parent-dir", default=None)
ap.add_argument("--use-existing-target-database", action="store_true", default=False)
ap.add_argument("--demuxed-fasta-filename", default="proteins.faa")
ap.add_argument("--demuxed-tsv-filename", default="proteins.tsv")

args = ap.parse_args()

source = CSVSource(DetectedTable, args.tsv_fn)
rows = source.values()

if args.pooled_target_fasta:
    protein_sequences = read_fasta_as_dict(args.pooled_target_fasta)
    proteins_by_db = {}
else:
    protein_sequences = None

def convert_accession(a):
    if "|" in a:
        splitted = a.split("|")
        return splitted[0], "|".join(splitted[1:])
    return None, a

for row in rows:

    sequence = None
    if protein_sequences:
        if row["target_accession"] not in protein_sequences:
            print(f"warning: cannot find {row['target_accession']} in {args.pooled_target_fasta}")
        else:
            sequence = protein_sequences[row["target_accession"]]

    query_db, query_acc = convert_accession(row["query_accession"])
    if query_db:
        row["query_database"] = query_db
        row["query_accession"] = query_acc

    target_db, target_acc = convert_accession(row["target_accession"])
    if target_db:
        row["target_database"] = target_db
        row["target_accession"] = target_acc
    elif protein_sequences and args.use_existing_target_database:
        target_db = row["target_database"]
    elif protein_sequences:
        print(f"warning: cannot determine a target_database value for {row['target_accession']}, skip writing to a fasta file")

    if protein_sequences and target_db:
        if target_db not in proteins_by_db:
            proteins_by_db[target_db] = {}
        if sequence:
            proteins_by_db[target_db][target_acc] = sequence

DetectedTable.write_tsv(args.modified_tsv_fn, rows)

if protein_sequences:
    for db, seq_dict in proteins_by_db.items():
        parent_parent_dir = Path(args.demuxed_fasta_parent_dir)
        parent_parent_dir.mkdir(exist_ok=True)
        parent_dir = parent_parent_dir / db
        parent_dir.mkdir(exist_ok=True)

        fasta_fn = parent_dir / args.demuxed_fasta_filename
        write_fasta_from_dict(seq_dict, str(fasta_fn))

        tsv_fn = str(parent_dir / args.demuxed_tsv_filename)
        db_rows = [row for row in rows if row["target_database"] == db]
        DetectedTable.write_tsv(tsv_fn, db_rows)
