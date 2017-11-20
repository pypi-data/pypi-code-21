#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from pyunitreport import HTMLTestRunner

from agent.worker.httprunner.task import TaskSuite


def api(testset_path, report_name=None, failfast=False):
    results = {}

    testset_path = testset_path.rstrip('/')

    task_suite = TaskSuite(testset_path)

    output_folder_name = '/Users/mafei/GT'
    kwargs = {
        "output": output_folder_name,
        "report_name": report_name,
        "failfast": failfast
    }
    result = HTMLTestRunner(**kwargs).run(task_suite)
    results[testset_path] = OrderedDict({
        "total": result.testsRun,
        "successes": len(result.successes),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped)
    })

    for task in task_suite.tasks:
        task.print_output()


if __name__ == '__main__':
    api('/Users/mafei/eleme.qa/HttpRunner/examples/quickstart-demo-rev-3.yml')
