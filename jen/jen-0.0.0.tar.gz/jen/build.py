from shutil import copyfile
import os

from .cli import CliCommand
from .template_renderer import TemplateRenderer


class Build(CliCommand):

    name = 'build'
    usage = 'jen build <source> <target>'
    description = 'Build contents from <source> and output results to <target>'

    def run(self, source, target):
        source = os.path.realpath(source)
        target = os.path.realpath(target)
        if not os.path.isdir(source):
            self.abort('ERROR:', 'source must be a valid directory')
        if os.path.exists(target):
            self.abort('ERROR:', 'target directory already exists')
        self.build(source, target)

    def build(self, source, target):
        self.template_renderer = TemplateRenderer(source)
        filepaths = self.get_files_from_directory(source)
        for path in filepaths:
            if self.is_static(path):
                self.copy_static(source, target, path)
            if self.is_template(path):
                self.render_template(source, target, path)

    def copy_static(self, source, target, path):
        relative_path = self.relative_path(source, path)
        target_path = os.path.join(target, relative_path)
        target_dir = os.path.dirname(target_path)
        self.ensure_directory(target_dir)
        copyfile(path, target_path)
        self.echo('OK:', relative_path)

    def render_template(self, source, target, path):
        relative_path = self.relative_path(source, path)
        relative_path_without_extension = relative_path[:-5]
        target_path = os.path.join(target, relative_path)
        target_dir = os.path.dirname(target_path)
        self.ensure_directory(target_dir)
        body = self.template_renderer.render_page(relative_path_without_extension)
        with open(target_path, 'w') as f:
            f.write(body)
        self.echo('OK:', relative_path)

    def get_files_from_directory(self, directory):
        files = []
        for dirpath, subdirs, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                files.append(filepath)
        return files

    def is_template(self, path):
        filename = os.path.basename(path)
        return path.endswith('.html') and not filename.startswith('_')

    def is_static(self, path):
        return not path.endswith('.html')

    def relative_path(self, source, path):
        return path[len(source)+1:]

    def ensure_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
