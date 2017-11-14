# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidDBTestCase
from anyblok.config import Configuration
from pyramid.response import Response
from anyblok_pyramid_beaker.config import get_db_name


def update_session_db_name(request):
    request.session['dbname'] = 'other_db_name'
    request.session.save()
    return Response('login')


def update_session_db_name2(request):
    request.session['dbname'] = None
    request.session.save()
    return Response('logout')


def _get_db_name(request):
    if request.anyblok and request.anyblok.registry:
        return Response(request.anyblok.registry.db_name)

    return Response('other_db_name')


class TestRegistry(PyramidDBTestCase):

    def add_route_and_views(self, config):
        config.add_route('dbname-login', '/test/login/')
        config.add_view(update_session_db_name, route_name='dbname-login')
        config.add_route('dbname-logout', '/test/logout/')
        config.add_view(update_session_db_name2, route_name='dbname-logout')
        config.add_route('dbname', '/test/')
        config.add_view(_get_db_name, route_name='dbname')

    def test_registry_by_default_method(self):
        self.includemes.append(self.add_route_and_views)
        webserver = self.init_web_server()
        res = webserver.get('/test/', status=200)
        self.assertEqual(Configuration.get('db_name'), res.body.decode('utf8'))
        webserver.get('/test/login/')
        res = webserver.get('/test/', status=200)
        self.assertEqual('other_db_name', res.body.decode('utf8'))
        webserver.get('/test/logout/')
        res = webserver.get('/test/', status=200)
        self.assertEqual(Configuration.get('db_name'), res.body.decode('utf8'))

    def test_plugin(self):
        self.assertIs(Configuration.get('get_db_name'), get_db_name)
