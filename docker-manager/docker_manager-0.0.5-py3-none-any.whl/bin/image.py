#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import sys
import argcomplete
import argparse


# create parser in order to autocomplete
parser = argparse.ArgumentParser()

parser.add_argument(
    '-t', "--type",
    help="What type of servers you want to import?",
    type=str,
    choices=['ftp', 'iomega'],
    required=True
)
parser.add_argument(
    "--from",
    help="Whats the source of your data?",
    type=str,
    choices=['shodan'],
    required=True
)


parser.add_argument(
    "--file",
    help="Where is the file you want to import?",
    type=str,
    required=True
)
argcomplete.autocomplete(parser)



def main():
  print("docker-image manager")

  arguments = parser.parse_args()
  pprint(arguments)

