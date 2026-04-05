import argparse
from tangle import open_file_to_read, unique_batch
from tangle.detected import DetectedTable

ap = argparse.ArgumentParser()
ap.add_argument("ipr_pfam_file")
ap.add_argument("selected_ids_file")
ap.add_argument("detected_tsv")
args = ap.parse_args()

rows = []
batch = unique_batch()

with open_file_to_read(args.selected_ids_file) as f_filter:
    keep = {l.strip():1 for l in f_filter}

with open_file_to_read(args.ipr_pfam_file) as f:
    for line in f:
        tokens = line.split("\t")
        query_accession = tokens[0]
        target_accession = tokens[3]
        query_start = tokens[4]
        query_end = tokens[5]

        if query_accession not in keep:
            continue

        row = dict(
            detection_type="sequence",
            detection_method="hmm",
            batch=batch,
            query_accession=query_accession,
            query_database="SwissProt",
            query_type="protein",
            target_accession=target_accession,
            target_database="Pfam-A",
            target_type="protein",
            query_start=query_start,
            query_end=query_end
        )
        rows.append(row)

        if len(rows) == 100:
            DetectedTable.write_tsv(args.detected_tsv, rows, append=True)
            rows = []

DetectedTable.write_tsv(args.detected_tsv, rows, append=True)
