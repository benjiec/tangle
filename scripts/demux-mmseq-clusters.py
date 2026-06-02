from tangle import open_file_to_read, unique_batch
from tangle.cluster import ClusterTable


def convert_accession(a):
    if "|" in a:
        splitted = a.split("|")
        return splitted[0], "|".join(splitted[1:])
    return None, a


def demux_tsv(cluster_output, clustering_description, cluster_type, cluster_tsv, append, parameters):
    rows = []
    batch = unique_batch()
    with open_file_to_read(cluster_output) as f:
        for line in f:
            repr, member = line.strip().split("\t")
            db, acc = convert_accession(member)
            rows.append(dict(
                batch=batch,
                clustering_description=clustering_description,
                cluster_name=repr,
                cluster_type=cluster_type,
                member_database=db,
                member_accession=acc,
                parameters=parameters
            ))

    ClusterTable.write_tsv(cluster_tsv, rows, append=append)


import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--cluster-type", required=True)
ap.add_argument("--clustering-description", required=True)
ap.add_argument("--parameters")
ap.add_argument("cluster_output")
ap.add_argument("cluster_tsv")
ap.add_argument("--append", action="store_true", default=False)
args = ap.parse_args()

demux_tsv(
    args.cluster_output,
    args.clustering_description,
    args.cluster_type,
    args.cluster_tsv,
    args.append,
    args.parameters
)
