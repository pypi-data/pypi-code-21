#!python

# Python 2 and 3 compatibility
from __future__ import print_function
from builtins import map

import os
import sys
import argparse
import multiprocessing as mp

import pickle
import json


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--format", required=True, type=str,
                    help="Specify the format to convert the RTS log to. "
                    "Supported formats: yaml, json, pickle.")
parser.add_argument("files", nargs='*', help="Files to be converted.")
args = parser.parse_args()


def convertor(filename):
    base, extension = os.path.splitext(os.path.basename(filename))
    output = "%s.%s" % (base, args.format)

    # Read.
    with open(filename, 'r') as i:
        if extension.lower() == ".pickle":
            data = pickle.load(i)
        elif extension.lower() == ".yaml":
            data = yaml.load(i, Loader=SafeLoader)
        elif extension.lower() == ".json":
            data = json.load(i)
        else:
            print("File extension (%s) not supported!" % extension, file=sys.stderr)
            exit(1)

    # Write.
    with open(output, 'w') as i:
        if args.format == "pickle":
            pickle.dump(data, i, pickle.HIGHEST_PROTOCOL)
        elif args.format == "yaml":
            yaml.dump(data, stream=i, Dumper=Dumper)
        elif args.format == "json":
            json.dump(data, i, indent=4, separators=(',', ": "))


if __name__ == "__main__":
    if args.format == "yaml" or any(list(map(lambda x: os.path.splitext(x)[1].lower() == ".yaml", args.files))):
        try:
            import yaml
            from yaml import CSafeLoader as SafeLoader, CDumper as Dumper
        except ImportError:
            try:
                from yaml import SafeLoader, Dumper
                print("LibYAML not available - using pure Python implementation (slower).", file=sys.stderr)
            except ImportError:
                print("PyYAML not installed - YAML functionality unavailable.", file=sys.stderr)

    mp.Pool().map(convertor, args.files)
