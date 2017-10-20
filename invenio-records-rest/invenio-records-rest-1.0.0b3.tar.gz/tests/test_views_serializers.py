# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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


"""Default serializer tests."""

from __future__ import absolute_import, print_function

import json

import pytest
from flask import current_app


def json_record(*args, **kwargs):
    """Test serializer."""
    return current_app.response_class(
        json.dumps({'json_record': 'json_record'}),
        content_type='application/json')


def xml_record(*args, **kwargs):
    """Test serializer."""
    return current_app.response_class(
        "<record>TEST</record>",
        content_type='application/xml')


def json_search(pid_fetcher, search_result, **kwargs):
    """Test serializer."""
    return current_app.response_class(
        json.dumps([{'test': 'test'}], search_result['hits']['total']),
        content_type='application/json')


def xml_search(*args, **kwargs):
    """Test serializer."""
    return current_app.response_class(
        "<collection><record>T1</record><record>T2</record></collection>",
        content_type='application/xml')


@pytest.mark.parametrize('app', [dict(
    endpoint=dict(
        record_serializers={
            'application/json': 'test_views_serializers:json_record',
            'application/xml': 'test_views_serializers.xml_record',
        },
        search_serializers={
            'application/json': 'test_views_serializers:json_search',
            'application/xml': 'test_views_serializers.xml_search',
        },
        default_media_type='application/xml',
    ),
)], indirect=['app'], scope='function')
def test_default_serializer(app, db, es, indexed_records):
    """Test default serializer."""
    # Create records
    accept_json = [('Accept', 'application/json')]
    accept_xml = [('Accept', 'application/xml')]

    with app.test_client() as client:
        res = client.get('/records/', headers=accept_json)
        assert res.status_code == 200
        assert res.content_type == 'application/json'

        res = client.get('/records/', headers=accept_xml)
        assert res.status_code == 200
        assert res.content_type == 'application/xml'

        res = client.get('/records/')
        assert res.status_code == 200
        assert res.content_type == 'application/xml'

        res = client.get('/records/1', headers=accept_json)
        assert res.status_code == 200
        assert res.content_type == 'application/json'

        res = client.get('/records/1', headers=accept_xml)
        assert res.status_code == 200
        assert res.content_type == 'application/xml'

        res = client.get('/records/1')
        assert res.status_code == 200
        assert res.content_type == 'application/xml'
