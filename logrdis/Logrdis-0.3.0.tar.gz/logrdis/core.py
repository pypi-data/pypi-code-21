import logging
import os
import re
from urllib.parse import urlparse
import click
from .config import parse
from .db import Adapter
from .socket import SocketServer
from .util import wait_for

LOGGER = logging.getLogger(__name__)

# Create thread pool, each worker consumes from a queue
# Each worker is configured for sql; queue passes socket/address tuples

@click.command()
@click.option('--config', '-c', default='/etc/logrdis/logrdis.yml', help='logrdis configuration directives; this file defaults to /etc/logrdis/logrdis.yml')
def run_log_server(config):
    """Entry point function.

    :param config_path: str. a filepath to the YAML configuration directive
    :raises: OSError, KeyError
    """
    if not os.path.exists(config):
        raise OSError('{} does not exist'.format(config))
    config_directives = parse(config)

    if not 'engine' in config_directives:
        raise KeyError('engine not defined in configuration')

    # Wait for db server if one is configured
    parsed = urlparse(config_directives['engine'])
    ip_addr = parsed.hostname
    port = parsed.port
    LOGGER.info('Waiting for {}:{} to be ready'.format(ip_addr, port))
    wait_for(ip_addr, port, config_directives['db_timeout'])

    sql = Adapter(config_directives['engine'])
    for process, directives in config_directives['process'].items():
        if directives['action'] == 'store':
            if 'pk' not in directives:
                directives['pk'] = "_id"
            if 'tablename' not in directives:
                raise KeyError('No tablename field declared in process config')
            if 'schema' not in directives:
                raise KeyError('No schema field declared in process config')
                raise KeyError('No pk field declared in process config')
            sql.declare(directives['tablename'], directives['pk'], directives['schema'])
            LOGGER.info('Stored directive {}'.format(directives['tablename']))

    socket_server = SocketServer()
    socket_server.run_forever(config_directives, sql)

    LOGGER.info('Exiting')