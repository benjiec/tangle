# creates a manifest from tsv file

from pathlib import Path
from tangle.sequence import read_fasta_as_dict
from tangle.manifest import ManifestTable

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--sequence-source", required=True)
ap.add_argument("--sequence-type", required=True)
ap.add_argument("--append", action="store_true", default=False)
ap.add_argument("manifest_tsv")
ap.add_argument("genome_fastas", nargs="+")
args = ap.parse_args()

for faa_fn in args.genome_fastas:
    genome_accession = Path(faa_fn).parent.name
    print(faa_fn, genome_accession, args.sequence_source)
    sequences = read_fasta_as_dict(faa_fn)

    rows = [dict(
        sequence_source=args.sequence_source,
        sequence_accession=k,
        sequence_database=genome_accession,
        sequence_type=args.sequence_type,
      ) for k,v in sequences.items()]

    ManifestTable.write_tsv(args.manifest_tsv, rows, append=args.append)
