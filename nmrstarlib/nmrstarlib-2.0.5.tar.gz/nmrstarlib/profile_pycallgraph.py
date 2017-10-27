#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from . import nmrstarlib


if __name__ == "__main__":
    # python3 -m nmrstarlib.profile_pycallgraph 18569

    source = sys.argv[-1]
    starfile_generator = nmrstarlib.read_files(source)

    with PyCallGraph(output=GraphvizOutput()):
        next(starfile_generator)
