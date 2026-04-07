import argparse
import subprocess
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fasta")
    parser.add_argument("--cluster_file_prefix", default=None)
    args = parser.parse_args()

    cluster_file_prefix = args.cluster_file_prefix
    if cluster_file_prefix is None:
        cluster_file_prefix = args.input_fasta+"_clusters"

    work_dir = Path(args.input_fasta).parent.resolve()

    cmd = ["docker", "run",
           "--rm",
           "-v", f"{work_dir}:/work",
           "ghcr.io/soedinglab/mmseqs2",
           "easy-cluster",
           f"/work/{args.input_fasta}",
           f"/work/{cluster_file_prefix}",
           "/tmp"]
    print(" ".join(cmd))
    subprocess.run(cmd)
