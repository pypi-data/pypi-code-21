import gevent
import gevent.monkey
import gevent.pywsgi
gevent.monkey.patch_all(thread=False)

import logging
import os
import signal
import socket
import sys
import urllib.parse

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils.module_loading import import_string

from .. import watcher
from .. import manifest

from . import bottle
from .liveserver import LIVE_PORT
from .utils import IP_ANY

logger = logging.getLogger(__name__)



class Worker:
    RESTART_EXIT_CODE = 4
    RESTART_SIGNAL = signal.SIGHUP
    READY_SIGNAL = signal.SIGALRM

    LIVE_SCRIPT_TPL = "<script>window.livereload={'url':'{url}'}</script>"+manifest.Manifest.find('assets:javascript:livereload')


    @classmethod
    def _get_django_app(cls):
        app_path = getattr(settings, 'WSGI_APPLICATION')
        if app_path is None:
            return get_wsgi_application()
        else:
            return import_string(app_path)

    def _inject_live_script(self, app):
        def wrapper(environ, start_response):
            def wrapped_start_response(status, headerlist):
                headers = []
                for key, value in headerlist:
                    if key.lower() == 'Content-Length'.lower():
                        value = str(int(value)+len(self.live_script))
                    headers.append((key, value))
                return start_response(status, headers)
            injected = False
            for body_part in app(environ, wrapped_start_response):
                pos = body_part.find(b'</body>')
                if pos > 0:
                    yield body_part[:pos]
                    yield self.live_script
                    yield body_part[pos:]
                    injected = True
                else:
                    yield body_part
            if not injected:
                yield b' '*len(self.live_script)
        return wrapper

    @classmethod
    def spawn(cls, ip, port, live_url):
        logger.info("Spawning worker")
        args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ["_RUN_WORKER"] = 'true'
        new_environ["_WORKER_IP"] = ip
        new_environ["_WORKER_PORT"] = str(port)
        new_environ["_LIVE_URL"] = live_url

        worker_pid = os.spawnve(os.P_NOWAIT, sys.executable, args, new_environ)
        logger.info("Spawned worker PID {pid}".format(pid=worker_pid))
        return worker_pid

    @classmethod
    def is_worker(cls):
        return os.environ.get('_RUN_WORKER', 'false') == 'true'

    def __init__(self, ip=None, port=None, live_url=None):
        if ip is None:
            self.ip = os.environ.get('_WORKER_IP', IP_ANY)
        if port is None:
            self.port = int(os.environ.get('_WORKER_PORT', 8080))
        if live_url is None:
            self.live_url = os.environ.get('_LIVE_URL','ws://{ip}:{port}/'.format(ip=IP_ANY,port=LIVE_PORT))

        self.live_script = bytes(self.LIVE_SCRIPT_TPL.replace('{url}',self.live_url), encoding='ascii')

        # Determine whether we need a separate server
        # to serve static files

        static_url = urllib.parse.urlparse(settings.STATIC_URL)
        media_url = urllib.parse.urlparse(settings.MEDIA_URL)
        if static_url.hostname:
            static_ip = socket.gethostbyname(static_url.hostname)
        else:
            static_ip = IP_ANY
        if static_url.port:
            static_port = static_url.port
        else:
            static_port = self.port

        django_ip = self.ip
        django_port = self.port

        if (static_ip == IP_ANY or django_ip == IP_ANY or static_ip == django_ip) and (static_port == django_port):
            self._separate_static_server = False
        else:
            self._separate_static_server = True

        self.static_ip = static_ip
        self.static_port = static_port
        self.django_ip = django_ip
        self.django_port = django_port

        self.app = bottle.Bottle()

        # Add CORS headers
        @self.app.hook('after_request')
        def enable_cors():
            """
            You need to add some headers to each request.
            Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
            """
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'
            bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
            bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        # Serve static files
        @self.app.route(static_url.path+'<filename:path>', skip=[self._inject_live_script])
        def send_static(filename):
            return bottle.static_file(filename, root=settings.STATIC_ROOT)

        # Serve user-uploaded media files
        @self.app.route(media_url.path+'<filename:path>', skip=[self._inject_live_script])
        def send_static(filename):
            return bottle.static_file(filename, root=settings.MEDIA_ROOT)


    def signal_handler(self, sig_num, stack_frame):
        if sig_num == self.RESTART_SIGNAL:
            logger.info("Restarting worker.")
            exit(Worker.RESTART_EXIT_CODE)

    def run_forever(self):
        signal.signal(self.RESTART_SIGNAL, self.signal_handler)
        djapp = self._inject_live_script(self._get_django_app())

        if self._separate_static_server:
            logger.info("Starting separate static server on {ip}:{port}".format(ip=self.static_ip, port=self.static_port))
            gevent.spawn(gevent.pywsgi.WSGIServer((self.static_ip, self.static_port), self.app).serve_forever)
            server=gevent.pywsgi.WSGIServer((self.django_ip, self.django_port), djapp)
        else:
            @bottle.error(404)
            def error404(error):
                def start_response(status, headerlist):
                    bottle.response.status = int(status.split()[0])
                    for key, value in headerlist:
                        bottle.response.add_header(key, value)
                ret = djapp(bottle.request.environ, start_response)
                return ret
            server = gevent.pywsgi.WSGIServer((self.django_ip, self.django_port), self.app)
        logger.info("Starting django app on {ip}:{port}".format(ip=self.django_ip, port=self.django_port))
        server.start()
        os.kill(os.getppid(), self.READY_SIGNAL)
        server.serve_forever()



