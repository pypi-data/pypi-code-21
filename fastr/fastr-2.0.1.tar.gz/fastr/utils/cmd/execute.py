#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import fastr
import fastr.execution.executionscript
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(description="Execute a job from commandline.")
    parser.add_argument('job', metavar='JOBFILE', nargs='?', type=str,
                        help='File of the job to execute (default ./__fastr_command__.pickle.gz)')
    return parser


def main():
    """
    Execute a fastr job file
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    if args.job is not None:
        job = args.job
    else:
        curdir_contents = os.listdir('.')

        if '__fastr_command__.pickle.gz' in curdir_contents:
            job = '__fastr_command__.pickle.gz'
        else:
            fastr.log.critical('No job given and cannot find __fastr_command__.pickle.gz in current directory!')
            exit()

    fastr.execution.executionscript.main(job)


if __name__ == '__main__':
    main()
