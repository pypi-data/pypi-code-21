"""
 # Copyright (c) 2017 Boolein Integer Indonesia, PT.
 # suryakencana 4/5/17 @author nanang.suryadi@boolein.id
 #
 # You are hereby granted a non-exclusive, worldwide, royalty-free license to
 # use, copy, modify, and distribute this software in source code or binary
 # form for use in connection with the web services and APIs provided by
 # Boolein.
 #
 # As with any software that integrates with the Boolein platform, your use
 # of this software is subject to the Boolein Developer Principles and
 # Policies [http://developers.Boolein.com/policy/]. This copyright notice
 # shall be included in all copies or substantial portions of the software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 # DEALINGS IN THE SOFTWARE
 #
 # __main__
"""
import sys
from wsgiref.simple_server import make_server

import trafaret as T
from pyramid.config import Configurator
from pyramid.view import view_config
from trafaret_config import parse_and_validate, ConfigError

from baka_armor.config import CONFIG as armor_cfg
from baka_i18n.config import CONFIG as i18n_cfg


TTRET = T.Dict({
    T.Key('package'): T.String(),
    T.Key('sublime'): T.String(),
})


TRAFARET = TTRET.merge(armor_cfg).merge(i18n_cfg)

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include(__name__)
    return config.make_wsgi_app()


def includeme(config):
    config.include('baka_armor')
    config.include('baka_i18n')
    # config.add_mako_renderer('.html')
    # config.add_static_view(settings.get('static_assets', 'static'),
    #                        '{egg}:public'.format(egg='example'),
    #                        cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('view_secret', '/secret')
    config.scan()


@view_config(route_name='home', renderer='example:templates/_base_main.html')
def route_home(request):
    _ = request
    return {
        'egg': __name__,
        'project': 'Baka Armor',
        'pyramid_version': '1.8.3'
    }

@view_config(route_name='view_secret', renderer='json', permission='view')
def route_secret(request):
    _ = request
    return {
        'okay': 'armor'
    }


if __name__ == '__main__':
    with open("example/configs/config.yaml") as f:
        text = f.read()
    try:
        settings = parse_and_validate(text, TRAFARET, filename='config.yaml')
        print(settings)
    except ConfigError as e:
        e.output()
        sys.exit(1)

    app = main({}, **settings)
    httpd = make_server('0.0.0.0', 6543, app)
    # httpd.socket = ssl.wrap_socket(httpd.socket, certfile='certificate.pem',
    #                                server_side=True)
    httpd.serve_forever()
