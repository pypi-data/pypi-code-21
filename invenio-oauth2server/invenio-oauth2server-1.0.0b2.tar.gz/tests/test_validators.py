# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test invenio_oauth2server validators."""

from __future__ import absolute_import, print_function

from collections import namedtuple

import pytest
from oauthlib.oauth2.rfc6749.errors import InsecureTransportError, \
    InvalidRedirectURIError
from wtforms.validators import ValidationError

from invenio_oauth2server.validators import URLValidator, validate_redirect_uri


@pytest.mark.parametrize('input,expected', [
    ('example.org/', InvalidRedirectURIError()),
    ('http://', InvalidRedirectURIError()),
    ('http://example.org/', InsecureTransportError()),
    ('https://example.org/', None),
    ('https://localhost/', None),
    ('https://127.0.0.1', None),
])
def test_validate_redirect_uri(input, expected):
    """Test redirect URI validator."""
    try:
        validate_redirect_uri(input)
    except Exception as e:
        assert type(e) is type(expected)


def test_url_validator(app):
    """Test url validator."""
    class Field(object):

        def __init__(self, data):
            self.data = data

        def gettext(self, *args, **kwargs):
            return 'text'

    with app.app_context():
        # usually if localhost, validation is failing
        with pytest.raises(ValidationError):
            URLValidator()(
                form=None, field=Field(data='http://localhost:5000'))
        URLValidator()(form=None, field=Field(data='http://mywebsite.it:5000'))

        # enable debug mode to accept also localhost
        app.config['DEBUG'] = True
        URLValidator()(form=None, field=Field(data='http://localhost:5000'))
        URLValidator()(form=None, field=Field(data='http://mywebsite.it:5000'))
