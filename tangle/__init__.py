import sys
import gzip
from contextlib import contextmanager

@contextmanager
def open_file_to_read(fn):
    if fn == "-":
        yield sys.stdin
    else:
        with open(fn, 'rb') as test_f:
            is_gz = test_f.read(2) == b'\x1f\x8b'
        opener = gzip.open if is_gz else open
        with opener(fn, "rt", encoding="utf-8") as f:
            yield f

@contextmanager
def open_file_to_write(fn, mode):
    if fn == "-":
        yield sys.stdin
    else:
        is_gz = fn.endswith(".gz")
        opener = gzip.open if is_gz else open
        with opener(fn, mode, encoding="utf-8") as f:
            yield f
