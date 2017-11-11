# -*- coding: utf-8 -*-
"""
    baka_tenshi
    ~~~~~~~~~~~~~~~~

    Adds basic SQLAlchemy support to your application.

    :copyright: (c) 2017 by Nanang Suryadi.
    :license: BSD, see LICENSE for more details.
"""
import zope.sqlalchemy
from pyramid.settings import asbool
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import sqlalchemy

from baka_tenshi.meta import Base, Model

__all__ = (
    '__version__',
    'Base',
    'Model',
    'DB'
)
__version__ = '1.0.2'


class _TenshiExtensions(object):
    def __init__(self):
        self.descriptors = {}
        self.methods = {}


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


DB = _TenshiExtensions
_include_sqlalchemy(DB)


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, request):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    session = session_factory()
    # If the request has a transaction manager, associate the session with it.
    try:
        tm = request.tm
    except AttributeError:
        pass
    else:
        zope.sqlalchemy.register(
            session, transaction_manager=tm)

    # hy
    # pyramid_tm doesn't always close the database session for us.
    #
    # For example if an exception view accesses the session and causes a new
    # transaction to be opened, pyramid_tm won't close this connection because
    # pyramid_tm's transaction has already ended before exception views are
    # executed.
    # Connections opened by NewResponse and finished callbacks aren't closed by
    # pyramid_tm either.
    #
    # So add our own callback here to make sure db sessions are always closed.
    #
    # See: https://github.com/Pylons/pyramid_tm/issues/40
    @request.add_finished_callback
    def close_the_sqlalchemy_session(request):
        # if session.dirty:
        #     request.sentry.captureMessage('closing a dirty session', stack=True, extra={
        #         'dirty': session.dirty,
        #     })
        session.close()

    return session


def bind_engine(engine,
                base=Base,
                should_create=False,
                should_drop=False):

    base.metadata.bind = engine
    if should_drop:
        base.metadata.reflect(engine)
        base.metadata.drop_all(engine)
    if should_create:
        base.metadata.create_all(engine)


def tm_activate_hook(request):
    if request.path.startswith(("/_debug_toolbar/", "/static/")):
        return False
    return True


def includeme(config):
    """
        Initialize the model for a Pyramid app.

        Activate this setup using ``config.include('baka_tenshi')``.

    """
    settings = config.get_settings()
    tenshi = settings.get('tenshi', {})
    should_create = asbool(tenshi.get('should_create_all', False))
    should_drop = asbool(tenshi.get('should_drop_all', False))

    # Configure the transaction manager to support retrying retryable
    # exceptions. We also register the session factory with the thread-local
    # transaction manager, so that all sessions it creates are registered.
    #    "tm.attempts": 3,
    config.add_settings({
        "retry.attempts": 3,
        "tm.activate_hook": tm_activate_hook,
        "tm.annotate_user": False,
    })

    # use pyramid_retry couse pyramid_tm disabled it
    config.include('pyramid_retry')
    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    config.registry['db_session'] = session_factory

    if tenshi.get('inject', False):
        config.add_ext('session', session_factory)

    # make request.db available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda request: get_tm_session(session_factory, request),
        'db',
        reify=True
    )

    # service model factory
    config.include('.service')

    # Register a deferred action to bind the engine when the configuration is
    # committed. Deferring the action means that this module can be included
    # before model modules without ill effect.
    config.action(None, bind_engine, (engine,), {
        'should_create': should_create,
        'should_drop': should_drop
    }, order=10)
