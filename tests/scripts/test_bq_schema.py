import os
import json
import tempfile
import unittest
import subprocess
from pathlib import Path
from tangle.detected import DetectedTable


class TestBigQuerySchema(unittest.TestCase):

    def test_can_retrieve_schema_from_table(self):
        cmd = ["python3", "scripts/bq-schema.py", "tangle.detected", "--table-name", "DetectedTable"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        schema = json.loads(result.stdout)
        self.assertEqual("query_accession" in [x["name"] for x in schema], True)

    def test_can_retrieve_schema_without_table_name(self):
        cmd = ["python3", "scripts/bq-schema.py", "tangle.detected", "--table-name", "DetectedTable"]
        result1 = subprocess.run(cmd, check=True, capture_output=True, text=True)
        schema1 = json.loads(result1.stdout)

        cmd = ["python3", "scripts/bq-schema.py", "tangle.detected"]
        result2 = subprocess.run(cmd, check=True, capture_output=True, text=True)
        schema2 = json.loads(result2.stdout)

        self.assertEqual(schema1, schema2)

    def test_can_check_if_tsv_matches_schema(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            in_tsv = temp_dir / "in.tsv"

            with open(in_tsv, "w") as f:
                f.write("a\tb\tc\n")        

            # this should work
            cmd = ["python3", "scripts/bq-schema.py", "tangle.detected", "--table-name", "DetectedTable"]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # this should fail
            with self.assertRaises(subprocess.CalledProcessError):
                cmd = ["python3", "scripts/bq-schema.py", "tangle.detected", "--table-name", "DetectedTable", "--check", in_tsv]
                res = subprocess.run(cmd, check=True, capture_output=True, text=True)

            schema = DetectedTable.bigquery_schema()
            headers = [x["name"] for x in schema]
            with open(in_tsv, "w") as f:
                f.write("\t".join(headers)+"\n")

            cmd = ["python3", "scripts/bq-schema.py", "tangle.detected", "--table-name", "DetectedTable", "--check", in_tsv]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
