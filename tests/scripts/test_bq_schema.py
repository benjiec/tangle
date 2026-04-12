import os
import json
import unittest
import subprocess

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
