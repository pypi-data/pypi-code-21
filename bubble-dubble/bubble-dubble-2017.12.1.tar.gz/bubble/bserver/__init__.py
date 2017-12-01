#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import argparse
from ..bcommon import utils
from .config import Config


def main():
    parser = argparse.ArgumentParser(description='Bubble server integrator',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('port', nargs='?', help='Port to listen', type=int, default=Config.Port)
    args = parser.parse_args()
    Config.set(args)
    loop = asyncio.get_event_loop()
    from .server import BubbleProtocol
    coro = loop.create_server(BubbleProtocol, '0.0.0.0', args.port)
    server = loop.run_until_complete(coro)
    print(f'Bubble server integrator {utils.get_version()}, '
          f'(c) Vadim Dyadkin 2014-2017, ESRF, inspired by Giuseppe Portale')
    print('If you use this program, please cite this paper: http://dx.doi.org/10.1107/S1600577516002411')
    print('Official web page: http://soft.snbl.eu/bubble.html')
    print('Mercurial repository: http://hg.3lp.cx/bubble')
    print(f'Mercurial hash: {utils.get_hg_hash()}')
    print('Serving on {}:{:d}'.format(*server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Ctrl-C has been pressed. Exit and clean up...')
    # it should be a 'finally' section here, but then we have to close the PeriodicTask properly.
    # It needs a refactoring before we put it in motion.
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
