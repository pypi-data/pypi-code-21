#!/usr/bin/env python2.7

import argparse

parser = argparse.ArgumentParser()
top_subparsers = parser.add_subparsers(help='types of A')
# parser.add_argument("-v")

dss_parser = top_subparsers.add_parser("dss")
dss_subparsers = dss_parser.add_subparsers(help="dss subparsers help")
get_head_parser = dss_subparsers.add_parser("get_head")
get_head_parser.add_argument("something")
get_head_parser.add_argument("else")

stage_parser = top_subparsers.add_parser("stage")
stage_parser.add_argument("command")

args = parser.parse_args()
