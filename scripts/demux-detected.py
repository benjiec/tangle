# demultiplex multiple genome's faa and TSV outputs, from using
# genome_accession|contig in fasta, to listing genome_accesss as query and
# target databases

import shutil
from pathlib import Path
from tangle import unique_batch
from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict
from tangle.models import CSVSource
from tangle.detected import DetectedTable


def convert_accession(a):
    if "|" in a:
        splitted = a.split("|")
        return splitted[0], "|".join(splitted[1:])
    return None, a


def demux_tsv(tsv_fn, fasta_fn, demuxed_parent_dir=None, keep_original=True,
              demuxed_fasta_filename=None, demuxed_tsv_filename=None, set_batch_to=None):

    if demuxed_fasta_filename is None:
        demuxed_fasta_filename = "proteins.faa"
    if demuxed_tsv_filename is None:
        demuxed_tsv_filename = "proteins.tsv"

    source = CSVSource(DetectedTable, tsv_fn)
    rows = source.values()

    if fasta_fn:
        protein_sequences = read_fasta_as_dict(fasta_fn)
        proteins_by_db = {}
    else:
        protein_sequences = None

    for row in rows:
        sequence = None
        if set_batch_to is not None:
            row["batch"] = set_batch_to

        query_db, query_acc = convert_accession(row["query_accession"])
        if query_db:
            row["query_database"] = query_db
            row["query_accession"] = query_acc

        orig_target_acc = row["target_accession"]
        target_db, target_acc = convert_accession(row["target_accession"])
        if target_db:
            row["target_database"] = target_db
            row["target_accession"] = target_acc

        if protein_sequences:
            if orig_target_acc not in protein_sequences:
                print(f"warning: cannot find {orig_target_acc} in {fasta_fn}")
            elif not target_db:
                print(f"warning: cannot determine a target_database value for {orig_target_acc}, skip writing to a fasta file")
            else:
                sequence = protein_sequences[orig_target_acc]
                if target_db not in proteins_by_db:
                    proteins_by_db[target_db] = {}
                proteins_by_db[target_db][target_acc] = sequence

    if keep_original:
        orig_fn = tsv_fn+".orig"
        shutil.copy(tsv_fn, orig_fn)
    DetectedTable.write_tsv(tsv_fn, rows)
    print(tsv_fn)

    if protein_sequences:
        parent_parent_dir = Path(demuxed_parent_dir)
        parent_parent_dir.mkdir(exist_ok=True)

        for db, seq_dict in proteins_by_db.items():
            parent_dir = parent_parent_dir / db
            parent_dir.mkdir(exist_ok=True)

            db_fasta_fn = parent_dir / demuxed_fasta_filename
            write_fasta_from_dict(seq_dict, str(db_fasta_fn), append=True)

            db_tsv_fn = str(parent_dir / demuxed_tsv_filename)
            db_rows = [row for row in rows if row["target_database"] == db]
            DetectedTable.write_tsv(db_tsv_fn, db_rows, append=True)

            print(db_tsv_fn, str(parent_dir))


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--forget-original", action="store_true", default=False)
ap.add_argument("--set-batch", action="store_true", default=False)
ap.add_argument("--pooled-target-fasta", default=None)
ap.add_argument("--pooled-target-fasta-suffix", default=None)
ap.add_argument("--demuxed-parent-dir", default=None)
ap.add_argument("--demuxed-fasta-filename", default="proteins.faa")
ap.add_argument("--demuxed-tsv-filename", default="proteins.tsv")
ap.add_argument("pooled_tsv", nargs="+")
args = ap.parse_args()

if (args.pooled_target_fasta is not None or \
    args.pooled_target_fasta_suffix is not None) and \
   args.demuxed_parent_dir is None:
    raise Exception("Please specify --demuxed-parent-dir if there is a pooled fasta file")

if len(args.pooled_tsv) > 1 and args.demuxed_parent_dir and not args.pooled_target_fasta_suffix:
    raise Exception("If demux multiple files, requires --pooled-target-fasta-suffix")

new_batch = None
if args.set_batch:
    new_batch = unique_batch()

def get_fasta_fn(fasta_fn, tsv_fn, fasta_fn_suffix):
    if fasta_fn_suffix:
        tsv_path = Path(tsv_fn)
        return str(tsv_path.parent / tsv_path.stem) + fasta_fn_suffix
    return fasta_fn

for tsv_fn in args.pooled_tsv:
    fasta_fn = get_fasta_fn(args.pooled_target_fasta, tsv_fn, args.pooled_target_fasta_suffix)
    demux_tsv(tsv_fn, fasta_fn,
              demuxed_parent_dir=args.demuxed_parent_dir,
              keep_original=not args.forget_original,
              demuxed_fasta_filename=args.demuxed_fasta_filename,
              demuxed_tsv_filename=args.demuxed_tsv_filename,
              set_batch_to=new_batch)
