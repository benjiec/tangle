# filter fasta by ids

from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("fasta_file")
ap.add_argument("--database", required=True)
ap.add_argument("--append-to", default=None)
ap.add_argument("--delim", default="|")
args = ap.parse_args()

seqs = read_fasta_as_dict(args.fasta_file)
seqs = {f"{args.database}{args.delim}{k}":v for k,v in seqs.items()}

if args.append_to:
    write_fasta_from_dict(seqs, args.append_to, append=True)
else:
    for k,v in seqs.items():
        print(f">{k}\n{v}")
