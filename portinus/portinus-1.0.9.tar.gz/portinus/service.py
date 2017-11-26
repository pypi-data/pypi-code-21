import subprocess
import os
import logging

import systemd_unit

import portinus

log = logging.getLogger(__name__)

class Service(object):

    def __init__(self, name, source=None):
        if not name:
            raise ValueError("Invalid value for 'name'")
        self.name = name
        self.service_name = "{}-{}".format("portinus", name)
        self._source = portinus.ComposeSource(name, source)
        self._systemd_service = systemd_unit.Unit(self.service_name)
        log.debug("Initialized Service for '{name}' with source: '{source}'".format(name=name, source=source))

    def exists(self):
        return os.path.isdir(portinus.get_instance_dir(self.name))

    def _generate_service_file(self):
        start_command = "{service_script} up".format(service_script=self._source.service_script)
        stop_command = "{service_script} down".format(service_script=self._source.service_script)

        template = portinus.get_template("instance.service")
        return template.render(
            name=self.name,
            start_command=start_command,
            stop_command=stop_command,
            )

    def ensure(self):
        log.info("Creating/updating {name} portinus instance".format(name=self.name))
        try:
            self._systemd_service.stop()
        except FileNotFoundError:
            pass
        self._source.ensure()
        self._systemd_service.ensure(content=self._generate_service_file())

    def remove(self):
        log.info("Removing {name} portinus instance".format(name=self.name))
        self._systemd_service.remove()
        self._source.remove()

    def restart(self):
        log.info("Restarting {name}".format(name=self.name))
        self._systemd_service.restart()

    def stop(self):
        log.info("Stopping {name}".format(name=self.name))
        self._systemd_service.stop()

    def compose(self, command):
        log.info("Running compose for {name} with command: '{command}'".format(name=self.name, command=command))
        if not self.exists():
            raise ValueError("The specified service does not exist")
        subprocess.call([self._source.service_script] + list(command))
