# -*- coding: utf-8 -*-
import logging
import sys

import click
import click_log

from .router import StreamRouter
from .telnet import TelnetServer

__version__ = '0.0.16'

logger = logging.getLogger(__name__)


@click.group()
@click_log.init(__name__)
def cli():
    pass


@cli.command()
@click.option('--source', '-s', 'sources', type=int, multiple=True, required=True,
              help='The source ports for incoming connections. Can (and likely will) be given multiple times')
@click.option('--output', '-o', 'outputs', multiple=True, required=True,
              help='Destinations to route to, in the form of: tcp://<hostnam>:<port>. Can be given multiple times')
@click.option('--delay', '-d', default=0.5,
              help='Delay until to fallback to secondary streams')
@click.option('--audio-threshold', '-a', default=-90,
              help='Minimum audio level (range [-90..0] dB) for input to be considered ok. Set to -90 to disable level detection')
@click.option('--telnet', '-t', required=False,
              help='Add telnet interface: <bind addr>:<port> or <port> (if only port is given interface will bind to 127.0.0.1)')
def run(sources, outputs, delay, telnet, audio_threshold):
    logger.info('Source ports: %s' % ', '.join(map(str, sources)))
    logger.info('Destinations: %s' % ', '.join(outputs))
    logger.info('Telnet Interface: %s' % telnet)

    while True:

        r = StreamRouter(sources, outputs, delay, audio_threshold)

        # adding telnet interface
        if telnet:
            _t = TelnetServer(router=r)

            if telnet.isdigit():
                _t.bind(port=int(telnet), address='127.0.0.1')
            else:
                _address, _port = telnet.split(':')
                _t.bind(port=int(_port), address=_address)

            r._telnet_server = _t

        try:
            r.connect()
            r.run()
        except KeyboardInterrupt:
            logger.info('Ctrl-c received! Stop router')
            r.stop()
            sys.exit()
