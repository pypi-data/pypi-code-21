#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import multiprocessing
import os
import signal

import click

import agent
import agent.config as config
import agent.qualityplatform.api as server_api
from agent.consts import AgentStatus
# from agent.queue.worker import (
#     handle_macaca_task,
#     handle_androidmonkey_task,
#     handle_appcrawler_task,
#     handle_selenium_task,
#     handle_schedulers,
#     handle_crawler_task,
#     handle_iosmonkey_task
# )
from agent.server.api import start_server
from exc import GracefulExitException
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
agent_id = 0

scheduler = BackgroundScheduler()
logging.getLogger("apscheduler").setLevel(logging.ERROR)


def output_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version: %s" % agent.__version__)
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
def parse_command(environment):
    config.qualityplatform['api_url'] = config.qualityplatform_env_api_url.get(environment)
    config.sentry_url['url'] = config.sentry_env_url.get(environment)
    print(config.sentry_url.get('url'))
    config.agent['port'] = config.agent_env_port.get(environment)
    start_agent_client()


def check_devices(status):
    return server_api.register_agent(status)


def check_devices_cron():
    server_api.register_agent(AgentStatus.online.value)


def signal_handler(signum, frame):
    server_api.unregister_agent(config.agent['agent_id'])
    raise GracefulExitException()


class GracefulExitEvent(object):
    def __init__(self, num_workers):
        self.exit_event = multiprocessing.Event()
        pass

    def is_stop(self):
        return self.exit_event.is_set()

    def notify_stop(self):
        self.exit_event.set()


def start_agent_client():
    agent_data = check_devices(AgentStatus.online.value)
    if agent_data:
        config.agent['agent_id'] = agent_data.get('id')
    signal.signal(signal.SIGINT, signal_handler)
    scheduler.add_job(check_devices_cron, 'interval', seconds=15)
    scheduler.start()
    start_server()
    # gee = GracefulExitEvent(1)
    # workers = []
    # p1 = multiprocessing.Process(target=start_server)
    # p1.daemon = True
    # p2 = multiprocessing.Process(target=handle_macaca_task)
    # p2.daemon = True
    # p3 = multiprocessing.Process(target=handle_selenium_task)
    # p3.daemon = True
    # p4 = multiprocessing.Process(target=handle_appcrawler_task)
    # p4.daemon = True
    # p5 = multiprocessing.Process(target=handle_androidmonkey_task)
    # p5.daemon = True
    # p6 = multiprocessing.Process(target=handle_schedulers)
    # p6.daemon = True
    # p8 = multiprocessing.Process(target=handle_crawler_task)
    # p8.daemon = True
    # p9 = multiprocessing.Process(target=handle_iosmonkey_task)
    # p9.daemon = True
    # p1.start()
    # workers.append(p1)
    # p2.start()
    # workers.append(p2)
    # p3.start()
    # workers.append(p3)
    # p4.start()
    # workers.append(p4)
    # p5.start()
    # workers.append(p5)
    # p6.start()
    # workers.append(p6)
    # p8.start()
    # workers.append(p8)
    # p9.start()
    # workers.append(p9)
    # try:
    #     for wp in workers:
    #         wp.join()
    # except GracefulExitException:
    #     print "main process(%d) got GracefulExitException" % os.getpid()
    #     gee.notify_stop()
    #     for worker in workers:
    #         worker.terminate()


def main():
    print("A Terminal Tools For agent Agent")
    parse_command()


if __name__ == "__main__":
    main()
