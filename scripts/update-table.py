import shutil
import inspect
import importlib
from tangle.models import Table, CSVSource

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--table-name")
ap.add_argument("--forget-original", action="store_true", default=False)
ap.add_argument("module_file")
ap.add_argument("tsv_file")
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

source = CSVSource(table_obj, args.tsv_file)
rows = source.values()

if not args.forget_original:
    orig_fn = args.tsv_file+".orig"
    shutil.copy(args.tsv_file, orig_fn)

print(args.tsv_file, len(rows))
table_obj.write_tsv(args.tsv_file, rows)
