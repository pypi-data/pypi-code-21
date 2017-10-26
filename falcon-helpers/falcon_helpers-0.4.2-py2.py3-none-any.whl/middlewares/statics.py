import os
import logging
import pathlib

import falcon


logger = logging.getLogger(__name__)


class StaticsMiddleware:
    """Statics Middleware

    Return static files from disk with a matching route.

    Example:
        import falcon
        from falcon_helpers.middlewares import statics

        api = falcon.api(
            middlewares=[statics.StaticsMiddleware()]
        )

        # HTTP GET /static/js/main.js

    Attributes:
        static_url (string): The url to look for when processing the request.
            This route is hijacked by the middleware, so any request going to it
            will attempt to find the remaining url path on the file system.

        static_folder (string): the folder, relative to the current working
            directory which contains the static files. Any attempts to go up a
            directory is stripped out (../), see ``clean_path()``

        content_types (dict): a dict containing additional file type to content
            type mappings.
    """

    extension_content_types = {
        'css': 'text/css',
        'js': 'application/javascript',
        'html': 'text/html',
        'svg': 'image/svg+xml'
    }

    def __init__(self, static_url='/static', static_folder='static',
                 content_types=None):
        self.static_url = static_url

        if content_types:
            self.extension_content_types.update(content_types)

        # Use the current working directory to search for the static folder
        path = pathlib.Path(os.getcwd())
        self.static_folder = path.joinpath(static_folder).resolve()
        logger.info('Using {self.static_folder} for the static.')

    def process_request(self, req, resp):
        prefixed = req.path.startswith(self.static_url)

        if not prefixed:
            return

        stripped = req.path.replace(self.static_url, '')
        cleaned = self.clean_path(stripped)
        path = self.static_folder.joinpath(cleaned).resolve()

        try:
            resp.stream = open(path, 'rb')
        except FileNotFoundError:
            raise falcon.HTTPNotFound()

        resp.content_type = self.extension_content_types.get(
            path.suffix.lstrip('.'), 'application/octet-stream')

        raise falcon.HTTPStatus('200 OK')

    def clean_path(self, path):
        """Cleanup a path to prevent traversing any directory above the
        static folder
        """
        return path.replace('../', '').lstrip('/')
