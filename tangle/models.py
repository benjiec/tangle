import re
import csv
import duckdb
from . import open_file_to_write


class Column(object):

    def __init__(self, name, values=None, required=False, type=None):
        if not re.match(r"^\w+$", name):
            raise Exception(f"'{name}' is not a valid column name")
        self.name = name
        self.type = type if type is not None else str
        self.values = values
        self.required = required


class Table(object):

    def __init__(self, name, columns):
        if not re.match(r"^\w+$", name):
            raise Exception(f"'{name}' is not a valid table name")
        self.name = name
        self.columns = columns

    def fieldnames(self):
        return [c.name for c in self.columns]

    def validate(self, rows):
        errors = []
        row_dicts = []
        for i,row in enumerate(rows):
            row_dict = row.copy()
            for column in self.columns:
                if column.required and column.name not in row_dict:
                    errors.append(f"record {i} - missing required field {column.name}")
                if column.values and column.name in row_dict and row_dict[column.name] and row_dict[column.name] not in column.values:
                    values = ", ".join([f"'{x}'" for x in column.values])
                    errors.append(f"record {i} - {column.name} must be one of {values}")
                if column.name in row_dict and column.type is not str:
                    try:
                        row_dict[column.name] = column.type(str(row_dict[column.name]))
                    except:
                        errors.append(f"record {i} - {column.name} must be {column.type.__name__}")
            row_dicts.append(row_dict)

        if errors:
            raise Exception(f"Cannot insert into table {self.name}: {', '.join(errors)}")
        return row_dicts

    def write_tsv(self, fn, rows, append = False):
        row_dicts = self.validate(rows)

        mode = "w"
        if append is True:
            mode = "a"

        with open_file_to_write(fn, mode) as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames(), delimiter='\t')
            if not append:
                writer.writeheader()
            for row in row_dicts:
                writer.writerow(row)


class LocalTableSource(object):

    def __init__(self, table):
        self.table = table

    def duckdb_create_table_str(self, schema):
        return f"CREATE TABLE {schema}.{self.table.name} AS SELECT * FROM {self.duckdb_source_str()}"


class CSVSource(LocalTableSource):

    def __init__(self, table, path):
        super(CSVSource, self).__init__(table)
        self.path = path

    def duckdb_source_str(self):
        return f"read_csv_auto('{self.path}', normalize_names=TRUE)"


class Schema(object):

    def __init__(self, name):
        if not re.match(r"^\w+$", name):
            raise Exception(f"'{name}' is not a valid table name")
        self.name = name
        self.table_sources = []

    def add_table(self, source):
        self.table_sources.append(source)

    def duckdb_load(self):
        duckdb.execute(f"DROP SCHEMA IF EXISTS {self.name} CASCADE")
        duckdb.execute(f"CREATE SCHEMA {self.name}")
        for source in self.table_sources:
            duckdb.execute(source.duckdb_create_table_str(self.name))
