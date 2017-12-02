"""
This module provides various utilities for command line tools.
"""

import sys
import pydoc
import logging
import argparse
# from urllib.parse import urlencode
from twisted.web.resource import Resource
from twisted.web.resource import NoResource
# from twisted.web.wsgi import WSGIResource
# from twisted.web.server import Site
# from twisted.internet import reactor
from twisted.python.log import PythonLoggingObserver

import relevance


# Loggers
logging.basicConfig(stream=sys.stderr)
observer = PythonLoggingObserver()  # pylint: disable=invalid-name
observer.start()
logger = logging.getLogger('relevance')  # pylint: disable=invalid-name
logger.setLevel(logging.INFO)
logging.getLogger().setLevel(logging.ERROR)


class _RootResource(Resource):
    """
    Twisted root resource implementation.

    This class allows to bind a single twisted reactor to multiple WSGI applications.
    """
    def getChild(self, _, request):  # pylint: disable=arguments-differ
        """
        Get a child application.
        """
        name = request.prepath.pop().decode('ascii')
        return self.children.get(name, NoResource())


def _args_default(parser: argparse.ArgumentParser):
    """
    Add some default arguments to the parser.

    :param parser: the parser object.
    """
    parser.add_argument(
        '--version',
        help='show the version information',
        action='store_true',
    )
    parser.add_argument(
        '-q', '--quiet',
        help='only log warnings and errors',
        action='store_const',
        dest='verbosity',
        const=0,
    )
    parser.add_argument(
        '-qq',
        help='only log errors',
        action='store_const',
        dest='verbosity',
        const=-1,
    )
    parser.add_argument(
        '-v', '--verbose',
        help='enable verbose logging',
        action='store_const',
        dest='verbosity',
        const=1,
    )
    parser.add_argument(
        '-vv',
        help='enable extra verbose logging',
        action='store_const',
        dest='verbosity',
        const=2,
    )
    parser.add_argument(
        '-vvv',
        help='enable ultra verbose logging',
        action='store_const',
        dest='verbosity',
        const=3,
    )


def _args_handle(args: argparse.Namespace):
    """
    Handle some default arguments.

    :param args: the argument namepsace object.
    """
    if args.version:
        print('Relevance {0}'.format(relevance.__version__))
        sys.exit(0)

    # Configure the loggers
    if args.verbosity == -1:
        logger.setLevel(logging.ERROR)

    if args.verbosity == 0:
        logger.setLevel(logging.WARNING)

    if args.verbosity == 1:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.WARNING)

    if args.verbosity == 2:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.INFO)

    if args.verbosity == 3:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)


# def server():
#     """
#     Start one or more web application server.
#     """
#     parser = argparse.ArgumentParser(
#         prog='relevance-server',
#         description='Start Relevance web application server.',
#     )
#     parser.add_argument(
#         '-a',
#         help='set the applications to start',
#         metavar='MODULE:PATH',
#         nargs='+',
#         dest='apps',
#         default=['search'],
#     )
#     parser.add_argument(
#         '-s',
#         help='set the listener to use for the server',
#         metavar='ADDR:PORT',
#         default='0.0.0.0:5346',
#         dest='listen',
#     )
#     _args_default(parser)
#     args = parser.parse_args(sys.argv[1:])
#     _args_handle(args)
#
#     try:
#         logger.info('version {0}'.format(relevance.__version__))
#
#         # Add the selected applications
#         root = _RootResource()
#
#         for spec in args.apps:
#             parts = spec.split(':')
#
#             if len(parts) == 1:
#                 parts.append(parts[0])
#
#             if len(parts) != 2:
#                 raise argparse.ArgumentTypeError('invalid server spec')
#
#             module, path = parts
#             app_name = 'relevance.api.{0}.app'.format(module)
#
#             app = pydoc.locate(app_name)
#             if app is None:
#                 raise argparse.ArgumentTypeError('invalid application {0}'.format(module))
#
#             start_app(app)
#
#             if len(args.apps) > 1:
#                 resource = WSGIResource(reactor, reactor.getThreadPool(), app)
#                 root.putChild(path, resource)
#                 logger.info('binding module {0} to /{1}/'.format(
#                     module, path,
#                 ))
#             else:
#                 root = WSGIResource(reactor, reactor.getThreadPool(), app)
#                 logger.info('binding module {0} to /'.format(
#                     module,
#                 ))
#
#         # Setup the reactor
#         try:
#             addr, port = args.listen.split(':')
#             port = int(port)
#         except (ValueError, TypeError):
#             raise argparse.ArgumentTypeError('invalid listener spec')
#
#         logger.info('starting application server on {0}:{1}'.format(
#             addr, port,
#         ))
#         reactor.listenTCP(port, Site(root), interface=addr)
#         reactor.run()
#
#         print()
#         logger.info('server shutting down')
#
#     except argparse.ArgumentTypeError as e:
#         logger.critical('startup error: {0}'.format(
#             str(e),
#         ))
#         sys.exit(1)
#
#     except Exception as e:
#         logger.critical('{0}: {1}'.format(e.__class__.__name__, str(e)))
#         sys.exit(1)
#
#
# def search():
#     """
#     Perform a search.
#     """
#     from relevance.api import search as api
#
#     parser = argparse.ArgumentParser(
#         prog='relevance-search',
#         description='Perform a search request locally on a Relevance engine',
#     )
#     parser.add_argument(
#         'engine_name',
#         help='the name of the engine to query',
#         metavar='ENGINE_NAME',
#         nargs='?',
#     )
#     parser.add_argument(
#         'query',
#         help='the search request to execute',
#         metavar='QUERY',
#         nargs='?',
#         default='',
#     )
#     parser.add_argument(
#         '--list',
#         help='list the configured engines',
#         action='store_true',
#     )
#     _args_default(parser)
#     args = parser.parse_args()
#     _args_handle(args)
#
#     start_app(api.app)
#
#     try:
#         logger.info('version {0}'.format(relevance.__version__))
#
#         environ = {
#             'SERVER_NAME': 'localhost',
#             'SERVER_PORT': '0',
#             'REQUEST_METHOD': 'GET',
#             'QUERY_STRING': urlencode({'q': args.query}),
#             'wsgi.url_scheme': 'http',
#         }
#
#         with api.app.request_context(environ):
#             if args.list:
#                 response = api.get_config()
#                 print(response.data.decode('utf-8'))
#             else:
#                 if not args.engine_name:
#                     raise argparse.ArgumentTypeError('need to specify an engine name')
#
#                 response = api.do_search(args.engine_name)
#                 print(response.data.decode('utf-8'))
#
#     except argparse.ArgumentTypeError as e:
#         logger.critical('utility error: {0}'.format(
#             str(e),
#         ))
#         sys.exit(1)
#
#     except Exception as e:
#         logger.critical('{0}: {1}'.format(e.__class__.__name__, str(e)))
#         sys.exit(1)


def _main():
    """
    Master command line tool.
    """
    if '--version' in sys.argv:
        print('Relevance {0}'.format(relevance.__version__))
        sys.exit(0)

    try:
        prog = sys.argv.pop(1)
        if prog[0] == '_':
            raise TypeError()

        name = '{0}.{1}'.format(_main.__module__, prog)
        cmd = pydoc.locate(name)
        if cmd is None:
            raise TypeError()
    except (TypeError, IndexError):
        print('usage: relevance --version')
        # print('       relevance server [<options>]')
        # print('       relevance search [<options>]')
        sys.exit(1)
    cmd()


if __name__ == '__main__':
    _main()
