PLUGIN = {}
IMPORT_HOOKS = {}



DEFINICATION = {
    'plugin': [
        ('', 'instrument_plugin'),
    ],
    'httpc_httplib': [
        ('httplib', 'instrument_httplib'),
        ('http.client', 'instrument_httplib'),
        ('httplib2', 'instrument_httplib2'),
    ],
    'httpc_requests': [
        ('requests.sessions', 'instrument_requests'),
    ],
    'httpc_urllib3': [
        ('urllib3.request', 'instrument_urllib3'),
        # ('requests.packages.urllib3.request', 'instrument_urllib3'),
    ],
    'database_mysql': [
        ('MySQLdb', 'instrument_MySQLdb'),
        ('MySQLdb.cursors', 'instrument_MySQLdb_cursors'),
        ('pymysql', 'instrument_pymysql'),
    ],
    'database_postgresql': [
        ('psycopg2', 'instrument_psycopg2'),
        ('psycopg2._psycopg', 'instrument_psycopg2_connection'),
        ('psycopg2.extensions', 'instrument_psycopg2_extensions'),
    ],
    'database_toolkit': [
        ('sqlalchemy.orm.session', 'instrument_sqlalchemy'),
    ],
    'application_wsgi': [
        ('', ''),
    ],
    'application_bottle': [
        ('bottle', 'instrument'),
    ],
    'application_cherrypy': [
        ('cherrypy', 'instrument'),
    ],
    'application_django': [
        ('django.core.handlers.wsgi', 'instrument'),
        ('django.core.handlers.base', 'instrument_handlers_base'),
        ('django.views.generic.base', 'instrument_generic_base'),
        # Django==1.10
        ('django.urls.resolvers', 'instrument_url_resolvers', False),
        ('django.urls.base', 'instrument_urls_base', False),
        ('django.core.handlers.exception', 'instrument_handlers_exception',
         False),
    ],
    'application_flask': [
        ('flask', 'instrument'),
    ],
    'application_tornado': [
        ('tornado.web', 'instrument'),
    ]
}
