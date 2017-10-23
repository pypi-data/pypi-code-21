import logging

import portinus
from systemd_unit import Unit

log = logging.getLogger(__name__)


class Timer(object):

    def __init__(self, name, restart_schedule):
        self.name = name
        self.restart_schedule = restart_schedule
        systemd_service_name = portinus.Service(name).service_name
        self._systemd_service = Unit(systemd_service_name + "-restart")
        self._systemd_timer = Unit(systemd_service_name + "-restart", type="timer")
        log.debug("Initialized restart.Timer for '{name}' with restart_schedule: '{restart_schedule}'".format(name=name, restart_schedule=restart_schedule))

    def __bool__(self):
        return bool(self.restart_schedule)

    def _generate_service_file(self):
        template_file = portinus.get_template("restart.service")
        instance_service = Unit(self.name)

        return template_file.render(
                name=self.name,
                service_name=instance_service.service_name,
                )

    def _generate_timer_file(self):
        template_file = portinus.get_template("restart.timer")

        return template_file.render(
                name=self.name,
                restart_schedule=self.restart_schedule,
                )

    def ensure(self):
        if self:
            log.info("Creating/updating {name} restart timer".format(name=self.name))
            self._systemd_service.ensure(content=self._generate_service_file(), restart=False, enable=False)
            self._systemd_timer.ensure(content=self._generate_timer_file())
        else:
            log.info("No restart schedule specified for {name}. Removing any existing restart timers".format(name=self.name))
            self.remove()

    def remove(self):
        log.info("Removing {name} restart timer. Errors from systemctl may occur".format(name=self.name))
        self._systemd_timer.remove()
        self._systemd_service.remove()
