"""
Sync entry point.

Sync attempts to read data from either a server (via JSON over HTTP) or a file (as YAML)
and write the same data to another (possibly the same) server or file.

"""
from argparse import ArgumentParser
from logging import basicConfig, DEBUG, ERROR, getLogger, INFO, WARN
import re

from microcosm_flask.sync.pull import pull
from microcosm_flask.sync.push import push
from microcosm_flask.sync.toposort import toposorted


def parse_args():
    parser = ArgumentParser()
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "--verbose",
        "-v",
        action="count",
        dest="verbosity",
        default=1,
        help="Set verbosity level",
    )
    verbosity_group.add_argument(
        "--quiet",
        "-q",
        action="store_const",
        const=0,
        dest="verbosity",
        help="Suppress verbosity",
    )
    follow_group = parser.add_mutually_exclusive_group()
    follow_group.add_argument(
        "--all",
        action="store_true",
        help="Traverse all links",
    )
    follow_group.add_argument(
        "--follow",
        action="append",
        help="Traverse links following one or more patterns",
    )
    parser.add_argument(
        "--exclude-first",
        "-x",
        action="store_true",
        help="Exclude the first resource from pull output",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=1,
        help="Batch size (requires backend PATCH support if >1)",
    )
    parser.add_argument(
        "--keep-instance-path",
        action="store_true",
        help="Keep the individual instance URI path when using the bulk import (PATCH) API. Used along with --batch-size.",  # noqa:E501
    )
    parser.add_argument(
        "--enable-sessions",
        action="store_true",
    )
    parser.add_argument(
        "input",
        help="Input location for resources",
    )
    parser.add_argument(
        "output",
        help="Output location for resources",
    )
    return parser.parse_args()


def set_relation_patterns(args):
    if args.all:
        patterns = [".*"]
    elif args.follow:
        patterns = args.follow
    else:
        patterns = ["search", "next"]

    args.relation_patterns = [
        re.compile(pattern) for pattern in patterns
    ]


def set_verbosity(args):
    verbosity = min(args.verbosity, 3)
    level = {0: ERROR, 1: WARN, 2: INFO, 3: DEBUG}.get(verbosity, WARN)
    basicConfig(level=level, format="%(name)s - %(message)s")
    getLogger("sync").setLevel(level)
    if verbosity < 3:
        getLogger("requests.packages.urllib3.connectionpool").setLevel(WARN)


def main():
    args = parse_args()
    set_relation_patterns(args)
    set_verbosity(args)
    data = pull(args)
    push(args, toposorted(data))
