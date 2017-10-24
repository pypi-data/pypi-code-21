# BOTLIB Framework to program bots
#
# botlib/rest.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" rest interface. """

from .object import Object

import botlib
import http
import http.server
import os
import logging
import time

def init(*args, **kwargs):
    """ initialise the REST server. """
    from .space import cfg, launcher
    server = REST(("localhost", int(cfg.port) or 10102), RESTHandler)
    server.start()
    return server

def shutdown(event):
    """ stop the REST server. """
    from .space import runtime
    rest = runtime.get("REST", [])
    for obj in rest:
        obj.exit()

class REST(http.server.HTTPServer, Object):

    """
        This REST server serves JSON string from a path into the workdir.
        This makes all data objects accessible through the HTTP server.

    """

    allow_reuse_address = True
    daemon_thread = True
    path = os.path.join("runtime", "rest")

    def __init__(self, *args, **kwargs):
        http.server.HTTPServer.__init__(self, *args, **kwargs)
        Object.__init__(self)
        self.host = args[0]
        self._last = time.time()
        self._starttime = time.time()
        self._stopped = False

    def exit(self):
        """ stop the server. """
        self._status = ""

    def server(self):
        """ blocking loop of the server. """
        self.ready()
        self.serve_forever()

    def start(self):
        """ start the server. """
        from .space import launcher, runtime
        logging.warn("# rest listening on http://%s:%s" % self.host)
        self._state.status = "run"
        runtime.register("REST", self)
        self.ready()
        launcher.launch(self.server)

    def request(self):
        """ called upon receiving a request. """
        self._last = time.time()

    def error(self, request, addr):
        """ log an error. """
        logging.info('! error rest %s %s' % (request, addr))

class RESTHandler(http.server.BaseHTTPRequestHandler):

    """ REST request handler, serves response to REST requests. """

    def setup(self):
        """ setup the handler upon receiving a request. """
        http.server.BaseHTTPRequestHandler.setup(self)
        self._ip = self.client_address[0]
        self._size = 0

    def write_header(self, typestr='text/plain'):
        """ write the standard header before sending data. """
        self.send_response(200)
        self.send_header('Content-type', '%s; charset=%s ' % (typestr, "utf-8"))
        self.send_header('Server', botlib.__version__)
        self.end_headers()

    def do_GET(self):
        """ serve a GET request. """
        from .space import cfg
        fn = cfg.workdir + os.sep + self.path
        try:
            f = open(fn, "r")
            txt = f.read()
            f.close()
        except (TypeError, FileNotFoundError, IsADirectoryError):
            self.send_response(404)
            self.end_headers()
            return
        txt = txt.replace("\\n", "\n")
        txt = txt.replace("\\t", "\t")
        self.write_header()
        self.wfile.write(bytes(txt, "utf-8"))
        self.wfile.flush()

    def log(self, code):
        """ log a request. """
        logging.info('! %s %s %s' % (self.address_string(), code, self.path))
