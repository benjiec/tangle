import os
import unittest
import tempfile

from tangle.project import recursive_project
from tangle.models import CSVSource, Schema
from tangle.detected import DetectedTable


detected_row_fixture = dict(
    detection_type="sequence",
    detection_method="hmm",
    batch="foo",
    query_database ="d",
    query_type="protein",
    target_database ="d",
    target_type="protein",
)


class TestFeatureProjection(unittest.TestCase):

    def test_finds_projections_across_multiple_files(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf1 = os.path.join(tmpd, "test1.tsv")
            tmpf2 = os.path.join(tmpd, "test2.tsv")

            DetectedTable.write_tsv(tmpf1, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=12, query_end=42,
                    target_accession="acc2", target_start=1, target_end=70
                ),
                detected_row_fixture | dict(
                    query_accession="acc3", query_start=15, query_end=30,
                    target_accession="acc4", target_start=1, target_end=20
                )
            ])

            DetectedTable.write_tsv(tmpf2, [
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=3, query_end=20,
                    target_accession="acc3", target_start=15, target_end=30
                ),
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=80, query_end=100,
                    target_accession="acc5", target_start=1, target_end=20
                )
            ])

            source = CSVSource(DetectedTable, tmpf1, tmpf2)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project("acc1", schema, fuzz=0)
            self.assertEqual(results, [
                ("acc2", 1, 70, 1),
                ("acc3", 15, 30, 1),
                ("acc4", 1, 20, 1),
            ])

    def test_finds_projections_with_fuzz_factor(self):
        self.assertEqual(True, False)

    def test_reports_strand_relative_to_root(self):
        self.assertEqual(True, False)

    def test_matching_uses_db_and_type(self):
        self.assertEqual(True, False)
