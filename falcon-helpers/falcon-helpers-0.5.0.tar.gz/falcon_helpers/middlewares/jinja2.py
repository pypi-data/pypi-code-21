import os
import logging

import jinja2
from jinja2 import FileSystemLoader
from jinja2.environment import Environment


logger = logging.getLogger(__name__)

class Jinja2ConfigurationError(Exception):
    pass


class Jinja2Response:
    """A Response Encapsulating a Jinja2 Response

    Utilize this with the Jinja2Middleware to automatically return a rendered
    template as a response.

    Example:
        from falcon_helpers.middlewares import Jinja2Response

        class SomeResource:

            def on_get(self, req, resp):
                data = {
                    "tile": "Some Title"
                }
                resp.context['template'] = Jinja2Response(
                    'path/tp/template',
                    date
                )

    The template will get a few special variables:
        - falcon_request: the current request
        - falcon_response: the current response
        - falcon_resource: the current resource processing the request


    TODO:
        - Add support for globally registered function and variables
    """

    def __init__(self, template, **ctx):
        self.template_fpath = template
        self.ctx = ctx

    def apply(self, resp, env):
        try:
            template = env.get_template(self.template_fpath)
        except jinja2.exceptions.TemplateNotFound as e:
            logger.error(f'Unable to find {self.template_fpath} looking in '
                         f'{env.loader.searchpath}')
            raise


        resp.content_type = 'text/html'
        resp.body = template.render(**self.ctx)


class Jinja2Middleware:

    # TODO: This should probably accept an environment instead of passing around
    # all these one-off environment options
    def __init__(self, template_dpath=None, globals=None):
        """Create a Jinja2Middleware

        :param template_dpath: the path to the Jinja2
        :param globals: a dictionary of globals to attach to the environment

        """
        if not os.path.isabs(template_dpath):
            raise Jinja2ConfigurationError(
                'Template directory path must be absolute')

        self.jinja2_env = Environment()

        # Set up the loader
        self.template_dpath = template_dpath
        self.jinja2_env.loader = FileSystemLoader(self.template_dpath)

        # Add the globals to the env
        self.jinja2_env.globals.update((globals or {}))

    def process_response(self, req, resp, resource, req_succeeded):
        if 'template' not in resp.context:
            return

        resp.context['template'].ctx['falcon_request'] = req
        resp.context['template'].ctx['falcon_response'] = resp
        resp.context['template'].ctx['falcon_resource'] = resource

        resp.context['template'].apply(resp, self.jinja2_env)
