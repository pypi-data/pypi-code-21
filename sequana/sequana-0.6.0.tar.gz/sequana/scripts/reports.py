# coding: utf-8
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
import os
import shutil
import glob
import sys
import argparse
import re
import json

import pandas as pd

from sequana.utils import config
from sequana import logger


class Options(argparse.ArgumentParser):
    def __init__(self, prog="sequana_reports"):
        usage = """Welcome to SEQUANA - Reports generator

sequana_reports --input-files variants.vcf --output-directory report/

AUTHORS: Thomas Cokelaer, Dimitri Desvillechabrol
Documentation: http://sequana.readthedocs.io
Issues: http://github.com/sequana/sequana
        """
        description = """DESCRIPTION:

        Create HTML reports for differents results files.

        You can analyse these differents files:

            - csv from sequana_coverage
            - vcf from freebayes
        """
        super().__init__(usage=usage, prog=prog, description=description)

        # Options to create all requested report and generated
        group = self.add_argument_group("Required arguments")
        group.add_argument(
            '-d', '--input-directory', type=str, dest='input_dir', help=(
            "Search for CSV and JSON files in the directory. It creates a "
            "report directory with a summary.html as main page."))
        group.add_argument('-i', '--input-files', type=str, nargs='*',
                           dest='input_files',
                           help="All CSV and JSON files produce by sequana")
        group.add_argument('-o', '--output-directory', type=str,
                           dest='output_dir', default='report',
                           help="Name of the output (report) directory")
        group = self.add_argument_group("General options")
        group.add_argument('--version', dest='version', action='store_true',
                           help="Print version of sequana")
        group.add_argument('-v', '--verbose', dest='verbose',
                           action='store_true', help="Display logs")
        group = self.add_argument_group("Optionnal options")
        group.add_argument('-n', '--name', type=str, dest='sample_name',
                           help="Name of your sample.")


def main(args=None):
    if args is None:
        args = sys.argv[:]

    user_options = Options(prog='sequana_report')

    # If --help or no options provided, show the help
    if len(args) == 1:
        user_options.parse_args(['prog', '--help'])
    else:
        options = user_options.parse_args(args[1:])
    config.output_dir = options.output_dir

    # list of all target files (csv or json) in input_dir
    if options.input_dir:
        input_files = [f for p in ('**/*.csv', '**/*.json') for f in
                       glob.glob(os.sep.join([options.input_dir, p]),
                       recursive=True)]
    elif options.input_files:
        input_files = options.input_files
    else:
        user_options.parse_args(['prog', '--help'])

    # set the sample name of the report
    if options.sample_name:
        config.sample_name = options.sample_name
    else:
        config.sample_name = os.path.basename(input_files[0]).split('.')[0]

    re_sequana = re.compile("sequana_\w+")
    for f in input_files:
        tool = None
        # get tools to retrieve module
        with open(f, 'r') as fp:
            logger.info("Found {}".format(f))
            if f.endswith('json'):
                data = json.load(fp)
                try:
                    tool = data['tool']
                except KeyError:
                    pass
            else:
                line = fp.readline()
                search_re = re_sequana.search(line)
                if search_re:
                    tool = search_re.group(0)
                    data = f
        # load and execute module
        if not tool:
            continue
        elif tool == 'sequana_summary':
            summary_json = data
        else:
            mod = config.module_dict[tool].load()
            mod(data)
    # summary.html may need custom section from other modules
    mod = config.module_dict['sequana_summary'].load()
    try:
        mod(summary_json)
    except NameError:
        pass


if __name__ == '__main__':
    main()
