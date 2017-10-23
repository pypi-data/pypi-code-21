import binascii
import os
import socket

from . import _srp as srp

try:
    import http
except ImportError:
    import httplib as http

from flask import Flask, Response, request
from flask.views import MethodView

from . import tlv

USER = 'Pair-Setup'
PIN = '031-31-666'


class PairingTLV8(Response):
    charset = 'utf-8'
    default_status = 200
    default_mimetype = 'application/pairing+tlv8'
    automatically_set_content_length = False

    def __init__(self, *args, **kwargs):
        super(PairingTLV8, self).__init__(*args, **kwargs)
        self.headers.extend([
            ('Transfer-Encoding', 'chunked'),
            ('Connection', 'keep-alive'),
        ])

    @classmethod
    def force_type(cls, response, environ=None):
        pass


class PairSetup(MethodView):
    def post(self):
        objects = tlv.decode(request.data)
        rv = PairingTLV8(do_pair_setup(objects))
        return rv


class Identify(MethodView):
    def post(self):
        return http.NO_CONTENT


def create_server():
    app = Flask('Happy')

    # add views
    app.add_url_rule('/identify', view_func=Identify.as_view('identify'))
    app.add_url_rule('/pair-setup', view_func=PairSetup.as_view('pair-setup'))

    return app


app = create_server()
