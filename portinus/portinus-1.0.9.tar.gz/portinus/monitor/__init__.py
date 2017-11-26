import logging
from subprocess import check_output

import portinus

import systemd_unit
from . import checker

log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name):
        self.name = name
        systemd_service_name = portinus.Service(name).service_name
        self._systemd_service = systemd_unit.Unit(systemd_service_name + "-monitor")
        self._systemd_timer = systemd_unit.Unit(systemd_service_name + "-monitor", type="timer")
        pass

    def _generate_service_file(self):
        template = portinus.get_template("monitor.service")
        portinus_monitor_path = check_output(["which", "portinus-monitor"])
        portinus_monitor_path = portinus_monitor_path.decode().strip("\n")

        return template.render(
                name=self.name,
                portinus_monitor_path=portinus_monitor_path
                )

    def _generate_timer_file(self):
        template = portinus.get_template("monitor.timer")

        return template.render(
                name=self.name,
                )

    def ensure(self):
        log.info("Creating/updating {name} monitor timer".format(name=self.name))
        self._systemd_service.ensure(content=self._generate_service_file(), restart=False, enable=False)
        self._systemd_timer.ensure(content=self._generate_timer_file())

    def remove(self):
        log.info("Removing {name} monitor timer".format(name=self.name))
        self._systemd_timer.remove()
        self._systemd_service.remove()
