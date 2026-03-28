import os
import duckdb
import unittest
import tempfile

from tangle.models import Column, Table, CSVSource, Schema


class TestWriteTSV(unittest.TestCase):

    def test_write_tsv_file(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            table = Table("test", [Column("a"), Column("b")])
            table.write_tsv(tmpf, [dict(a=1,b=2), dict(a=3,b=4)])

            f = open(tmpf, "r")
            self.assertEqual(f.read(), "a\tb\n1\t2\n3\t4\n")
            f.close()


    def test_append_to_tsv_file(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            table = Table("test", [Column("a"), Column("b")])
            table.write_tsv(tmpf, [dict(a=1,b=2), dict(a=3,b=4)])
            table.write_tsv(tmpf, [dict(a=5,b=6)], append=True)

            f = open(tmpf, "r")
            self.assertEqual(f.read(), "a\tb\n1\t2\n3\t4\n5\t6\n")
            f.close()


    def test_append_behaves_like_write_if_file_does_not_exist_or_empty(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            table = Table("test", [Column("a"), Column("b")])
            table.write_tsv(tmpf, [dict(a=1,b=2), dict(a=3,b=4)], append=True)

            f = open(tmpf, "r")
            self.assertEqual(f.read(), "a\tb\n1\t2\n3\t4\n")
            f.close()


    def test_loads_tsv_file_into_duckdb(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = os.path.join(tmpd, "test.tsv")

            table = Table("test", [Column("a"), Column("b")])
            table.write_tsv(tmpf, [dict(a=1,b=2), dict(a=3,b=4)])

            source = CSVSource(table, tmpf)
            schema = Schema("test_schema")
            schema.add_table(source)
            schema.duckdb_load()

            con = duckdb.connect(":default:")
            sql = "SELECT * FROM test_schema.test"
            data = con.sql(sql).fetchall()
            self.assertEqual(data, [(1,2), (3,4)])
            os.remove(tmpf)


class TestValidation(unittest.TestCase):
    
    def test_no_validation(self):
        table = Table("test", [
            Column("a"),
            Column("b")
        ])
        rows = [
            dict(a=1, b=2),
            dict(a=3, b=4)
        ]
        table.validate(rows)

    def test_required_field(self):
        table = Table("test", [
            Column("a"),
            Column("b"),
            Column("c", required=True),
        ])
        rows = [
            dict(a=1, b=2, c=3),
            dict(a=3, b=4)
        ]
        with self.assertRaisesRegex(Exception, "Cannot insert into table test: missing required field c, in record 1"):
            table.validate(rows)

    def test_required_field_value(self):
        table = Table("test", [
            Column("a"),
            Column("b"),
            Column("c", required=True, values=('x', 'y')),
        ])
        rows = [
            dict(a=1, b=2, c=3),
            dict(a=3, b=4, c='x')
        ]
        with self.assertRaisesRegex(Exception, "Cannot insert into table test: c must be one of 'x', 'y', in record 0"):
            table.validate(rows)

    def test_field_value_not_checked_if_not_required(self):
        table = Table("test", [
            Column("a"),
            Column("b"),
            Column("c", values=('x', 'y')),
        ])
        rows = [
            dict(a=1, b=2),
            dict(a=3, b=4, c='z')
        ]
        with self.assertRaisesRegex(Exception, "Cannot insert into table test: c must be one of 'x', 'y', in record 1"):
            table.validate(rows)

    def test_field_type(self):
        table = Table("test", [
            Column("a", type=int),
            Column("b", type=float),
        ])
        rows = [
            dict(a=1, b=2.2),
            dict(a="z", b="4"),
            dict(a=3.1, b="3"),
        ]
        with self.assertRaisesRegex(Exception, "Cannot insert into table test: a must be int, in records 1, 2"):
            table.validate(rows)
