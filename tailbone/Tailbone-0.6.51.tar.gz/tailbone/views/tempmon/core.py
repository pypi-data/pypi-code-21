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
Common stuff for tempmon views
"""

from __future__ import unicode_literals, absolute_import

from rattail_tempmon.db import Session as RawTempmonSession

from formalchemy.fields import SelectFieldRenderer
from webhelpers2.html import tags

from tailbone import views
from tailbone.db import TempmonSession


class MasterView(views.MasterView2):
    """
    Base class for tempmon views.
    """
    Session = TempmonSession

    def get_bulk_delete_session(self):
        return RawTempmonSession()


class ClientFieldRenderer(SelectFieldRenderer):

    def render_readonly(self, **kwargs):
        client = self.raw_value
        if not client:
            return ''
        return tags.link_to(client, self.request.route_url('tempmon.clients.view', uuid=client.uuid))


class ProbeFieldRenderer(SelectFieldRenderer):

    def render_readonly(self, **kwargs):
        probe = self.raw_value
        if not probe:
            return ''
        return tags.link_to(probe, self.request.route_url('tempmon.probes.view', uuid=probe.uuid))
