from pathlib import Path

from aiohttp import web
# {% if database.is_pg_sqlalchemy %}
from aiopg.sa import create_engine
from sqlalchemy.engine.url import URL
# {% endif %}

# {% if template_engine.is_jinja %}
import aiohttp_jinja2
from aiohttp_jinja2 import APP_KEY as JINJA2_APP_KEY
import jinja2
# {% endif %}
# {% if session.is_secure %}
import base64
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
# {% endif %}

from .settings import Settings
# {% if example.is_message_board %}
from .views import index, messages, message_data
# {% else %}
from .views import index
# {% endif %}


THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


# {% if template_engine.is_jinja %}
@jinja2.contextfilter
def reverse_url(context, name, **parts):
    """
    jinja2 filter for generating urls,
    see http://aiohttp.readthedocs.io/en/stable/web.html#reverse-url-constructing-using-named-resources

    Usage:
    {%- raw %}

      {{ 'the-view-name'|url }} might become "/path/to/view"

    or with parts and a query

      {{ 'item-details'|url(id=123, query={'active': 'true'}) }} might become "/items/1?active=true
    {%- endraw %}

    see app/templates.index.jinja for usage.

    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param name: the name of the route
    :param parts: url parts to be passed to route.url(), if parts includes "query" it's removed and passed seperately
    :return: url as generated by app.route[<name>].url(parts=parts, query=query)
    """
    app = context['app']

    kwargs = {}
    if 'query' in parts:
        kwargs['query'] = parts.pop('query')
    if parts:
        kwargs['parts'] = parts
    return app.router[name].url(**kwargs)


@jinja2.contextfilter
def static_url(context, static_file_path):
    """
    jinja2 filter for generating urls for static files. NOTE: heed the warning in create_app about "static_root_url"
    as this filter uses app['static_root_url'].

    Usage:

    {%- raw %}
      {{ 'styles.css'|static }} might become "http://mycdn.example.com/styles.css"
    {%- endraw %}

    see app/templates.index.jinja for usage.

    :param context: see http://jinja.pocoo.org/docs/dev/api/#jinja2.contextfilter
    :param static_file_path: path to static file under static route
    :return: roughly just "<static_root_url>/<static_file_path>"
    """
    app = context['app']
    try:
        static_url = app['static_root_url']
    except KeyError:
        raise RuntimeError('app does not define a static root url "static_root_url"')
    return '{}/{}'.format(static_url.rstrip('/'), static_file_path.lstrip('/'))
# {% endif %}


# {% if database.is_pg_sqlalchemy %}
def pg_dsn(settings: Settings) -> str:
    """
    :param settings: settings including connection settings
    :return: DSN url suitable for sqlalchemy and aiopg.
    """
    return str(URL(
        database=settings.DB_NAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        username=settings.DB_USER,
        drivername='postgres',
    ))


async def startup(app: web.Application):
    app['pg_engine'] = await create_engine(pg_dsn(app['settings']), loop=app.loop)


async def cleanup(app: web.Application):
    app['pg_engine'].close()
    await app['pg_engine'].wait_closed()
# {% endif %}


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    # {% if example.is_message_board %}
    app.router.add_route('*', '/messages', messages, name='messages')
    app.router.add_get('/messages/data', message_data, name='message-data')
    # {% endif %}


def create_app(loop):
    app = web.Application()
    settings = Settings()
    app.update(
        name='{{ name }}',
        settings=settings
    )
    # {% if template_engine.is_jinja %}

    jinja2_loader = jinja2.FileSystemLoader(str(THIS_DIR / 'templates'))
    aiohttp_jinja2.setup(app, loader=jinja2_loader, app_key=JINJA2_APP_KEY)
    app[JINJA2_APP_KEY].filters.update(
        url=reverse_url,
        static=static_url,
    )
    # {% endif %}
    # {% if database.is_pg_sqlalchemy %}

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    # {% endif %}
    # {% if session.is_secure %}

    secret_key = base64.urlsafe_b64decode(settings.COOKIE_SECRET)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))
    # {% endif %}

    setup_routes(app)
    return app
