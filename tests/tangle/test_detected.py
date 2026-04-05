import unittest

from tangle.detected import DetectedTable

class TestDetectedTable(unittest.TestCase):

    def test_table_defined_without_syntax_error(self):
        self.assertEqual(DetectedTable.name, "detected")
