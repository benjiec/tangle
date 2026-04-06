import inspect
import argparse
import functools
from pathlib import Path
from tangle import open_file_to_read


class PathDefaultsBase(object):

    @staticmethod
    def main(cls):

        methods = {}
        for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            sig = inspect.signature(func)
            if len(sig.parameters) <= 1:
                methods[name] = func

        parser = argparse.ArgumentParser(description="Get default paths")
        parser.add_argument("-m", "--method", action="append", choices=methods.keys(), help="Method to execute")
        parser.add_argument("values", nargs='*', help="Zero or more values to pass to the method, each triggers one method call")
        parser.add_argument("-f", "--file", help="consider arguments as files that contain input values", action="store_true", default=False)

        args = parser.parse_args()

        if args.file:
            input_values = []
            for fn in args.values:
                with open_file_to_read(fn) as f:
                    for line in f:
                        input_values.append(line.strip())
        else:
            input_values = args.values

        for method in args.method:
            target_func = methods[method]
            if len(input_values) == 0:
                p = target_func()
                if p: print(p)
            for val in input_values:
                p = target_func(val)
                if p: print(p)


def validate_path_exists(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            return
        if Path(result).exists():
            return result
        return
    return wrapper
