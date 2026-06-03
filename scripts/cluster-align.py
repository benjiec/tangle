import sys
import shutil
import argparse
import subprocess
import tempfile
from pathlib import Path
from tangle import open_file_to_read
from tangle.cluster import cluster_name_from_repr
from tangle.sequence import write_fasta_from_dict

parser = argparse.ArgumentParser()
parser.add_argument("mmseqs_all_seq_file")
parser.add_argument("output_file")
parser.add_argument("cluster_name")
args = parser.parse_args()

last_line_is_sequence = False
last_accession = None

cluster_name = None
target_cluster = None

with open_file_to_read(args.mmseqs_all_seq_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith(">"):
            if last_line_is_sequence:  # this line may be a new cluster name or just a member
                last_accession = line[1:]
            else:  # last accession is a cluster name
                if last_accession and cluster_name_from_repr(last_accession) == args.cluster_name:  # found the cluster
                    target_cluster = {}
                    cluster_name = args.cluster_name
                elif cluster_name:  # just finished the target cluster
                    break
                last_accession = line[1:]
            last_line_is_sequence = False
        else:
            assert last_line_is_sequence is False
            if cluster_name:
                target_cluster[last_accession] = line
            last_line_is_sequence = True

if cluster_name is None:
    print("Did not find cluster with name", args.cluster_name)
    sys.exit(-1)

with tempfile.TemporaryDirectory() as tmpdir:
    input_file = Path(tmpdir) / "input.faa"
    write_fasta_from_dict(target_cluster, str(input_file))

    cmd = ["docker", "run",
           "--platform", "linux/amd64",
           "--rm",
           "-v", f"{tmpdir}:/app",
           "pegi3s/muscle",
           "-in", "/app/input.faa",
           "-out", "/app/output.faa"]
    print(" ".join(cmd))
    subprocess.run(cmd)

    shutil.copy(Path(tmpdir) / "output.faa", args.output_file)
