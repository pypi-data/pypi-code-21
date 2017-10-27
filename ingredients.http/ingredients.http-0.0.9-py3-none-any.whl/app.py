import atexit
import enum
import ipaddress
import logging
import logging.config
import uuid

import cherrypy
from simple_settings import settings, LazySettings
from sqlalchemy_utils.types.arrow import arrow
from sqlalchemy_utils.types.json import json

from ingredients_db.database import Database
from ingredients_http.tools.model import model_in, model_out, model_out_pagination
from ingredients_http.tools.param_validation import model_params


def atexit_register(func):  # pragma: no cover
    """
    Uses either uwsgi's atexit mechanism, or atexit from the stdlib.

    When running under uwsgi, using their atexit handler is more reliable,
    especially when using gevent
    :param func: the function to call at exit
    """
    try:
        import uwsgi
        orig = getattr(uwsgi, 'atexit', None)

        def uwsgi_atexit():
            if callable(orig):
                orig()
            func()

        uwsgi.atexit = uwsgi_atexit
    except ImportError:
        atexit.register(func)


class HTTPApplication(object):
    def __init__(self):
        self.logger = logging.getLogger("%s.%s" % (self.__module__, self.__class__.__name__))

        self.database = None
        self.__mounts = []

    def register_mount(self, mount):
        self.__mounts.append(mount)

    def __setup_logging(self):
        logging.config.dictConfig(settings.LOGGING_CONFIG)

    def __setup_mounts(self):
        config = {}

        for mount in self.__mounts:
            mount.setup()
            config[mount.mount_point] = mount.mount_config()

        cherrypy.tree.mount(None, config=config)

    def __setup_database(self):
        self.logger.debug("Connecting to Database")
        database = Database(settings.DATABASE_HOST, settings.DATABASE_PORT, settings.DATABASE_USERNAME,
                            settings.DATABASE_PASSWORD, settings.DATABASE_DB, settings.DATABASE_POOL_SIZE)
        database.connect()

        self.logger.debug("Testing database connection")
        with database.session():
            pass

        self.database = database

    def __setup_signaling(self):
        def signal_handler():  # pragma: no cover
            self.database.close()

        atexit_register(signal_handler)

    def db_session(self):
        cherrypy.request.db_session = self.database.session

    def __setup_tools(self):
        cherrypy.tools.model_params = cherrypy.Tool('before_request_body', model_params, priority=10)
        cherrypy.tools.model_in = cherrypy.Tool('before_request_body', model_in, priority=20)

        cherrypy.tools.db_session = cherrypy.Tool('on_start_resource', self.db_session, priority=10)

        cherrypy.tools.model_out = cherrypy.Tool('before_handler', model_out)
        cherrypy.tools.model_out_pagination = cherrypy.Tool('before_handler', model_out_pagination)

    def setup(self):

        default_settings = LazySettings('ingredients_http.conf.default_settings')
        settings.configure(**default_settings.as_dict())
        settings._initialized = False
        settings.setup()

        old_json_encoder = json.JSONEncoder.default

        def json_encoder(self, o):  # pragma: no cover
            if isinstance(o, uuid.UUID):
                return str(o)
            if isinstance(o, arrow.Arrow):
                return o.isoformat()
            if isinstance(o, ipaddress.IPv4Network):
                return str(o)
            if isinstance(o, ipaddress.IPv4Address):
                return str(o)
            if isinstance(o, enum.Enum):
                return o.value

            return old_json_encoder(self, o)

        json.JSONEncoder.default = json_encoder

        # setup basic logging
        self.__setup_logging()

        if settings.DEBUG:
            self.logger.warning("==========================================================================")
            self.logger.warning("RUNNING IN DEBUG MODE. SET THE ENVIRONMENT VARIABLE PRODUCTION TO DISABLE.")
            self.logger.warning("==========================================================================")

        # setup signaling
        self.__setup_signaling()

        # setup database
        self.__setup_database()

        # setup tools
        self.__setup_tools()

        # setup mount points
        self.__setup_mounts()

    @property
    def wsgi_application(self):

        return cherrypy.tree
