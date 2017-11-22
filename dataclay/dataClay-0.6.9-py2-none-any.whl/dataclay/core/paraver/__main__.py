"""Entry point for the utils application related to the Paraver tracing.

This module can be run as a standalone and expects a series of parameters for
performing some work. Check the usage of argparse in this submodule.
"""

import argparse

import yaml
import os.path

from . import merger


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


def do_merge(ns):
    with open(os.path.join(ns.input_path, "merge-config.yaml")) as f:
        config = yaml.safe_load(f)

    merger.main(config, ns.output_path, ns.verify)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Paraver-related dataClay utilities.',
                                     prog='dataclay.paraver')
    subparsers = parser.add_subparsers()

    # Merge
    p_merge = subparsers.add_parser('merge')
    p_merge.add_argument("--input-path", required=True,
                         help="Path with the prv files and the merge configuration (merge-config.yaml)")
    p_merge.add_argument("--output-path", required=True,
                         help="Result of the merge process (merge.pcf, merge.prv and merge.row files will be created)")
    p_merge.add_argument("-v", "--verify", action="store_true",
                         help="Perform an extra verification on the integrity of input files")
    p_merge.set_defaults(func=do_merge)

    # Do the parsing and call the appropriate function
    args = parser.parse_args()
    args.func(args)
