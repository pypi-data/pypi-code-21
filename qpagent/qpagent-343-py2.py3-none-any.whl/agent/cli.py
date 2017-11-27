#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.cli
    ~~~~~~~~~~~~

    This module is the main of agent.

    :copyright: (c) 2017 by Ma Fei.
"""
import argparse
import logging
import os
import signal
from collections import OrderedDict

import click
from apscheduler.schedulers.background import BackgroundScheduler
from pyunitreport import HTMLTestRunner
from pyunitreport import __version__ as pyu_version

import agent
import agent.config as config
from agent.consts import AgentStatus
from agent.exc import GracefulExitException, TestcaseNotFound
from agent.qualityplatform import server_api
from agent.server.api import start_server, stop_server
from agent.util.sentry import Sentry
from agent.worker.httprunner.task import TaskSuite

logger = logging.getLogger(__name__)

sentry = Sentry()

scheduler = BackgroundScheduler()
logging.getLogger("apscheduler").setLevel(logging.ERROR)


def output_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version: {}".format(agent.__version__))
    click.echo("PyUnitReport version: {}".format(pyu_version))
    ctx.exit()


@click.command()
@click.option(
    '-v',
    '--version',
    is_flag=True,
    is_eager=True,
    callback=output_version,
    expose_value=False,
    help="show the version of this tool")
@click.option(
    '-e',
    '--environment',
    default='prod',
    help='select a development environment such as alpha|beta|prod')
@click.option(
    '-l',
    '--log',
    default='INFO',
    help='Specify logging level, default is INFO')
def parse_command(environment, log):
    log_level = getattr(logging, log.upper())
    logging.basicConfig(level=log_level)

    config.qualityplatform['api_url'] = config.qualityplatform_env_api_url.get(environment)
    config.sentry_url['url'] = config.sentry_env_url.get(environment)
    logger.info(config.sentry_url.get('url'))
    config.agent['port'] = config.agent_env_port.get(environment)
    start_agent_client()


def check_devices_cron():
    server_api.register_agent(AgentStatus.online.value)


def signal_handler(signum, frame):
    server_api.unregister_agent(config.agent['agent_id'])
    stop_server()
    scheduler.shutdown()
    logger.info("main process(%d) got GracefulExitException" % os.getpid())
    os._exit(0)


def start_agent_client():
    agent_data = server_api.register_agent(AgentStatus.online.value)
    if agent_data:
        config.agent['agent_id'] = agent_data.get('id')
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        scheduler.add_job(check_devices_cron, 'interval', seconds=15)
        scheduler.start()
        start_server()
    except GracefulExitException:
        sentry.client.captureException()


def main():
    print("A Terminal Tools For agent Agent")
    parse_command()


def main_ate():
    """ API test: parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(
        description='HTTP test runner, not just about api test and load test.')
    parser.add_argument(
        '-V', '--version', dest='version', action='store_true',
        help="show version")
    parser.add_argument(
        'testset_paths', nargs='*',
        help="testset file path")
    parser.add_argument(
        '--log-level', default='INFO',
        help="Specify logging level, default is INFO.")
    parser.add_argument(
        '--report-name',
        help="Specify report name, default is generated time.")
    parser.add_argument(
        '--failfast', action='store_true', default=False,
        help="Stop the test run on the first error or failure.")
    parser.add_argument(
        '--startproject',
        help="Specify new project name.")

    args = parser.parse_args()

    report_name = args.report_name
    if report_name and len(args.testset_paths) > 1:
        report_name = None
        logging.warning("More than one testset paths specified, \
                        report name is ignored, use generated time instead.")

    results = {}
    success = True

    for testset_path in set(args.testset_paths):

        testset_path = testset_path.rstrip('/')

        try:
            task_suite = TaskSuite(testset_path)
        except TestcaseNotFound:
            success = False
            continue

        output_folder_name = os.path.basename(os.path.splitext(testset_path)[0])
        kwargs = {
            "output": output_folder_name,
            "report_name": report_name,
            "failfast": args.failfast
        }
        result = HTMLTestRunner(**kwargs).run(task_suite)
        results[testset_path] = OrderedDict({
            "total": result.testsRun,
            "successes": len(result.successes),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped)
        })

        if len(result.successes) != result.testsRun:
            success = False

        for task in task_suite.tasks:
            task.print_output()

    return 0 if success is True else 1


if __name__ == "__main__":
    main()
