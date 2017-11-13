import logging
from operator import attrgetter

import pathlib
from jinja2 import Template

from .cli import task
from . import restart, monitor
from .environmentfile import EnvironmentFile
from .composesource import ComposeSource
from .service import Service

_script_dir = pathlib.Path(__file__).resolve().parent
template_dir = _script_dir.joinpath("templates")
service_dir = pathlib.Path("/usr/local/portinus-services")


def list():
    """
    List the available services
    """
    _ensure_service_dir()
    print("Available portinus services:")
    for i in sorted(service_dir.iterdir()):
        if i.is_dir():
            print(i.name)


def get_instance_dir(name):
    """
    Get the directory used for storing the service files
    """
    return service_dir.joinpath(name)


def get_template(file_name):
    """
    Returns the named template
    """
    template_file = template_dir.joinpath(file_name)
    with template_file.open() as f:
        template_contents = f.read()

    return Template(template_contents)


def _ensure_service_dir():
    """
    Make sure that the service dir exists
    """
    service_dir.mkdir(exist_ok=True)


class Application(object):
    """
    A portinus Application. This contains all the pieces of a portinus service
    including the restart timer, monitor server, environment file and
    service files themselves
    """

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
        """
        Ensure all the application components are in the correct state
        """
        _ensure_service_dir()
        self.environment_file.ensure()
        self.service.ensure()
        self.restart_timer.ensure()
        self.monitor_service.ensure()

    def remove(self):
        """
        Remove all the application components
        """
        self.service.remove()
        self.environment_file.remove()
        self.restart_timer.remove()
        self.monitor_service.remove()
