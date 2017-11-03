#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import argparse
import json
import logging
import os
import re
import sys
import yaml

logger = logging.getLogger(__name__)

PARSER = argparse.ArgumentParser(
    description='Dump environment variables into configuration file'
)
PARSER.add_argument(
    '--prefix', help="Regular expression to filter variables names"
)
PARSER.add_argument(
    '--verbose', action='store_const', const=True, help="Increase verbosity"
)
PARSER.add_argument(
    'format', choices=['ini', 'json', 'yaml'], help="Output format"
)
PARSER.add_argument('file', metavar='FILE', help="Output configuration file")


def load_envs(prefix=None):
    result = dict()
    if prefix:
        logger.debug("Filter is set ({}*)".format(prefix))
    for key, value in os.environ.items():
        if prefix:
            if re.match(prefix, key):
                result[key] = value
        else:
            result[key] = value
    return result


def dump_to_file(filename, fmt, data):
    """"""
    logger.debug("{} format will be used".format(fmt.upper()))
    with open(filename, "w") as hfile:
        if fmt == 'ini':
            hfile.write("[default]\n")
            hfile.writelines(sorted(
                ["{} = \"{}\"\n".format(*r) for r in data.items()]
            ))

        elif fmt == "json":
            json.dump(
                data, hfile, sort_keys=True, indent=4, separators=(',', ': ')
            )
        elif fmt == "yaml":
            yaml.dump(data, hfile, default_flow_style=False)
        else:
            raise ValueError("Invalid format: {}".format(fmt))

    logger.info("{} wrote".format(filename))


def main():
    ns = PARSER.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if ns.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s"
    )
    try:
        dump_to_file(ns.file, ns.format, load_envs(ns.prefix))
    except Exception as exc:
        logger.critical("Fatal error: {}".format(exc))
        sys.exit(1)
