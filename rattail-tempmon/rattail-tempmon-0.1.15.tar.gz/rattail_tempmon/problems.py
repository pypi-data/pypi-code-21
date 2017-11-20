# -*- coding: utf-8; -*-
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
Tempmon data problems
"""

from __future__ import unicode_literals, absolute_import

from rattail.mail import send_email
from rattail_tempmon.db import Session as TempmonSession, model as tempmon


def disabled_probes(config, progress=None):
    """
    Notifies if any Tempmon client devices or probes are disabled.
    """
    tempmon_session = TempmonSession()
    clients = tempmon_session.query(tempmon.Client)\
                             .filter(tempmon.Client.enabled == False)\
                             .all()
    probes = tempmon_session.query(tempmon.Probe)\
                            .join(tempmon.Client)\
                            .filter(tempmon.Client.enabled == True)\
                            .filter(tempmon.Probe.enabled == False)\
                            .all()
    if clients or probes:
        send_email(config, 'tempmon_disabled_probes', {
            'disabled_clients': clients,
            'disabled_probes': probes,
        })
    tempmon_session.close()
