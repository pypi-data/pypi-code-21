# coding: utf-8

import click
import signal
from deployv.base import errors
from deployv.helpers import utils, configuration


def signal_handler(signal_number, stack_frame):
    raise errors.GracefulExit(
        'Received a signal to terminate, stopping workers'
    )


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@click.command()
@click.option("-l", "--log_level", help="Log level to show", default='INFO')
@click.option("-h", "--log_file", help="Write log history to a file")
@click.option("-C", "--config", help="Additional .conf files.")
def run(log_level, log_file, config):
    utils.setup_deployv_logger(level=log_level, log_file=log_file)
    cfg = configuration.DeployvConfig(config)
    reader_p = []
    n_workers = int(cfg.config.get('deployer', 'workers'))
    worker_type = cfg.config.get('deployer', 'worker_type')

    module = __import__('deployv.messaging', fromlist=[str(worker_type)])
    if not hasattr(module, worker_type):
        raise ValueError
    msg_object = getattr(module, worker_type)
    config_class = msg_object.CONFIG_CLASSES['file']
    work_state = msg_object.factory(config_class(cfg, status=True), "Status")
    work_state.daemon = True
    work_state.start()
    reader_p.append(work_state)
    for nworker in range(n_workers):
        work = msg_object.factory(config_class(cfg), nworker)
        work.daemon = True
        work.start()
        reader_p.append(work)
    try:
        for aworker in reader_p:
            aworker.join()
    except (KeyboardInterrupt, errors.GracefulExit):
        for aworker in reader_p:
            aworker.signal_exit()
