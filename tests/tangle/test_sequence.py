import os
import unittest
import tempfile

from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict


class TestReadWriteFasta(unittest.TestCase):

    def test_read_multiple_line_fasta(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.fa")
            with open(tmpf, "w") as f:
                f.write(">test1\nagc\nttt\naaa\n>test2\nccc")

            fasta_1 = read_fasta_as_dict(tmpf)
            self.assertCountEqual(list(fasta_1.keys()), ["test1", "test2"])
            self.assertEqual(fasta_1["test1"], "agctttaaa")
            self.assertEqual(fasta_1["test2"], "ccc")

    def test_handles_accession_as_string_before_first_whitespace(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.fa")
            with open(tmpf, "w") as f:
                f.write(">test1-test2 test3\nagc\nttt\naaa\n>test 4\nccc\n>test5|test6 blah\nagg")

            fasta_1 = read_fasta_as_dict(tmpf)
            self.assertCountEqual(list(fasta_1.keys()), ["test1-test2", "test", "test5|test6"])
            self.assertEqual(fasta_1["test1-test2"], "agctttaaa")
            self.assertEqual(fasta_1["test"], "ccc")
            self.assertEqual(fasta_1["test5|test6"], "agg")

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
