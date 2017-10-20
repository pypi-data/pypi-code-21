# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak contrib team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak contrib projet.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.

"""
This module is an Alignak Broker module that collects the `monitoring_log` broks to send
them to a Python logger configured in the module configuration file
"""

import os
import json
import time
import Queue
import logging
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
from logging.config import dictConfig as logger_dictConfig

from alignak.basemodule import BaseModule
from alignak_module_logs.logevent import LogEvent

from alignak_backend_client.client import Backend, BackendException

logger = logging.getLogger('alignak.module')

properties = {
    'daemons': ['broker'],
    'type': 'logs',
    'external': True,
    'phases': ['running'],
}


class UTCFormatter(logging.Formatter):
    """This logging formatter converts the log date/time to UTC"""
    converter = time.gmtime


def get_instance(mod_conf):
    """Return a module instance for the modules manager

    :param mod_conf: the module properties as defined globally in this file
    :return:
    """
    logger.info("Give an instance of %s for alias: %s", mod_conf.python_name, mod_conf.module_alias)

    return MonitoringLogsCollector(mod_conf)


class MonitoringLogsCollector(BaseModule):
    """Monitoring logs module main class"""
    def __init__(self, mod_conf):
        # pylint: disable=global-statement
        """Module initialization

        mod_conf is a dictionary that contains:
        - all the variables declared in the module configuration file
        - a 'properties' value that is the module properties as defined globally in this file

        :param mod_conf: module configuration file as a dictionary
        """
        BaseModule.__init__(self, mod_conf)

        global logger
        logger = logging.getLogger('alignak.module.%s' % self.alias)

        logger.debug("inner properties: %s", self.__dict__)
        logger.debug("received configuration: %s", mod_conf.__dict__)

        # Internal logger for the monitoring logs
        self.logger = None

        # Logger configuration file
        self.logger_configuration = os.getenv('ALIGNAK_MONITORING_LOGS_CFG', None)
        if not self.logger_configuration:
            self.logger_configuration = getattr(mod_conf, 'logger_configuration', None)

        # Logger default parameters (used if logger_configuration is not defined)
        self.default_configuration = True
        self.log_logger_name = getattr(mod_conf, 'log_logger_name', 'monitoring-logs')
        self.log_dir = getattr(mod_conf, 'log_dir', '/tmp')
        self.log_file = getattr(mod_conf, 'log_file', 'monitoring-logs.log')
        self.log_filename = os.path.join(self.log_dir, self.log_file)
        self.log_rotation_when = getattr(mod_conf, 'log_rotation_when', 'midnight')
        self.log_rotation_interval = int(getattr(mod_conf, 'log_rotation_interval', '1'))
        self.log_rotation_count = int(getattr(mod_conf, 'log_rotation_count', '365'))
        self.log_level = getattr(mod_conf, 'log_level', 'INFO')
        self.log_level = getattr(logging, self.log_level, None)
        self.log_format = getattr(mod_conf, 'log_format ',
                                  '[%(created)i] %(levelname)s: %(message)s')
        self.log_date = getattr(mod_conf, 'log_date', '%Y-%m-%d %H:%M:%S %Z')

        if self.logger_configuration:
            logger.info("logger configuration defined in %s",
                        self.logger_configuration)
            self.default_configuration = False
            if not os.path.exists(self.logger_configuration):
                self.default_configuration = True
                logger.warning("defined logger configuration file does not exist! "
                               "Using default configuration.")

        if self.default_configuration:
            logger.info("logger default configuration:")
            logger.info(" - rotating logs in %s", self.log_filename)
            logger.info(" - log level: %s", self.log_level)
            logger.info(" - rotation every %d %s, keeping %s files",
                        self.log_rotation_interval, self.log_rotation_when, self.log_rotation_count)

        self.setup_logging()

        # Alignak Backend part
        # ---
        self.backend_available = False
        self.backend_url = getattr(mod_conf, 'alignak_backend', '')
        if self.backend_url:
            logger.info("Alignak backend endpoint: %s", self.backend_url)

            self.client_processes = int(getattr(mod_conf, 'client_processes', '1'))
            logger.info("Number of processes used by backend client: %s", self.client_processes)

            self.backend = Backend(self.backend_url, self.client_processes)
            # If a backend token is provided in the configuration, we assume that it is valid
            # and the backend is yet connected and authenticated
            self.backend.token = getattr(mod_conf, 'token', '')
            self.backend.authenticated = (self.backend.token != '')
            self.backend_available = False

            self.backend_username = getattr(mod_conf, 'username', '')
            self.backend_password = getattr(mod_conf, 'password', '')
            self.backend_generate = getattr(mod_conf, 'allowgeneratetoken', False)

            self.alignak_backend_polling_period = \
                int(getattr(mod_conf, 'alignak_backend_polling_period', '10'))

            if not self.backend.token and not self.backend_username:
                logger.warning("No Alignak backend credentials configured (empty token and "
                               "empty username. "
                               "The requested backend connection will not be available")
                self.backend_url = ''
            else:
                self.getBackendAvailability()
        else:
            logger.warning('Alignak Backend is not configured. '
                           'Some module features will not be available.')

    def init(self):
        """Handle this module "post" init ; just before it'll be started.

        Like just open necessaries file(s), database(s),
        or whatever the module will need.

        :return: None
        """
        return True

    def setup_logging(self):
        """Setup logging configuration

        :return: none
        """
        self.logger = logging.getLogger(self.log_logger_name)

        if self.default_configuration:
            # Set logger level
            self.logger.setLevel(self.log_level)

            logger.debug("Logger (default) handlers: %s", self.logger.handlers)
            if not self.logger.handlers:
                file_handler = TimedRotatingFileHandler(self.log_filename,
                                                        when=self.log_rotation_when,
                                                        interval=self.log_rotation_interval,
                                                        backupCount=self.log_rotation_count)
                file_handler.setFormatter(Formatter(self.log_format, self.log_date))
                self.logger.addHandler(file_handler)
                logger.debug("Logger (default), added a TimedRotatingFileHandler")
        else:
            with open(self.logger_configuration, 'rt') as f:
                config = json.load(f)
            try:
                logger_dictConfig(config)
            except ValueError as exp:
                logger.error("Logger configuration file is not parsable correctly!")
                logger.exception(exp)

    def getBackendAvailability(self):
        """Authenticate and get the token

        :return: None
        """
        generate = 'enabled'
        if not self.backend_generate:
            generate = 'disabled'

        try:
            if not self.backend.authenticated:
                logger.info("Signing-in to the backend...")
                self.backend_available = self.backend.login(self.backend_username,
                                                            self.backend_password, generate)
            logger.debug("Checking backend availability, token: %s, authenticated: %s",
                         self.backend.token, self.backend.authenticated)
            self.backend.get('/realm', {'where': json.dumps({'name': 'All'})})
            self.backend_available = True
        except BackendException as exp:
            logger.warning("Alignak backend is currently not available.")
            logger.warning("Exception: %s", exp)
            logger.warning("Response: %s", exp.response)
            self.backend_available = False

    def do_loop_turn(self):  # pragma: no cover
        """This function is present because of an abstract function in the BaseModule class"""
        logger.info("In loop")
        time.sleep(1)

    def manage_brok(self, brok):
        """We got the data to manage

        :param brok: Brok object
        :type brok: object
        :return: False if a backend post error happens
        """
        # Ignore all except 'monitoring_log' broks...
        if brok.type not in ['monitoring_log']:
            return False

        level = brok.data['level'].lower()
        if level not in ['debug', 'info', 'warning', 'error', 'critical']:
            return False

        logger.debug("Got monitoring log brok: %s", brok)

        # Send to configured logger
        message = brok.data['message']
        message = message.replace('\r', '\\r')
        message = message.replace('\n', '\\n')
        func = getattr(self.logger, level)
        func(message)

        if not self.backend_available:
            return False

        # Try to get a monitoring event
        try:
            event = LogEvent(('[%s] ' % int(time.time())) + brok.data['message'])
            if event.valid:
                # -------------------------------------------
                # Add an history event
                data = {}
                if event.event_type == 'TIMEPERIOD':
                    data = {
                        "host_name": 'n/a',
                        "service_name": 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.timeperiod_transition",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'NOTIFICATION':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.notification",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'ALERT':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.alert",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'DOWNTIME':
                    downtime_type = "monitoring.downtime_start"
                    if event.data['state'] == 'STOPPED':
                        downtime_type = "monitoring.downtime_end"
                    if event.data['state'] == 'CANCELLED':
                        downtime_type = "monitoring.downtime_cancelled"

                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": downtime_type,
                        "message": brok.data['message'],
                    }

                if event.event_type == 'FLAPPING':
                    flapping_type = "monitoring.flapping_start"
                    if event.data['state'] == 'STOPPED':
                        flapping_type = "monitoring.flapping_stop"

                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": flapping_type,
                        "message": brok.data['message'],
                    }

                if event.event_type == 'COMMENT':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": event.data['author'] or 'Alignak',
                        "type": "webui.comment",
                        "message": event.data['comment'],
                    }

                if data:
                    try:
                        logger.debug("Posting history data: %s", data)
                        self.backend.post('history', data)
                    except BackendException as exp:
                        logger.exception("Exception: %s", exp)
                        logger.error("Exception response: %s", exp.response)
                        return False
                else:
                    logger.debug("Monitoring event not stored in the backend: %s",
                                 brok.data['message'])
            else:
                logger.warning("No monitoring event detected from: %s", brok.data['message'])
        except ValueError:
            logger.warning("Unable to decode a monitoring event from: %s", brok.data['message'])

        return True

    def main(self):
        """Main loop of the process

        This module is an "external" module
        :return:
        """
        # Set the OS process title
        self.set_proctitle(self.alias)
        self.set_exit_handler()

        logger.info("starting...")

        while not self.interrupted:
            try:
                logger.debug("queue length: %s", self.to_q.qsize())
                start = time.time()

                message = self.to_q.get_nowait()
                for brok in message:
                    # Prepare and manage each brok in the queue message
                    brok.prepare()
                    self.manage_brok(brok)

                logger.debug("time to manage %s broks (%d secs)", len(message), time.time() - start)
            except Queue.Empty:
                # logger.debug("No message in the module queue")
                time.sleep(0.1)

        logger.info("stopping...")

        # Properly close all the Python logging stuff
        # fixme: this seems to make the alignak daemon hung when shutting down...
        # probably because it is running as a daemon.
        # See: http://stackoverflow.com/questions/24816456/python-logging-wont-shutdown
        logging.shutdown()

        logger.info("stopped")
