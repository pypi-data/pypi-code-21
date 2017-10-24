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
Common email config objects
"""

from __future__ import unicode_literals, absolute_import

import sys
import socket
from traceback import format_exception

from rattail.mail import Email


class datasync_error_watcher_get_changes(Email):
    """
    When any datasync watcher thread encounters an error trying to get changes,
    this email is sent out.
    """
    default_subject = "Watcher failed to get changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        watcher = DataSyncWatcher(self.config, 'test')
        watcher.consumes_self = True
        return {
            'watcher': watcher,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasyncchanges',
            'attempts': 2,
        }


class filemon_action_error(Email):
    """
    When any filemon thread encounters an error (and the retry attempts have
    been exhausted) then it will send out this email.
    """
    default_subject = "Error invoking action(s)"

    def sample_data(self, request):
        from rattail.filemon import Action
        action = Action(self.config)
        action.spec = 'rattail.filemon.actions:Action'
        action.retry_delay = 10
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        return {
            'hostname': socket.gethostname(),
            'path': '/tmp/foo.csv',
            'action': action,
            'attempts': 3,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
        }


class rattail_import_versions_updates(Email):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    fallback_key = 'rattail_import_updates'
    default_subject = "Changes for Rattail -> Rattail (Versions) import"


class user_feedback(Email):
    """
    Sent when a user submits a Feedback form from the web UI.
    """
    default_subject = "User Feedback"

    def sample_data(self, request):
        return {
            'user': None,
            'user_name': "Fred Flintstone",
            'referrer': request.route_url('home'),
            'message': "Hey there,\n\njust wondered what the heck was going on with this site?  It's crap.\n\nFred",
        }
