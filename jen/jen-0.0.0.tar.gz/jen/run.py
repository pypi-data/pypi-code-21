import mimetypes
import os.path

from gunicorn.app.base import BaseApplication

from .cli import CliCommand
from .template_renderer import TemplateRenderer


class Run(CliCommand):

    name = 'run'
    usage = 'jen run <source>'
    description = 'Serves content from specified <source> directory'

    def run(self, source):
        if not os.path.isdir(source):
            self.abort('ERROR:', 'source must be a valid directory')
        server = GunicornApp(source)
        server.run()


class GunicornApp(BaseApplication):

    def __init__(self, directory):
        self.app = App(directory)
        super(GunicornApp, self).__init__()

    def load_config(self):
        pass

    def load(self):
        return self.app


class App(object):

    def __init__(self, directory):
        self.directory = directory
        self.template_renderer = TemplateRenderer(directory)

    def __call__(self, env, start_response):
        path = env['PATH_INFO']
        response = self.try_template(start_response, path)
        if response:
            return response
        response = self.try_static(start_response, path)
        if response:
            return response
        response = self.try_404(start_response, path)
        if response:
            return response
        return self.response(start_response, '404 Not Found')

    def try_template(self, start_response, path):
        if path != '/' and path.endswith('/'):
            return
        if self.template_renderer.has_page(path):
            body = self.template_renderer.render_page(path)
            return self.response(start_response, '200 OK', 'text/html', body)

    def try_static(self, start_response, path):
        full_path = os.path.join(self.directory, path.lstrip('/'))
        if not full_path.endswith('.html') and os.path.exists(full_path) and not os.path.isdir(full_path):
            with open(full_path, 'rb') as f:
                body = f.read()
            return self.response(start_response, '200 OK', self.guess_mime(full_path), body)

    def try_404(self, start_response, path):
        if '.' not in path and self.template_renderer.has_page('404'):
            body = self.template_renderer.render_page('404')
            return self.response(start_response, '404 Not Found', 'text/html', body)

    def guess_mime(self, path):
        mime, _ = mimetypes.guess_type(path)
        return mime or 'application/octet-stream'

    def response(self, start_response, status, mime='text/html', data=''):
        if isinstance(data, str):
            data = data.encode('utf-8')
        start_response(status, [
            ('Content-Type', mime),
            ('Content-Length', str(len(data))),
        ])
        return iter([data])
