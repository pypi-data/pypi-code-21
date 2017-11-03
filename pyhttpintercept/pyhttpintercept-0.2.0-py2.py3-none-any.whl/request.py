
from BaseHTTPServer import BaseHTTPRequestHandler
import logging_helper; logging = logging_helper.setup_logging()
from classutils.profiling import ProfilingMixIn
from .methods.get import GetHandler
from .methods.post import PostHandler


class HTTPRequestHandler(BaseHTTPRequestHandler):
    BaseHTTPRequestHandler.protocol_version = u"HTTP/1.1"

    #  Override base class logging function
    def log_message(self,
                    fmt,
                    *args):
        logging.info(u"{addr} - {fmt}".format(addr=self.client_address[0],
                                              fmt=fmt % args))

    # Request handlers
    def do_GET(self):
        GetHandler(self,
                   scenarios=self.server.scenarios).handle()

    def do_POST(self):
        PostHandler(self,
                    scenarios=self.server.scenarios).handle()


class HTTPRequestHandlerWithProfiling(BaseHTTPRequestHandler,
                                      ProfilingMixIn):
    BaseHTTPRequestHandler.protocol_version = u"HTTP/1.1"

    #  Override base class logging function
    def log_message(self,
                    fmt,
                    *args):
        logging.info(u"{addr} - {fmt}".format(addr=self.client_address[0],
                                              fmt=fmt % args))

    # Request handlers
    def do_GET(self):
        self.enable_profiling()
        GetHandler(self,
                   scenarios=self.server.scenarios).handle()
        self.disable_profiling_and_log_pstats()

    def do_POST(self):
        self.enable_profiling()
        PostHandler(self,
                    scenarios=self.server.scenarios).handle()
        self.disable_profiling_and_log_pstats()
