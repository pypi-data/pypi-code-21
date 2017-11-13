#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import mwtab


if __name__ == "__main__":
    # python3 -m mwtab.profile_pycallgraph 1

    source = sys.argv[-1]
    mwtabfile_generator = mwtab.read_files(source)

    with PyCallGraph(output=GraphvizOutput()):
        next(mwtabfile_generator)
