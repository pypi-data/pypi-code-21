# coding: utf-8

"""Copyright(c) 2017, Very Large Bits LLC

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

from future import standard_library
standard_library.install_aliases()

from base64 import b64decode, b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

import requests
import unittest2 as unittest

from verylargebits.client import Client

def get_free_port(host):
    """Tries to pick a port that likely will be free when needed."""

    socket_ = socket(AF_INET, type=SOCK_STREAM)
    socket_.bind((host, 0))
    _, port = socket_.getsockname()
    socket_.close()

    return port

class MockService(object):
    def __init__(self, handler):
        self.port = get_free_port('localhost')
        self.url = 'http://localhost:' + str(self.port)
        self.server = HTTPServer(('localhost', self.port), handler)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.server.shutdown()

class ClientTestCase(unittest.TestCase):
    def test_post_asset_json(self):
        class TestRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == '/asset' \
                    and self.headers['Authorization'] == 'Basic dGVzdDpwYXNzd29yZA==' \
                    and self.headers['Content-Type'] == 'application/json':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'id': 'l3pgbkpbcm5l41kt4tdgf2x4jq',
                    }).encode('utf-8'))

        service = MockService(TestRequestHandler)
        client = Client.from_basic_auth('test', 'password', service_url=service.url)
        response = client.post_asset(b'my-data', sha1=None, patch_count=1).json()
        self.assertEqual(response['id'], 'l3pgbkpbcm5l41kt4tdgf2x4jq')
        service.stop()

    def test_post_asset_octet_stream(self):
        class TestRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == '/asset' \
                    and self.headers['Authorization'] == 'Basic dGVzdDpwYXNzd29yZA==' \
                    and self.headers['Content-Type'] == 'application/octet-stream':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'id': 'l3pgbkpbcm5l41kt4tdgf2x4jq',
                    }).encode('utf-8'))

        service = MockService(TestRequestHandler)
        client = Client.from_basic_auth('test', 'password', service_url=service.url)
        response = client.post_asset(b'my-data').json()
        self.assertEqual(response['id'], 'l3pgbkpbcm5l41kt4tdgf2x4jq')
        service.stop()
