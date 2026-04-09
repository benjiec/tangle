import os
import tempfile
import unittest
import subprocess
from pathlib import Path

from tangle.sequence import write_fasta_from_dict, read_fasta_as_dict
from tangle.detected import DetectedTable
from tangle.models import CSVSource


class TestFilterCluster(unittest.TestCase):

    def setUp(self):
        # by default, both on locus (q1, 1, 10, 1)
        self.detection_rows = [
            dict(detection_type="sequence", detection_method="hmm", batch="b1",
                 query_database="g1", query_accession="q1", query_type="contig",
                 target_database="g1", target_accession="t1", target_type="protein",
                 query_start=1, query_end=10, target_start=1, target_end=2),
            dict(detection_type="sequence", detection_method="hmm", batch="b1",
                 query_database="g1", query_accession="q1", query_type="contig",
                 target_database="g1", target_accession="t2", target_type="protein",
                 query_start=2, query_end=8, target_start=1, target_end=2)
        ]

        # by default, both classifies to same profile and t2 has lower evalue
        self.ko_rows = [
            dict(detection_type="sequence", detection_method="hmm", batch="b1",
                 query_database="g1", query_accession="t1", query_type="protein",
                 target_database="KO", target_accession="h1", target_type="protein",
                 query_start=1, query_end=2, target_start=1, target_end=2, evalue=0.002, bitscore=10, bitscore_threshold=9),
            dict(detection_type="sequence", detection_method="hmm", batch="b1",
                 query_database="g1", query_accession="t2", query_type="protein",
                 target_database="KO", target_accession="h1", target_type="protein",
                 query_start=1, query_end=2, target_start=1, target_end=2, evalue=0.001, bitscore=10, bitscore_threshold=9)
        ]

        self.clusters = {"t1": ["t1", "t2"]}

    def write_files(self, temp_dir):
        temp_dir = Path(temp_dir)

        genome_dir = temp_dir / "g1"
        genome_dir.mkdir()
        in_tsv = genome_dir / "proteins.tsv"
        in_faa = genome_dir / "proteins.faa"

        DetectedTable.write_tsv(str(in_tsv), self.detection_rows)
        sequences = { row["target_accession"]: "A" for row in self.detection_rows }
        write_fasta_from_dict(sequences, str(in_faa))

        ko_tsv = temp_dir / "ko.tsv"
        DetectedTable.write_tsv(str(ko_tsv), self.ko_rows)

        cluster_fn = temp_dir / "cluster.tsv"
        with open(cluster_fn, "w") as f:
            for repr, members in self.clusters.items():
                for member in members:
                    f.write(f"{repr}\t{member}\n")

        return genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa

    # DEFAULT CASE
    def test_filter_clustered_proteins_removes_clustered_protein_at_same_locus(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            # t1 is in the same cluster as t2, at same locus, higher e-value, removed
            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t2")])
            self.assertCountEqual(list(seq.keys()), ["t2"])

    def test_filter_clustered_proteins_keeps_multiple_proteins_in_same_cluster_from_different_loci(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

            self.detection_rows[1]["query_accession"] = "q2"

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1"), ("g1", "t2")])
            self.assertCountEqual(list(seq.keys()), ["t1", "t2"])

    def test_filter_clustered_proteins_keeps_multiple_proteins_in_same_cluster_matching_to_different_profile(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

            self.ko_rows[1]["target_accession"] = "h2"

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1"), ("g1", "t2")])
            self.assertCountEqual(list(seq.keys()), ["t1", "t2"])

    def test_filter_clustered_proteins_keeps_lowest_evalue(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

            self.ko_rows[0]["evalue"] = self.ko_rows[1]["evalue"]*0.5

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1")])
            self.assertCountEqual(list(seq.keys()), ["t1"])

    def test_filter_clustered_proteins_keeps_protein_above_bitscore_threshold_even_if_higher_evalue(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

            # t1 has lower evalue
            self.ko_rows[0]["evalue"] = self.ko_rows[1]["evalue"]*0.5
            # but t1 does not meet bitscore threshold
            self.ko_rows[1]["bitscore"] = self.ko_rows[1]["bitscore_threshold"]*2
            self.ko_rows[0]["bitscore"] = self.ko_rows[0]["bitscore_threshold"]*0.5

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t2")])
            self.assertCountEqual(list(seq.keys()), ["t2"])

    def test_filter_clustered_proteins_uses_best_match_for_a_protein_in_ko_file(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

	    # there is now a second t1 classification in ko file, that's a
	    # better match, so t1 will be kept because it now has lower evalue
	    # than t2
            self.ko_rows.append(self.ko_rows[0].copy())
            self.ko_rows[2]["evalue"] = self.ko_rows[1]["evalue"]*0.5
            assert self.ko_rows[0]["evalue"] > self.ko_rows[1]["evalue"]

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1")])
            self.assertCountEqual(list(seq.keys()), ["t1"])

    def test_filter_clustered_proteins_uses_best_match_for_a_protein_in_ko_file_with_different_profile(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

	    # there is now a second t1 classification in ko file, that's a
	    # better match, to a different profile, so t1 and t2 are kept
            self.ko_rows.append(self.ko_rows[0].copy())
            self.ko_rows[2]["evalue"] = self.ko_rows[1]["evalue"]*0.5
            self.ko_rows[2]["target_accession"] = "h2"
            assert self.ko_rows[0]["evalue"] > self.ko_rows[1]["evalue"]

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1"), ("g1", "t2")])
            self.assertCountEqual(list(seq.keys()), ["t1", "t2"])

    def test_filter_clustered_proteins_does_not_keep_protein_not_in_ko_file(self):
        # recall that DEFAULT CASE (see above) is to keep t2

        with tempfile.TemporaryDirectory() as temp_dir:

            self.ko_rows = self.ko_rows[:-1]

            genome_dir, cluster_fn, ko_tsv, in_tsv, in_faa = self.write_files(temp_dir)

            cmd = ["python3", "scripts/filter-clustered-proteins.py",
                   "--cluster-file", str(cluster_fn),
                   "--ko-classification-tsv", str(ko_tsv), str(genome_dir)]
            subprocess.run(cmd)

            seq = read_fasta_as_dict(in_faa)
            values = CSVSource(DetectedTable, in_tsv).values()

            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1")])
            self.assertCountEqual(list(seq.keys()), ["t1"])
