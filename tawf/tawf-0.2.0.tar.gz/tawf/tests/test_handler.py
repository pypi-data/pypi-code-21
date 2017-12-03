#
# TAWF ain't web framework.
#
# Copyright (C) 2015 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from tawf.api import Method
from tawf.handler import RestHandler, HandlerType

import tornado.web

from unittest import mock


def test_405():
    """
    Check if 405 error is sent when URI is not mapped to a function for
    given method.
    """
    app = mock.MagicMock()
    request = mock.MagicMock()
    request.method = 'POST'
    request.uri = '/a/b/c'

    h = RestHandler(app, request)
    h.send_error = mock.MagicMock()
    try:
        h.get()
    except tornado.web.HTTPError as ex:
        assert 'HTTP 405: Method Not Allowed' == str(ex)


def test_serialize_text_plain():
    """
    Check if data returned by a function mapped to an URI is serialized to
    text/plain.
    """
    f = mock.MagicMock()
    f.return_value = 123
    f.__annotations__ = {}

    app = mock.MagicMock()
    request = mock.MagicMock()
    request.method = 'GET'
    cls = RestHandler.copy()
    cls.add_method('get', f, 'text/plain', HandlerType.SYNC)
    h = cls(app, request)
    h.write = mock.MagicMock()

    h.get()
    h.write.assert_called_with('123') # expect string to be sent to client


def test_args():
    """
    Check if appropriate arguments are passed to a function mapped to an
    URI.
    """
    f = mock.MagicMock()
    f.__annotations__ = {}

    app = mock.MagicMock()
    request = mock.MagicMock()
    request.method = 'GET'
    cls = RestHandler.copy()
    cls.add_method('get', f, 'text/plain', HandlerType.SYNC)
    h = cls(app, request)
    h.write = mock.MagicMock()

    h.get(arg1='v1', arg2='v2')
    f.assert_called_with(arg1='v1', arg2='v2')


def test_args_post():
    """
    Check if appropriate arguments are passed to a function mapped to an
    URI with POST HTTP method.
    """
    f = mock.MagicMock()
    f.__annotations__ = {}

    app = mock.MagicMock()
    request = mock.MagicMock()
    request.method = 'POST'
    request.body = b'some data'  # mimetype == text/plain, coverted to str

    cls = RestHandler.copy()
    cls.add_method('post', f, 'text/plain', HandlerType.SYNC)
    h = cls(app, request)
    h.write = mock.MagicMock()

    h.post(arg1='v1', arg2='v2')
    f.assert_called_with(arg1='v1', arg2='v2', data='some data')


def test_args_post_json_data():
    """
    Check if JSON data is passed to a function mapped to an URI with POST
    HTTP method.
    """
    f = mock.MagicMock()
    f.return_value = None
    f.__annotations__ = {}

    app = mock.MagicMock()
    request = mock.MagicMock()
    request.method = 'POST'
    request.body = b'["some data"]'

    cls = RestHandler.copy()
    cls.add_method('post', f, 'application/json', HandlerType.SYNC)
    h = cls(app, request)
    h.write = mock.MagicMock()

    h.post(arg1='v1')
    f.assert_called_with(arg1='v1', data=['some data'])


def test_args_types():
    """
    Check if arguments passed to a function mapped to an URI receives
    properly parsed values.
    """
    f = mock.MagicMock()
    f.__annotations__ = {'arg2': int}

    app = mock.MagicMock()

    request = mock.MagicMock()
    request.method = 'GET'
    cls = RestHandler.copy()
    cls.add_method('get', f, 'text/plain', HandlerType.SYNC)
    h = cls(app, request)
    h.write = mock.MagicMock()

    h.get(arg1='1', arg2='2') # pass values as strings...
    f.assert_called_with(arg1='1', arg2=2) # ... but expect them to be parsed


# vim: sw=4:et:ai
