
import threading
from BaseHTTPServer import HTTPServer
from multiprocessing import cpu_count
from SocketServer import ThreadingMixIn
from multiprocessing.pool import ThreadPool
from pyhttpintercept.intercept import InterceptScenario

import logging_helper
from pyhttpintercept.request import HTTPRequestHandler

logging = logging_helper.setup_logging()


class HTTPWebServer(HTTPServer):

    def __init__(self,
                 server_address,
                 request_handler_class=HTTPRequestHandler,
                 threads=cpu_count()):

        """Constructor.  May be extended, do not override."""

        self.port = server_address[-1]

        self.pool = ThreadPool(processes=threads if threads > 1 else 2)

        HTTPServer.__init__(self,
                            server_address=server_address,
                            RequestHandlerClass=request_handler_class,
                            bind_and_activate=False)

        self.timeout = 5

        self.__stop = True

        # Initialise scenario config.
        self.scenarios = InterceptScenario()

    def start(self):

        logging.info(u'Starting HTTP Server on port {port}'.format(port=self.port))

        self.__stop = False

        try:
            # Load active intercept scenario.
            self.scenarios.load_active_scenario()

            self.server_bind()
            self.server_activate()

        except Exception as err:

            self.server_close()

            logging.exception(err)
            logging.error(u'HTTP Server on port {port} failed to start'.format(port=self.port))

            self.__stop = True

        if not self.__stop:
            logging.info(u'HTTP Server started on port {port}!'.format(port=self.port))

            # Run Main loop
            self.pool.apply_async(func=self.__main_loop)

    def stop(self):

        logging.info(u'Stopping HTTP Server on port {port}. Waiting for '
                     u'processes to complete...'.format(port=self.port))

        # Signal loop termination
        self.__stop = True

        try:
            self.shutdown()
            logging.info(u'HTTP Server shutdown on port {port}'
                         .format(port=self.port))

        except Exception as err:
            logging.warning(u'HTTP Server was not started or failed to '
                            u'shut down properly on port {port}'.format(port=self.port))
            logging.debug(err)

        # Wait for running processes to complete
        self.pool.close()
        self.pool.join()

        logging.info(u'HTTP Server stopped on port {port}'.format(port=self.port))

    def __main_loop(self):

        logging.debug(u'main loop ({t})'.format(t=threading.currentThread().name))

        try:
            self.serve_forever()

        except Exception as err:
            logging.error(err)

        while not self.__stop:
            pass  # Run until stop requested!

    @property
    def active(self):
        return not self.__stop


class ThreadedHTTPWebServer(ThreadingMixIn, HTTPWebServer):
    """Handle requests in a separate thread."""


if __name__ == u'__main__':

    ws = ThreadedHTTPWebServer(server_address=(u'', 9080))
    ws.start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        ws.stop()
