# filter fasta by ids

from tangle import open_file_to_read
from tangle.sequence import read_fasta_as_dict

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("fasta_file")
ap.add_argument("identifier_file")
args = ap.parse_args()

identifiers = []
with open_file_to_read(args.identifier_file) as f:
    for line in f.readlines():
        identifiers.append(line.strip())

seqs = read_fasta_as_dict(args.fasta_file)
seqs = {k:v for k,v in seqs.items() if k in identifiers}

for k,v in seqs.items():
    print(f">{k}\n{v}")
