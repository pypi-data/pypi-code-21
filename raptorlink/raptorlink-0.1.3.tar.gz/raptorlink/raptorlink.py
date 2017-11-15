#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time
import nose
import json
import shutil
import datetime
import json
import traceback

from os.path import join, exists


RESULT_CODE = {'pass': 0, 'fail': 1, 'error': 2}


def _formatOutput(err):
    out_str = 'NA'
    exception_text = traceback.format_exception(*err)
    if exception_text and len(exception_text):
        out_str = ''.join(exception_text)
    return out_str


def _test_result_output(raptor_prefix, test_case, case_start, result, trace):
    module_name, class_name, method_name = test_case.id().split('.')[-3:]
    case_result = {'task_id': None,
                   'module': module_name,
                   'case_name': method_name,
                   'case_desc': test_case.shortDescription() or str(test_case),
                   'cycle': 1,
                   'test_cycle': 1,
                   'case_num': 1,
                   'total_times': '0',
                   'result': RESULT_CODE[result],
                   'beg_time': case_start,
                   'end_time': int(time.time()),
                   'image': 'NA',
                   'trace_back': trace,
                   'logpath': 'NA',
                   'run_log': 'NA',
                   'acterror': 'NA'
                   }
    sys.stdout.write(raptor_prefix + json.dumps(case_result,
                                                ensure_ascii=False) + '\n')


class RaptorPlugin(nose.plugins.Plugin):
    """
    write test result to $WORKSPACE/result.txt or ./result.txt
    """
    enabled = False
    name = 'raptor-link'

    def options(self, parser, env):
        """
        Register commandline options.
        Called to allow plugin to register command line options with the parser. DO NOT return a value from this method unless you want to stop all other plugins from setting their options.        
        """
        super(RaptorPlugin, self).options(parser, env)

        parser.add_option('--raptor-report', action='store_true',
                          dest='report_enable', default=False,
                          help="whether submit the test result to raptor server")
        parser.add_option('--raptor-prefix', action='store',
                          dest='raptor_prefix', default='#utyyfkfuyd9784521hkjojfnvcynsf46764oiu9872908iojkafkd#',
                          help="provide the token for accessing raptor server")

    def configure(self, options, conf):
        """
        Called after the command  line has been parsed, with the parsed options and the config container. Here, implement any config storage or changes to state or operation that are set by command line options. DO NOT return a value from this method unless you want to stop all other plugins from being configured.
        """
        super(RaptorPlugin, self).configure(options, conf)
        self.conf = conf
        self.opt = options
        if options.report_enable:
            self.enabled = True
        self.raptor_prefix = options.raptor_prefix

    def beforeTest(self, test):
        self.case_start_time = int(time.time())

    # remote upload
    def addFailure(self, test, err, capt=None, tbinfo=None):
        _test_result_output(self.raptor_prefix, test, self.case_start_time,
                            'fail', _formatOutput(err))

    # remote upload
    def addError(self, test, err, capt=None):
        _test_result_output(self.raptor_prefix, test, self.case_start_time,
                            'error', _formatOutput(err))

    # remote upload
    def addSuccess(self, test, capt=None):
        _test_result_output(self.raptor_prefix, test,
                            self.case_start_time, 'pass', '')
