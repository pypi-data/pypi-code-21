# coding: utf-8
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref test for pyramid views."""

import lxml.etree

from cubicweb.pyramid.test import PyramidCWTest

import testutils


class EACWSTC(PyramidCWTest):
    settings = {'cubicweb.bwcompat': True}

    def test_xml_post(self):
        with self.admin_access.client_cnx() as cnx:
            testutils.authority_record(cnx, u'TEST AR')
            cnx.commit()
        with open(self.datapath('D33-100.xml')) as stream:
            data = stream.read()

        res = self.webapp.post('/authorityrecord',
                               params=data,
                               content_type='application/xml',
                               headers={'Accept': 'application/json'},
                               status=401)
        self.assertEqual(res.json,
                         {'error': 'This service requires authentication.'})

        self.login()
        res = self.webapp.post('/authorityrecord',
                               params=data,
                               content_type='application/xml',
                               headers={'Accept': 'application/json'},
                               status=403)
        self.assertEqual(res.json,
                         {'error': 'Authenticated user is not linked to an organisation, '
                          'or his organisation has no ARK naming authority.'})

        # to fix previous error, link user to an organization with a ARK NAA
        with self.admin_access.client_cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            cnx.user.cw_set(authority=org)
            cnx.commit()

        res = self.webapp.post('/authorityrecord',
                               params='not xml',
                               content_type='application/xml',
                               headers={'Accept': 'application/json'},
                               status=400)

        expected_details = "Start tag expected, '<' not found, line 1, column 1"
        if lxml.etree.LXML_VERSION[:2] >= (3, 7):
            expected_details += " (line 1)"
        self.assertEqual(res.json,
                         {'error': u'Invalid XML file',
                          'details': expected_details})

        res = self.webapp.post('/authorityrecord',
                               params='<xml xmlns="bla"/>',
                               content_type='application/xml',
                               headers={'Accept': 'application/json'},
                               status=400)
        self.assertEqual(res.json,
                         {'error': 'Unexpected EAC data',
                          'details': 'Missing tag control in XML file'})

        res = self.webapp.post('/authorityrecord',
                               params=data,
                               content_type='application/xml',
                               headers={'Accept': 'application/json'})
        self.assertEqual(list(res.json), ['ark'])

    def test_default_route(self):
        with self.admin_access.client_cnx() as cnx:
            testutils.authority_record(cnx, u'TEST AR')
            cnx.commit()
        res = self.webapp.get('/authorityrecord')
        self.assertEqual(res.content_type, 'text/html')
        # XXX it would be nice if POST with other Content-Type would be routed to cubicweb. See
        # attempt to set 'header' route predicate in pviews.
        # res = self.webapp.post('/authorityrecord')
        # self.assertEqual(res.content_type, 'text/html')
