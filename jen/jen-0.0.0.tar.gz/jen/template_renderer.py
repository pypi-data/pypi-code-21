import os.path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound


class TemplateRenderer(object):

    def __init__(self, directory):
        self.directory = directory
        self.jinja_env = None

    def has_page(self, path):
        templates = self._templates_for_path(path)
        for template in templates:
            full_path = os.path.join(self.directory, template)
            if os.path.exists(full_path):
                return True
        return False

    def render_page(self, path):
        templates = self._templates_for_path(path)
        for template in templates:
            full_path = os.path.join(self.directory, template)
            if os.path.exists(full_path):
                return self._render(template)
        return None

    def _templates_for_path(self, path):
        path = path.strip('/')
        last_bit = path.split('/')[-1]
        if last_bit.startswith('_'):
            return []
        if not path:
            return ['index.html']
        return [path + '.html', path + '/index.html']

    def _render(self, template_identifier):
        self._set_env_once()
        template = self.jinja_env.get_template(template_identifier)
        return template.render()

    def _set_env_once(self):
        if self.jinja_env:
            return
        loader = FileSystemLoader(self.directory)
        autoescape = select_autoescape(default=True, default_for_string=True)
        self.jinja_env = Environment(loader=loader, autoescape=autoescape)
