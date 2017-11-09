import argparse
import collections
from pprint import pprint

import attr

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    return parser

args = create_parser().parse_args()

key_map = collections.defaultdict(lambda: collections.defaultdict(int))

with open(args.file) as f:
    for line in (line.strip() for line in f):
        if not line.endswith("]delim"):
            continue

        line = line.lstrip("delim[").rstrip("]delim")
        op, key = (v.strip() for v in line.split(":")[-2:])
        key_map[key][op] += 1


pprint({k: dict(v) for k, v in key_map.items()
        if not v['pop-start'] == v['pop-stop']})
