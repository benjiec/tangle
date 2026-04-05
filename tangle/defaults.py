import argparse
import inspect
from tangle import open_file_to_read


class PathDefaultsBase(object):

    @staticmethod
    def main(cls):

        methods = {}
        for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            sig = inspect.signature(func)
            if len(sig.parameters) == 1:
                methods[name] = func

        parser = argparse.ArgumentParser(description="Get default paths")
        parser.add_argument("method", choices=methods.keys(), help="Method to execute")
        parser.add_argument("values", nargs='+', help="One or more values to pass to the method, each triggers one method call")
        parser.add_argument("-f", "--file", help="consider arguments as files that contain input values", action="store_true", default=False)

        args = parser.parse_args()
        target_func = methods[args.method]

        if args.file:
            input_values = []
            for fn in args.values:
                with open_file_to_read(fn) as f:
                    for line in f:
                        input_values.append(line.strip())
        else:
            input_values = args.values

        for val in input_values:
            result = target_func(val)
            print(result)
