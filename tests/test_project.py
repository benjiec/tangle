import os
import unittest
import tempfile

from tangle.project import recursive_project, Feature, results_to_detected_table
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

    def test_does_not_project_feature_out_side_of_match(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            DetectedTable.write_tsv(tmpf, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=12, query_end=42,
                    target_accession="acc2", target_start=1, target_end=70
                ),
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=3, query_end=20,
                    target_accession="acc3", target_start=15, target_end=30
                ),
                # coordinates of this match on acc2 is outside of the acc2 region matched to acc1
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=80, query_end=100,
                    target_accession="acc5", target_start=1, target_end=20
                )
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 1, 70, 1),
                (Feature("acc3", "d", "protein"), 15, 30, 1),
            ])

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
            ])

            source = CSVSource(DetectedTable, tmpf1, tmpf2)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 1, 70, 1),
                (Feature("acc3", "d", "protein"), 15, 30, 1),
                (Feature("acc4", "d", "protein"), 1, 20, 1),
            ])

    def test_finds_projections_with_fuzz_factor(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            DetectedTable.write_tsv(tmpf, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=12, query_end=42,
                    target_accession="acc2", target_start=10, target_end=70
                ),
                # match ends at 75 on acc2, not 70 from above
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=10, query_end=75,
                    target_accession="acc3", target_start=15, target_end=30
                )
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 10, 70, 1),
            ])

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=5)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 10, 70, 1),
                (Feature("acc3", "d", "protein"), 15, 30, 1),
            ])

    def test_handles_reverse_match_and_reports_strand_relative_to_root(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            DetectedTable.write_tsv(tmpf, [
                # reverse match as specified by query coordinates on acc1
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=42, query_end=12,
                    target_accession="acc2", target_start=10, target_end=70
                ),
                # forward match
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=10, query_end=60,
                    target_accession="acc3", target_start=15, target_end=30
                ),
                # forward match specified with two reversed coordinates
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=68, query_end=48,
                    target_accession="acc5", target_start=220, target_end=205
                ),
                # reverse match as specified by target coordinates on acc4
                detected_row_fixture | dict(
                    query_accession="acc3", query_start=15, query_end=30,
                    target_accession="acc4", target_start=90, target_end=70
                ),
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)
            self.assertCountEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 10, 70, -1),
                (Feature("acc3", "d", "protein"), 15, 30, -1),
                (Feature("acc4", "d", "protein"), 70, 90, 1),
                (Feature("acc5", "d", "protein"), 205, 220, -1),
            ])

    def test_matching_uses_db_and_type(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            acc2_to_acc3_match = dict(
                query_accession="acc2", query_database="d1", query_type="protein", query_start=10, query_end=69,
                target_accession="acc3", target_database="d2", target_type="protein", target_start=15, target_end=30
            )
            acc2_to_acc4_wrong_db = acc2_to_acc3_match | dict(query_database="d2", target_accession="acc4")
            acc2_to_acc5_wrong_type = acc2_to_acc3_match | dict(query_type="transcript", target_accession="acc5")

            DetectedTable.write_tsv(tmpf, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_database="d1", query_type="protein", query_start=12, query_end=42,
                    target_accession="acc2", target_database="d1", target_type="protein", target_start=10, target_end=70
                ),
                detected_row_fixture | acc2_to_acc3_match,
                detected_row_fixture | acc2_to_acc4_wrong_db,
                detected_row_fixture | acc2_to_acc5_wrong_type
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d1", "protein"), schema, fuzz=0)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d1", "protein"), 10, 70, 1),
                (Feature("acc3", "d2", "protein"), 15, 30, 1),
            ])

    def test_does_not_follow_loops(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            DetectedTable.write_tsv(tmpf, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=12, query_end=42,
                    target_accession="acc2", target_start=10, target_end=70
                ),
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=11, query_end=69,
                    target_accession="acc1", target_start=15, target_end=40
                ),
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)
            self.assertEqual([m.summary() for m in results], [
                (Feature("acc2", "d", "protein"), 10, 70, 1),
                (Feature("acc1", "d", "protein"), 15, 40, 1),
            ])

    def test_results_can_become_a_table(self):

        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")
            outf = os.path.join(tmpd, "out.tsv")

            DetectedTable.write_tsv(tmpf, [
                detected_row_fixture | dict(
                    query_accession="acc1", query_start=12, query_end=42,
                    target_accession="acc2", target_start=1, target_end=70
                ),
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=3, query_end=20,
                    target_accession="acc3", target_start=15, target_end=30
                ),
                # coordinates of this match on acc2 is outside of the acc2 region matched to acc1
                detected_row_fixture | dict(
                    query_accession="acc2", query_start=80, query_end=100,
                    target_accession="acc5", target_start=1, target_end=20
                )
            ])

            source = CSVSource(DetectedTable, tmpf)
            schema = Schema("schema")
            schema.add_table(source)

            results = recursive_project(Feature("acc1", "d", "protein"), schema, fuzz=0)

            results_to_detected_table(results, outf)
            with open(outf, "r") as f:
                received = f.read()

            expected = """
detection_type	detection_method	batch	query_accession	query_database	query_type	target_accession	target_database	target_type	query_start	query_end	target_start	target_end	evalue	bitscore	bitscore_threshold	custom_metric_name	custom_metric_value
sequence	hmm	foo	acc1	d	protein	acc2	d	protein	12	42	1	70					
sequence	hmm	foo	acc2	d	protein	acc3	d	protein	3	20	15	30
"""
            self.assertEqual(received.strip(), expected.strip())
