import os
import unittest
import tempfile

from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict


class TestReadWriteFasta(unittest.TestCase):

    def test_read_write_append_consistently(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.fa")

            fasta_1 = dict(a="a", g="gg", c="ccc")
            write_fasta_from_dict(fasta_1, tmpf)
            fasta_2 = read_fasta_as_dict(tmpf)
            self.assertEqual(fasta_1, fasta_2)

            fasta_3 = dict(t="tttt")
            write_fasta_from_dict(fasta_3, tmpf, append=True)
            fasta_4 = read_fasta_as_dict(tmpf)
            self.assertEqual(fasta_1 | fasta_3, fasta_4)

    def test_read_write_compressed(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.gz")

            fasta_1 = dict(a="a", g="gg", c="ccc")
            write_fasta_from_dict(fasta_1, tmpf)
            fasta_2 = read_fasta_as_dict(tmpf)
            self.assertEqual(fasta_1, fasta_2)
