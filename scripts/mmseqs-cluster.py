import argparse
import subprocess
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fasta")
    parser.add_argument("--min-seq-id", type=float, default=None)
    parser.add_argument("--coverage", type=float, default=None)
    parser.add_argument("--cov-mode", type=int, default=None)
    parser.add_argument("--cluster_file_prefix", default=None)
    args = parser.parse_args()

    cluster_file_prefix = args.cluster_file_prefix
    if cluster_file_prefix is None:
        cluster_file_prefix = args.input_fasta+"_clusters"

    work_dir = Path(args.input_fasta).parent.resolve()
    input_faa = Path(args.input_fasta).name

    cmd = ["docker", "run",
           "--rm",
           "-v", f"{work_dir}:/work",
           "ghcr.io/soedinglab/mmseqs2",
           "easy-cluster"]

    if args.min_seq_id is not None:
        cmd.extend(["--min-seq-id", str(args.min_seq_id)])
    if args.cov_mode is not None:
        cmd.extend(["--cov-mode", str(args.cov_mode)])
    if args.coverage is not None:
        cmd.extend(["-c", str(args.coverage)])

    cmd.extend([f"/work/{input_faa}",
                f"/work/{cluster_file_prefix}",
                "/tmp"])

    print(" ".join([str(x) for x in cmd]))
    subprocess.run(cmd)
