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

from tawf.api import Application, Method


def method_meta(app, path, method):
    cls = app._handlers['^' + path + '$'][1]
    f = getattr(cls, method)._partialmethod.args[1]
    return f


def test_route_default():
    """
    Check if GET HTTP method is used for default route.
    """
    app = Application()

    @app.route('/test')
    def f():
        return 1

    assert f == method_meta(app, '/test', 'get').callback


def test_route_post():
    """
    Check if route for POST HTTP method can be created.
    """
    app = Application()

    @app.route('/test', method=Method.POST)
    def f():
        return 1

    assert f == method_meta(app, '/test', 'post').callback


def test_multiple_methods_for_single_function():
    """
    Test if one URI can be mapped to one function handling different HTTP
    methods.
    """
    app = Application()

    @app.route('/test', method=(Method.GET, Method.POST))
    def f():
        return 1

    assert f == method_meta(app, '/test', 'get').callback
    assert f == method_meta(app, '/test', 'post').callback


def test_multiple_methods_and_functions():
    """
    Test if one URI can be mapped to different functions handling different
    HTTP methods.
    """
    app = Application()

    @app.route('/test', method=Method.GET)
    def f1():
        return 1

    @app.route('/test', method=Method.POST)
    def f2():
        return 1

    assert f1 == method_meta(app, '/test', 'get').callback
    assert f2 == method_meta(app, '/test', 'post').callback


def test_sse_and_rest_mix():
    """
    Test if URI can be mapped to SSE handling function and to different
    function with non-get HTTP method.
    """
    app = Application()

    @app.sse('/test')
    def f1():
        return 1

    @app.route('/test', method=Method.OPTIONS)
    def f2():
        return 1

    assert f1 == method_meta(app, '/test', 'get').callback
    assert f2 == method_meta(app, '/test', 'options').callback


def test_mimetype_mix():
    """
    Test if URI mapped to two different HTTP methods can respond with
    different content type.
    """
    app = Application()

    @app.sse('/test')
    def f1():
        return 1

    @app.route('/test', method=Method.OPTIONS, mimetype='application/json')
    def f2():
        return 1

    assert 'text/plain' == method_meta(app, '/test', 'get').mimetype
    assert 'application/json' == method_meta(app, '/test', 'options').mimetype


# vim: sw=4:et:ai
