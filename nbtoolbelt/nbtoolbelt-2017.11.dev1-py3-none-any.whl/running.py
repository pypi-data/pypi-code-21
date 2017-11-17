"""
Functions for running

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.
"""

import sys
from argparse import Namespace
from nbformat import NotebookNode
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from .cleaning import clean_code_output, clean_code_metadata, truncate_output_streams

TEST = False


def run_nb(nb: NotebookNode, args: Namespace) -> None:
    """Run notebook.

    .. note:: **Modifies**: ``nb``

    :param nb: notebook to run
    :param args: arguments (options)
    """
    # clean up before execution
    if args.clean_before:
        clean_code_output(nb)

    if args.append_cell:
        nb.cells.append(nbformat.v4.new_code_cell(args.appended_cell))

    # run notebook
    ep = ExecutePreprocessor(
        timeout=args.timeout,
        kernel_name=args.kernel_name,
        allow_errors=args.allow_errors,
        interrupt_on_timeout=args.interrupt_on_timeout
    )
    try:
        resources = {'metadata': {'path': args.run_path}}  # set working directory
        _ = ep.preprocess(nb, resources)  # nb is executed in-place, locally
    except CellExecutionError as e:  # only possible if not args.allow_errors
        if getattr(args, 'assert'):  # args.assert gives syntax error
            raise
        else:
            print('{}: {}'.format(type(e).__name__, e), file=sys.stderr)
    finally:
        # clean up after execution
        if args.clean_after:
            clean_code_metadata(nb, args)

        if args.streams_head >= 0:
            truncate_output_streams(nb, args)
