import logging
import os
from operator import attrgetter

from pathlib import Path
from jinja2 import Template

from .cli import task
from . import restart, monitor
from .environmentfile import EnvironmentFile
from .composesource import ComposeSource
from .service import Service

_script_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(_script_dir, 'templates')
service_dir = '/usr/local/portinus-services'


def list():
    _ensure_service_dir()
    print("Available portinus services:")
    for i in sorted(Path(service_dir).iterdir()):
        if i.is_dir():
            print(i.name)


def get_instance_dir(name):
    return os.path.join(service_dir, name)


def get_template(file_name):
    template_file = os.path.join(template_dir, file_name)
    with open(template_file) as f:
        template_contents = f.read()

    return Template(template_contents)


def _ensure_service_dir():
    try:
        os.mkdir(service_dir)
    except FileExistsError:
        pass


class Application(object):

    log = logging.getLogger()

    def __init__(self, name, source=None, environment_file=None, restart_schedule=None):
        self.name = name
        self.environment_file = EnvironmentFile(name, environment_file)
        self.service = Service(name, source)
        self.restart_timer = restart.Timer(name, restart_schedule=restart_schedule)
        self.monitor_service = monitor.Service(name)

    def exists(self):
        return self.service.exists()

    def ensure(self):
        _ensure_service_dir()
        self.environment_file.ensure()
        self.service.ensure()
        self.restart_timer.ensure()
        self.monitor_service.ensure()

    def remove(self):
        self.service.remove()
        self.environment_file.remove()
        self.restart_timer.remove()
        self.monitor_service.remove()
