# This file is part of Indico.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import pytest


@pytest.fixture
def smtp(disallow_emails, smtpserver, app):
    """Wrapper for the `smtpserver` fixture which updates the Indico config
    and disables the SMTP autofail logic for that smtp server.
    """
    old_config = app.config['INDICO']
    app.config['INDICO'] = dict(app.config['INDICO'])  # make it mutable
    app.config['INDICO']['SMTP_SERVER'] = smtpserver.addr
    disallow_emails.add(smtpserver.addr)  # whitelist our smtp server
    yield smtpserver
    app.config['INDICO'] = old_config
