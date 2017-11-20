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
Tempmon server daemon
"""

from __future__ import unicode_literals, absolute_import

import time
import datetime
import logging

from rattail.db import Session, api
from rattail_tempmon.db import Session as TempmonSession, model as tempmon
from rattail.daemon import Daemon
from rattail.time import localtime, make_utc
from rattail.mail import send_email


log = logging.getLogger(__name__)


class TempmonServerDaemon(Daemon):
    """
    Linux daemon implementation of tempmon server.
    """
    timefmt = '%Y-%m-%d %H:%M:%S'

    def run(self):
        """
        Keeps an eye on tempmon readings and sends alerts as needed.
        """
        self.extra_emails = self.config.getlist('rattail.tempmon', 'extra_emails', default=[])
        while True:
            self.check_readings()

            # TODO: make this configurable
            time.sleep(60)

    def check_readings(self):
        self.now = make_utc()
        session = TempmonSession()

        try:
            clients = session.query(tempmon.Client)\
                             .filter(tempmon.Client.enabled == True)
            for client in clients:
                self.check_readings_for_client(session, client)
        except:
            log.exception("Failed to check client probe readings (but will keep trying)")
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    def check_readings_for_client(self, session, client):
        delay = client.delay or 60
        cutoff = self.now - datetime.timedelta(seconds=delay + 60)
        online = True
        for probe in client.enabled_probes():
            online = online and bool(self.check_readings_for_probe(session, probe, cutoff))
        if not online and client.online:
            log.info("marking client as OFFLINE: {}".format(client))
            client.online = False

    def check_readings_for_probe(self, session, probe, cutoff):
        readings = session.query(tempmon.Reading)\
                          .filter(tempmon.Reading.probe == probe)\
                          .filter(tempmon.Reading.taken >= cutoff)\
                          .all()
        if readings:
            # we really only care about the latest reading
            reading = sorted(readings, key=lambda r: r.taken)[-1]

            if (reading.degrees_f <= probe.critical_temp_min or
                  reading.degrees_f >= probe.critical_temp_max):
                self.update_status(probe, self.enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP, reading)

            elif reading.degrees_f < probe.good_temp_min:
                self.update_status(probe, self.enum.TEMPMON_PROBE_STATUS_LOW_TEMP, reading)

            elif reading.degrees_f > probe.good_temp_max:
                self.update_status(probe, self.enum.TEMPMON_PROBE_STATUS_HIGH_TEMP, reading)

            else: # temp is good
                self.update_status(probe, self.enum.TEMPMON_PROBE_STATUS_GOOD_TEMP, reading)

        else: # no readings for probe
            self.update_status(probe, self.enum.TEMPMON_PROBE_STATUS_ERROR)

        return readings

    def update_status(self, probe, status, reading=None):
        data = {
            'probe': probe,
            'status': self.enum.TEMPMON_PROBE_STATUS[status],
            'reading': reading,
            'taken': localtime(self.config, reading.taken, from_utc=True) if reading else None,
            'now': localtime(self.config),
        }

        prev_status = probe.status
        prev_alert_sent = probe.status_alert_sent
        if probe.status != status:
            probe.status = status
            probe.status_changed = self.now
            probe.status_alert_sent = None

            # send email when things go back to normal, after being bad
            if status == self.enum.TEMPMON_PROBE_STATUS_GOOD_TEMP and prev_alert_sent:
                send_email(self.config, 'tempmon_good_temp', data)
                probe.status_alert_sent = self.now

        # no (more) email if status is good
        if status == self.enum.TEMPMON_PROBE_STATUS_GOOD_TEMP:
            return

        # no email if we already sent one...until timeout is reached
        if probe.status_alert_sent:
            timeout = datetime.timedelta(minutes=probe.status_alert_timeout)
            if (self.now - probe.status_alert_sent) <= timeout:
                return

        # delay even the first email, until configured threshold is reached
        timeout = datetime.timedelta(minutes=probe.therm_status_timeout)
        if (self.now - probe.status_changed) <= timeout:
            return

        msgtypes = {
            self.enum.TEMPMON_PROBE_STATUS_LOW_TEMP             : 'tempmon_low_temp',
            self.enum.TEMPMON_PROBE_STATUS_HIGH_TEMP            : 'tempmon_high_temp',
            self.enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP        : 'tempmon_critical_temp',
            self.enum.TEMPMON_PROBE_STATUS_ERROR                : 'tempmon_error',
        }

        send_email(self.config, msgtypes[status], data)

        # maybe send more emails if config said so
        for msgtype in self.extra_emails:
            send_email(self.config, msgtype, data)

        probe.status_alert_sent = self.now


def make_daemon(config, pidfile=None):
    """
    Returns a tempmon server daemon instance.
    """
    if not pidfile:
        pidfile = config.get('rattail.tempmon', 'server.pid_path',
                             default='/var/run/rattail/tempmon-server.pid')
    return TempmonServerDaemon(pidfile, config=config)
