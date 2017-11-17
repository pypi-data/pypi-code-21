"""Sub-command that hosts the output directory of the publisher as a web server."""
import pathlib
import urllib
from http.server import HTTPServer, SimpleHTTPRequestHandler

import os
import posixpath

from autology.configuration import get_configuration


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('serve', help='Serve the contents of the publishers output files')
    parser.set_defaults(func=_main)

    parser.add_argument('--port', '-p', type=int, help='Port that the server will be listening on',
                        default=8080)


def _main(args):
    """Instantiate the server and start hosting files."""
    server_address = ('localhost', args.port)
    httpd = HTTPServer(server_address, _RequestHandler)

    print('Now listening on http://localhost:{}/'.format(args.port))

    httpd.serve_forever()


class _RequestHandler(SimpleHTTPRequestHandler):
    """Request handler that overrides translate path to provide the path of the publishing output."""

    def translate_path(self, path):
        """Code copied from parent class except the definition of the path variable."""
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)

        # Modify the path so that it is fetching files from the output directory, not the root of the project.
        path = str(pathlib.Path.cwd() / get_configuration().publishing.output)

        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path
