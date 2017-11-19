"""
@file
@brief Defines a Tornado application.
Tutorial `chat <https://github.com/tornadoweb/tornado/tree/stable/demos/chat>`_.
"""
import logging
import os
import pprint
from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.log import enable_pretty_logging
from .handlersml import MainHandler, LoginHandler, LogoutHandler, UploadData, SubmitForm, CompetitionHandler
from .default_options import LightMLBoardDefaultOptions
from .options_helpers import read_options, read_users
from .dbmanager import DatabaseCompetition


class LightMLBoard(Application):
    """
    Overloads a :epkg:`tornado:Application`.
    """

    def __init__(self, handlers=None, default_host=None, transforms=None,
                 **settings):
        """
        Constructor.
        See `wep.py <https://github.com/tornadoweb/tornado/blob/master/tornado/web.py>`_.
        """
        if "login_url" not in settings:
            settings['login_url'] = "/login"
        if "xsrf_cookies" not in settings:
            settings["xsrf_cookies"] = True

        Application.__init__(self, handlers=handlers, default_host=default_host,
                             transforms=transforms, **settings)
        app_log = logging.getLogger("tornado.application")
        app_log.info('[LightMLBoard] Settings: {0}'.format(settings))

    def update_options(config_options):
        """
        Returns updated options, includes the default ones.
        """
        context = {}
        lang = None
        debug = False
        cookie_secret = None
        enablelog = False
        for opts in [LightMLBoardDefaultOptions.__dict__,
                     config_options]:
            for k, v in opts.items():
                if not k.startswith("_"):
                    if k == 'cookie_secret':
                        cookie_secret = v
                    elif k == "lang":
                        lang = v
                    elif k == "debug":
                        debug = debug
                    elif k == "logging":
                        enablelog = v
                    elif k == "allowed_users":
                        context[k] = v
                    else:
                        context["tmpl_" + k] = v
        app_options = dict(lang=lang, debug=debug, enablelog=enablelog,
                           cookie_secret=cookie_secret)
        return context, app_options

    @staticmethod
    def make_app(config=None, logged=None, dbfile=":memory:"):
        """
        Creates a *LightMLBoard* application.

        @param      config      configuration file
        @param      logged      to log one user
        @param      dbfile      file for the db file
        @return                 @see cl LightMLBoard
        """
        this = os.path.dirname(__file__)
        st = os.path.join(this, "static")

        # Update the context for static files.
        updated_context = {'path': st}

        # Options.
        config_options = read_options(config)
        context, local_context = LightMLBoard.update_options(config_options)
        allowed = context["allowed_users"]
        if allowed is None:
            raise ValueError("No allowed users.\n{0}".format(
                pprint.pformat(context)))
        users = read_users(allowed)

        # db manager
        if config is not None:
            dbman = DatabaseCompetition(dbfile)
            dbman.init_from_options(context)
            context['dbman'] = dbman

        # We remove the users.
        del context['allowed_users']

        # Specifies a logged user.
        if logged:
            context["ut_logged"] = logged
            updated_context["ut_logged"] = logged

        context_users = context.copy()
        context_users['users'] = users

        # Logging.
        if local_context['debug'] or local_context['enablelog']:
            enable_pretty_logging()

        pages = [
            (r"/", MainHandler, context),
            (r'/login', LoginHandler, context_users),
            (r'/logout', LogoutHandler, context),
            (r'/static/(.*)', StaticFileHandler, updated_context),
            (r'/submit', SubmitForm, context),
            (r'/upload', UploadData, context),
            (r'/competition', CompetitionHandler, context),
        ]

        args = dict(lang=local_context["lang"], debug=local_context['debug'])
        if 'cookie_secret' in local_context:
            args['cookie_secret'] = local_context['cookie_secret']
        return LightMLBoard(pages, **args)

    @staticmethod
    def start_app(port=8897, **kwargs):
        """
        Starts the application.

        @param      port        port to listen
        @param      kwargs      @see me make_app
        """
        import tornado.ioloop
        app = LightMLBoard.make_app(**kwargs)
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()
