import os
import tempfile
import unittest
import subprocess
from pathlib import Path

from tangle.sequence import write_fasta_from_dict, read_fasta_as_dict
from tangle.detected import DetectedTable
from tangle.models import CSVSource


class TestFilterProteins(unittest.TestCase):

    def test_filter_proteins_removes_accessions_from_both_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            genome_dir = temp_dir / "g1"
            genome_dir.mkdir()
            in_tsv = genome_dir / "proteins.tsv"
            in_faa = genome_dir / "proteins.faa"

            filter_tsv = temp_dir / "filter.tsv"

            rows = [
                dict(detection_type="sequence", detection_method="hmm", batch="b1",
                     query_database="g1", query_accession="q1", query_type="contig",
                     target_database="g1", target_accession="t1", target_type="protein",
                     query_start=1, query_end=2, target_start=1, target_end=2),
                dict(detection_type="sequence", detection_method="hmm", batch="b1",
                     query_database="g1", query_accession="q2", query_type="contig",
                     target_database="g1", target_accession="t2", target_type="protein",
                     query_start=1, query_end=2, target_start=1, target_end=2)
            ]

            DetectedTable.write_tsv(str(in_tsv), rows)
            sequences = { "t1": "A", "t2": "S" }
            write_fasta_from_dict(sequences, str(in_faa))

            rows = [
                dict(detection_type="sequence", detection_method="hmm", batch="b1",
                     query_database="g1", query_accession="t1", query_type="protein",
                     target_database="KO", target_accession="h1", target_type="protein",
                     query_start=1, query_end=2, target_start=1, target_end=2),
                dict(detection_type="sequence", detection_method="hmm", batch="b1",
                     query_database="g2", query_accession="t2", query_type="protein",
                     target_database="KO", target_accession="h2", target_type="protein",
                     query_start=1, query_end=2, target_start=1, target_end=2)
            ]
            DetectedTable.write_tsv(str(filter_tsv), rows)

            cmd = ["python3", "scripts/filter-proteins.py",
                   "--filter-targets-with-queries-from", str(filter_tsv), str(genome_dir)]

            subprocess.run(cmd)

            seq = read_fasta_as_dict(str(in_faa))
            values = CSVSource(DetectedTable, str(in_tsv)).values()

            # t1 is in filter file, keep
            # t2 is in filter file under different genome, so remove
            self.assertEqual(seq, dict(t1="A"))
            self.assertCountEqual([(row["target_database"], row["target_accession"]) for row in values], [("g1", "t1")])
