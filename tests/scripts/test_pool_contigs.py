import os
import tempfile
import unittest
import subprocess
from pathlib import Path

from tangle.sequence import write_fasta_from_dict, read_fasta_as_dict
from tangle.detected import DetectedTable
from tangle.models import CSVSource


class TestPoolContigs(unittest.TestCase):

    def test_pool_contigs_adds_genome_accession_to_accession(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            out_faa = temp_dir / "out.faa"

            in_dir1 = temp_dir / "g1"
            in_dir1.mkdir()
            in_faa1 = in_dir1 / "in1.faa"
            in_dir2 = temp_dir / "g2"
            in_dir2.mkdir()
            in_faa2 = in_dir2 / "in2.faa"
            in_dir3 = temp_dir / "g3"
            in_dir3.mkdir()
            in_faa3 = in_dir3 / "in3.faa"

            g1_sequences = { "t1": "A", "t2": "S" }
            g2_sequences = { "t3": "L" }
            g3_sequences = { "t5": "M", "t6": "Q" }

            write_fasta_from_dict(g1_sequences, str(in_faa1))
            write_fasta_from_dict(g2_sequences, str(in_faa2))
            write_fasta_from_dict(g3_sequences, str(in_faa3))

            cmd = ["python3", "scripts/pool-contigs.py", str(out_faa), str(in_faa1), str(in_faa2), str(in_faa3)]

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            sequences = read_fasta_as_dict(out_faa)

            self.assertEqual(sequences, {
                "g1|t1": "A",
                "g1|t2": "S",
                "g2|t3": "L",
                "g3|t5": "M",
                "g3|t6": "Q"
            })

    def test_pool_contigs_uses_parent_dir_name_in_full_as_genome_accession_across_different_input_file_names(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            out_faa = temp_dir / "out.faa"

            in_dir1 = temp_dir / "g1.1"
            in_dir1.mkdir()
            in_faa1 = in_dir1 / "in1.faa"
            in_dir2 = temp_dir / "g1.2"
            in_dir2.mkdir()
            in_faa2 = in_dir2 / "in2.faa"
            in_faa3 = in_dir1 / "in3.faa"

            g1_sequences = { "t1": "A", "t2": "S" }
            g2_sequences = { "t3": "L" }
            g3_sequences = { "t5": "M", "t6": "Q" }

            write_fasta_from_dict(g1_sequences, str(in_faa1))
            write_fasta_from_dict(g2_sequences, str(in_faa2))
            write_fasta_from_dict(g3_sequences, str(in_faa3))

            cmd = ["python3", "scripts/pool-contigs.py", str(out_faa), str(in_faa1), str(in_faa2), str(in_faa3)]

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            sequences = read_fasta_as_dict(out_faa)

            self.assertEqual(sequences, {
                "g1.1|t1": "A",
                "g1.1|t2": "S",
                "g1.2|t3": "L",
                "g1.1|t5": "M",
                "g1.1|t6": "Q"
            })
