# filter fasta by ids

from tangle import open_file_to_read
from tangle.sequence import read_fasta_as_dict

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("fasta_file")
ap.add_argument("identifier_file")
ap.add_argument("--prefix-with-underscore", action="store_true", default=False)
args = ap.parse_args()

identifiers = []
with open_file_to_read(args.identifier_file) as f:
    for line in f.readlines():
        identifiers.append(line.strip())

seqs = read_fasta_as_dict(args.fasta_file)

if args.prefix_with_underscore:
    new_seqs = {}
    identifiers = sorted([x+"_" for x in identifiers])
    seq_accessions = sorted(seqs.keys())
    seq_acc_i = 0
    for id in identifiers:
        found = False
        for i in range(seq_acc_i, len(seq_accessions)):
            if seq_accessions[i].startswith(id):
                # print(f"{i}: {id} in {seq_accessions[i]}")
                # print(f"  {i+1}: next {seq_accessions[i+1]}")
                found = True
                seq_acc_i = i
                new_seqs[seq_accessions[i]] = seqs[seq_accessions[i]]
            elif found is True:  # already found, so not going to find another instance
                # print(f"stop {id} at {i}")
                break
        if found is False:
            # print(f"cannot find {id}, seq_acc_i is {seq_acc_i}")
            # assert found is True
            pass
    seqs = new_seqs

else:
    seqs = {k:v for k,v in seqs.items() if k in identifiers}

for k,v in seqs.items():
    print(f">{k}\n{v}")
