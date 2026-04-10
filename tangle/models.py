import os
import re
import csv
import duckdb
from . import open_file_to_write, unique_batch


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
        errors = {}
        max_errors = 10

        def add_error(errcode, record_i):
            if errcode in errors:
                if len(errors[errcode]) < max_errors:
                    errors[errcode].append(record_i)
            else:
                errors[errcode] = [record_i]

        row_dicts = []
        for i,row in enumerate(rows):
            row_dict = row.copy()
            for column in self.columns:
                if column.required and column.name not in row_dict:
                    errcode = f"missing required field {column.name}"
                    add_error(errcode, i)

                if column.values and column.name in row_dict and row_dict[column.name] and row_dict[column.name] not in column.values:
                    values = ", ".join([f"'{x}'" for x in column.values])
                    errcode = f"{column.name} must be one of {values}"
                    add_error(errcode, i)

                if column.name in row_dict and row_dict[column.name] is not None and column.type is not str:
                    try:
                        row_dict[column.name] = column.type(str(row_dict[column.name]))
                    except:
                        errcode = f"{column.name} must be {column.type.__name__}"
                        add_error(errcode, i)

            row_dicts.append(row_dict)

        if errors:
            error_strings = \
              [f"{errcode}, in record{'s' if len(records) > 1 else ''} "+\
               f"{', '.join([str(x) for x in records])}{' (or more)' if len(records) >= max_errors else ''}" for errcode, records in errors.items()]
            raise Exception(f"Cannot insert into table {self.name}: {'; '.join(error_strings)}")
        return row_dicts

    def write_tsv(self, fn, rows, append = False):
        row_dicts = self.validate(rows)

        mode = "wt"
        if append is True:
            mode = "at"

        if not append or (not os.path.exists(fn) or os.path.getsize(fn) == 0):
            write_header = True
        else:
            write_header = False

        with open_file_to_write(fn, mode) as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames(), delimiter='\t', lineterminator='\n')
            if write_header:
                writer.writeheader()
            for row in row_dicts:
                writer.writerow(row)


class LocalTableSource(object):

    def __init__(self, table):
        self.table = table

    def table_name(self, schema):
        return f"{schema.name}.{self.table.name}"

    def duckdb_create_table_str(self, schema):
        return f"CREATE TABLE {self.table_name(schema)} AS SELECT * FROM {self.duckdb_source_str()}"


class CSVSource(LocalTableSource):

    def __init__(self, table, *paths):
        super(CSVSource, self).__init__(table)
        self.paths = paths

    def duckdb_source_str(self):
        paths = [f"'{x}'" for x in self.paths]
        return f"read_csv_auto([{','.join(paths)}], union_by_name=TRUE, normalize_names=TRUE)"

    def values(self, schema=None, column_filters=None, just=None):
        if schema is None:
            schema = Schema('__temp__'+unique_batch())
            schema.add_table(self)
            schema.duckdb_load()

        if column_filters:
            cond = f" WHERE {' AND '.join(column_filters)}"
        else:
            cond = ""

        if just is None:
            fields = "*"
        else:
            fields = just
        query = f"SELECT {fields} FROM {self.table_name(schema)}{cond}"

        values = duckdb.execute(query).fetchdf().to_dict('records')
        if just is None:
            return values
        else:
            return [v[just] for v in values]


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
            duckdb.execute(source.duckdb_create_table_str(self))
