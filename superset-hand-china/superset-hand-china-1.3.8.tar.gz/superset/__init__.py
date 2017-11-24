"""Package's main module!"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from logging.handlers import TimedRotatingFileHandler

import json
import os

from flask import Flask, redirect, g
from flask_appbuilder import SQLA, AppBuilder, IndexView
from flask_appbuilder.baseviews import expose
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.contrib.fixers import ProxyFix

from superset.connectors.connector_registry import ConnectorRegistry
from superset import utils, config  # noqa
from superset.hand.role_manager import MySecurityManager

from flask.ext.cache import Cache

#Start Modifications CAS Configuration******************
from flask_appbuilder.security.sqla.models import User
from flask_cas import CAS
from flask_cas import login_required
from flask_login import login_user, logout_user
from flask.ext.cas import logout
#End Modifications CAS Configuration********************

APP_DIR = os.path.dirname(__file__)
# create log directory
if os.path.exists(APP_DIR + '/../../supersetLog') is False:
    os.mkdir(APP_DIR + '/../../supersetLog')

CONFIG_MODULE = os.environ.get('SUPERSET_CONFIG', 'superset.config')

with open(APP_DIR + '/static/assets/backendSync.json', 'r') as f:
    frontend_config = json.load(f)

app = Flask(__name__)
app.config.from_object(CONFIG_MODULE)
conf = app.config

#################################################################
# Handling manifest file logic at app start
#################################################################
MANIFEST_FILE = APP_DIR + '/static/assets/dist/manifest.json'
manifest = {}


def parse_manifest_json():
    global manifest
    try:
        with open(MANIFEST_FILE, 'r') as f:
            manifest = json.load(f)
    except Exception:
        print("no manifest file found at " + MANIFEST_FILE)


def get_manifest_file(filename):
    if app.debug:
        parse_manifest_json()
    return '/static/assets/dist/' + manifest.get(filename, '')


parse_manifest_json()


@app.context_processor
def get_js_manifest():
    return dict(js_manifest=get_manifest_file)


#################################################################

for bp in conf.get('BLUEPRINTS'):
    try:
        print("Registering blueprint: '{}'".format(bp.name))
        app.register_blueprint(bp)
    except Exception as e:
        print("blueprint registration failed")
        logging.exception(e)

if conf.get('SILENCE_FAB'):
    logging.getLogger('flask_appbuilder').setLevel(logging.ERROR)

if not app.debug:
    # In production mode, add log handler to sys.stderr.
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)
logging.getLogger('pyhive.presto').setLevel(logging.INFO)

db = SQLA(app)

if conf.get('WTF_CSRF_ENABLED'):
    csrf = CSRFProtect(app)
    csrf_exempt_list = conf.get('WTF_CSRF_EXEMPT_LIST', [])
    for ex in csrf_exempt_list:
        csrf.exempt(ex)

utils.pessimistic_connection_handling(db.engine)

cache = utils.setup_cache(app, conf.get('CACHE_CONFIG'))
tables_cache = utils.setup_cache(app, conf.get('TABLE_NAMES_CACHE_CONFIG'))

migrate = Migrate(app, db, directory=APP_DIR + "/migrations")

# Logging configuration
logging.basicConfig(format=app.config.get('LOG_FORMAT'))
logging.getLogger().setLevel(app.config.get('LOG_LEVEL'))

if app.config.get('ENABLE_TIME_ROTATE'):
    logging.getLogger().setLevel(app.config.get('TIME_ROTATE_LOG_LEVEL'))
    handler = TimedRotatingFileHandler(
        app.config.get('FILENAME'),
        when=app.config.get('ROLLOVER'),
        interval=app.config.get('INTERVAL'),
        backupCount=app.config.get('BACKUP_COUNT'))
    logging.getLogger().addHandler(handler)

if app.config.get('ENABLE_CORS'):
    from flask_cors import CORS
    CORS(app, **app.config.get('CORS_OPTIONS'))

if app.config.get('ENABLE_PROXY_FIX'):
    app.wsgi_app = ProxyFix(app.wsgi_app)

if app.config.get('ENABLE_CHUNK_ENCODING'):

    class ChunkedEncodingFix(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            # Setting wsgi.input_terminated tells werkzeug.wsgi to ignore
            # content-length and read the stream till the end.
            if environ.get('HTTP_TRANSFER_ENCODING', '').lower() == u'chunked':
                environ['wsgi.input_terminated'] = True
            return self.app(environ, start_response)

    app.wsgi_app = ChunkedEncodingFix(app.wsgi_app)

if app.config.get('UPLOAD_FOLDER'):
    try:
        os.makedirs(app.config.get('UPLOAD_FOLDER'))
    except OSError:
        pass

for middleware in app.config.get('ADDITIONAL_MIDDLEWARE'):
    app.wsgi_app = middleware(app.wsgi_app)

# cas = CAS(app, '/cas')

class MyIndexView(IndexView):
    @expose('/')
    # @login_required
    def index(self):
        # cas login
        if app.config.get('CAS_AUTHORIZE'):
            print("**************login******************")
            print(cas.username)
            username = cas.username
            if username:
                user = self.appbuilder.sm.find_user(username)
                if user is not None and user.is_active():
                    login_user(user)
                else:
                    return '<h1>user is not invalid</h1>'

        # redirect to login page
        if str(g.user).startswith('<flask_login.AnonymousUserMixin'):
            # not login
            return redirect('/login')
        else:
            if app.config.get('request_url'):
                url = app.config.get('request_url')
                app.config['request_url'] = None
                return redirect(url)
            else:
                portals = db.session.query(models.Portal.id,models.Portal.portal_name).all()
                # print(portals)
                portalIds = [p[0] for p in portals]
                if len(portalIds) > 0:
                    return redirect('/hand/portal/' + str(portalIds[0]) + '/show')
                else:
                    return redirect('/superset/welcome')

    @expose('/logout/')
    def logout(self):
        if app.config.get('CAS_AUTHORIZE'):
            # cas logout
            print('**************logout******************')
            logout_user()
            return logout()
        else:
            logout_user()
            return redirect('/')


appbuilder = AppBuilder(
    app,
    db.session,
    base_template='superset/base.html',
    indexview=MyIndexView,
    # security_manager_class=app.config.get("CUSTOM_SECURITY_MANAGER")
    security_manager_class = MySecurityManager
    )

sm = appbuilder.sm

results_backend = app.config.get("RESULTS_BACKEND")
# results_backend = Cache(app, config={'CACHE_TYPE': 'redis',          # Use Redis
#                            'CACHE_REDIS_HOST': 'localhost',  # Host, default 'localhost'
#                            'CACHE_REDIS_PORT': 6379,       # Port, default 6379
#                         #    'CACHE_REDIS_PASSWORD': '',  # Password
#                            'CACHE_REDIS_DB': 2})

# Registering sources
module_datasource_map = app.config.get("DEFAULT_MODULE_DS_MAP")
module_datasource_map.update(app.config.get("ADDITIONAL_MODULE_DS_MAP"))
ConnectorRegistry.register_sources(module_datasource_map)

from superset import views  # noqa
from superset.hand import views, models, start
