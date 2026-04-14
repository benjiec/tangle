import sys
import json
import inspect
import importlib
from tangle import open_file_to_read
from tangle.models import Table

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("module_file")
ap.add_argument("--table-name")
ap.add_argument("--check")
args = ap.parse_args()

table_module = importlib.import_module(args.module_file)

if args.table_name:
    table_obj = getattr(table_module, args.table_name)
else:
    matches = [
        obj for name, obj in inspect.getmembers(table_module)
          if isinstance(obj, Table)
    ]
    if not matches:
        raise Exception(f"no Table subclass found in {args.module_file}")
    if len(matches) > 1:
        raise Exception(f"multiple Table subclasses found in {args.module_file}")
    table_obj = matches[0]

schema_data = table_obj.bigquery_schema()

if args.check:
    with open_file_to_read(args.check) as f:
        first_line = f.readline()
    headers = first_line.strip('\n').split('\t')
    if headers != [x["name"] for x in schema_data]:
        raise Exception(f"Headers from TSV {args.check} does not match schema")

print(json.dumps(schema_data, indent=2))
