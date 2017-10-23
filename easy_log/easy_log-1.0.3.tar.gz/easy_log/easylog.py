#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("echo")
args = parser.parse_args()

def easylog():
    print args.echo


def test(*args):
    print args[0]