# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
TempMon client daemon
"""

from __future__ import unicode_literals, absolute_import

import time
import datetime
import random
import socket
import logging

from sqlalchemy.orm.exc import NoResultFound

from rattail.daemon import Daemon
from rattail_tempmon.db import Session, model as tempmon
from rattail.exceptions import ConfigurationError


log = logging.getLogger(__name__)


class TempmonClient(Daemon):
    """
    Linux daemon implementation of Tempmon client
    """

    def run(self):
        """
        This method is invoked upon daemon startup.  It is meant to run/loop
        "forever" or until daemon stop.
        """
        # maybe generate random data instead of reading from true probe
        self.dummy_probes = self.config.getbool('tempmon.client', 'dummy_probes', default=False)

        # figure out which client we are
        hostname = self.config.get('tempmon.client', 'hostname', default=socket.gethostname())
        session = Session()
        try:
            client = session.query(tempmon.Client)\
                            .filter_by(hostname=hostname)\
                            .one()
        except NoResultFound:
            session.close()
            raise ConfigurationError("No tempmon client configured for hostname: {}".format(hostname))
        client_uuid = client.uuid
        self.delay = client.delay or 60
        session.close()

        # main loop: take readings, pause, repeat
        while True:

            session = Session()

            try:
                client = session.query(tempmon.Client).get(client_uuid)
                self.delay = client.delay or 60
                if client.enabled:
                    for probe in client.enabled_probes():
                        self.take_reading(session, probe)

            except:
                log.exception("Failed to read/record temperature data (but will keep trying)")
                session.rollback()

            else:
                # make sure we show as being online
                if not client.online:
                    client.online = True
                try:
                    session.commit()
                except:
                    log.exception("Failed to read/record temperature data (but will keep trying)")
                    session.rollback()

            finally:
                session.close()

            time.sleep(self.delay)

    def take_reading(self, session, probe):
        """
        Take a single reading and add to Rattail database.
        """
        reading = tempmon.Reading()
        reading.client = probe.client
        reading.probe = probe
        reading.degrees_f = self.read_temp(probe)
        reading.taken = datetime.datetime.utcnow()
        session.add(reading)
        return reading

    def read_temp(self, probe):
        """
        Check for good reading, then format temperature to our liking
        """
        if self.dummy_probes:
            return self.random_temp(probe)
        lines = self.read_temp_raw(probe)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw(probe)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return round(temp_f,4)

    def read_temp_raw(self, probe):
        """
        Function that gets the raw temp data
        """
        with open(probe.device_path, 'rt') as therm_file:
            return therm_file.readlines()

    def random_temp(self, probe):
        temp = random.uniform(probe.critical_temp_min - 5, probe.critical_temp_max + 5)
        return round(temp, 4)


def make_daemon(config, pidfile=None):
    """
    Returns a tempmon client daemon instance.
    """
    if not pidfile:
        pidfile = config.get('rattail.tempmon', 'client.pid_path',
                             default='/var/run/rattail/tempmon-client.pid')
    return TempmonClient(pidfile, config=config)
