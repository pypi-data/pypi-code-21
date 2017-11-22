"""
@file
@brief Defines handlers for a Tornado application.
"""
import logging
import pprint
from tornado.web import RequestHandler
import tornado.web


class _BaseRequestHandler(RequestHandler):
    """
    Base handler. Returns the user.
    """

    def __init__(self, application, request, **kwargs):
        """
        Constructor.
        See `web.py <https://github.com/tornadoweb/tornado/blob/master/tornado/web.py>`_.
        """
        if 'ut_logged' in kwargs:
            # For unit test, we impose a logged user.
            self._logged_user = kwargs['ut_logged']['user']
            del kwargs['ut_logged']
        if 'dbman' in kwargs:
            self._db = kwargs['dbman']
            del kwargs['dbman']
        RequestHandler.__init__(self, application, request, **kwargs)
        self._app_log = logging.getLogger("tornado.application")

    def info(self, message):
        """
        Log information.
        """
        self._app_log.info('[{0}] {1}'.format(
            self.__class__.__name__, message))

    def get_current_user(self):
        """
        Returns the current user.
        """
        if hasattr(self, '_logged_user'):
            res = {'user': self._logged_user}
        else:
            res = self.get_secure_cookie("user")
            if isinstance(res, bytes):
                res = {'user': res.decode('utf-8')}
        self.info('user={0}'.format(res))
        return res


class _TemplateHandler(_BaseRequestHandler):
    """
    Defines the main page handler.
    """

    def __init__(self, application, tmpl_name, request, **kwargs):
        """
        Constructor.
        See `web.py <https://github.com/tornadoweb/tornado/blob/master/tornado/web.py>`_.

        @param  tmpl_name   template name
        @param  context     additional context for the template
        """
        tmpl, torn = self._process_kwargs(kwargs)
        _BaseRequestHandler.__init__(self, application, request, **torn)
        self._tmpl_name = "templates/{0}".format(tmpl_name)
        self._tmpl_context = {'style': '/static/style.css',
                              'icon': '/static/icon.ico',
                              'image': '/static/icon.png'}
        self._tmpl_context.update(tmpl)
        self.info("template='{0}'".format(self._tmpl_name))
        self.info("kwargs={0}".format(torn))
        self.info("context={0}".format(self._tmpl_context))

    def _process_kwargs(self, kwargs):
        """
        Separates attributes templates / tornado.

        @param      kwargs      attributes
        @return                 attributes for temples, attributes for tornado

        An attributes for the template is prefixed with ``'tmpl_'``.
        """
        tmpl = {}
        torn = {}
        for k, v in kwargs.items():
            if k.startswith("tmpl_"):
                tmpl[k[5:]] = v
            else:
                torn[k] = v
        return tmpl, torn

    @tornado.web.authenticated
    def get(self):
        """
        Returns the content page.
        """
        return self.render(self._tmpl_name, **self._tmpl_context)


class LogoutHandler(_TemplateHandler):
    """
    Logout Handler.
    """

    def __init__(self, application, request, **kwargs):
        """
        Expected additional parameters:

        * tmpl_title: application title
        """
        _TemplateHandler.__init__(
            self, application, "unused", request, **kwargs)

    @tornado.web.authenticated
    def get(self):
        """
        Page.
        """
        self.info("logout {0}".format(self.get_current_user()))
        self.clear_cookie("user")
        self.redirect("/")


class LoginHandler(_TemplateHandler):
    """
    Login Handler.
    """

    def __init__(self, application, request, **kwargs):
        """
        Expected additional parameters:

        * title: application title
        """
        users = kwargs.get('users')
        if users is None:
            raise ValueError("No users was defined.\n{0}".format(
                pprint.pformat(kwargs)))
        del kwargs['users']
        _TemplateHandler.__init__(self, application, "login.{0}.html".format(kwargs.get('lang', 'fr')),
                                  request, **kwargs)
        self._users = users
        if not isinstance(users, dict):
            raise TypeError(
                "users must be a dictionary not {0}.".format(type(users)))
        if hasattr(self, '_logged_user'):
            self.set_current_user(self._logged_user)

    @tornado.gen.coroutine
    def get(self):
        """
        Page.
        """
        self.info('processing GET')
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 20:
            self.write('<center>blocked</center>')
            return
        return self.render(self._tmpl_name, **self._tmpl_context)

    def set_current_user(self, user):
        """
        Sets the current user or clear the cookie if None.
        """
        if user:
            self.info("set user '{0}'".format(user))
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

    @tornado.gen.coroutine
    def post(self):
        self.info('processing POST')
        self.info(str(self.request.arguments))
        self.info(str(self.request.headers))
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 20:
            self.write('<center>blocked</center>')
            return

        getusername = tornado.escape.xhtml_escape(
            self.get_argument("username"))
        getpassword = tornado.escape.xhtml_escape(
            self.get_argument("password"))
        self.info("login='{0}'".format(getusername))
        self.info("nb users={0}".format(len(self._users)))
        if getusername in self._users:
            val = self._users[getusername]
            if isinstance(val, dict):
                goodpwd = val['pwd'] == getpassword
            else:
                goodpwd = self._users[getusername] == getpassword
        if goodpwd:
            self.set_current_user(getusername)
            self.set_secure_cookie("incorrect", "0")
            self.redirect("/")
        else:
            incorrect = self.get_secure_cookie("incorrect") or 0
            increased = str(int(incorrect) + 1)
            self.set_secure_cookie("incorrect", increased)
            self.set_current_user(None)
            self.write("""<center>
                            Something Wrong With Login<br />
                            <a href="/login">Try Again</a>
                          </center>""")


class MainHandler(_TemplateHandler):
    """
    Handlers for the main page.
    """

    def __init__(self, application, request, **kwargs):
        """
        Constructor.
        """
        _TemplateHandler.__init__(
            self, application, "index.{0}.html".format(
                kwargs.get('lang', 'fr')),
            request, **kwargs)


class SubmitForm(_TemplateHandler):
    """
    Handlers for the form to upload dataset.
    """

    def __init__(self, application, request, **kwargs):
        """
        Constructor.
        """
        _TemplateHandler.__init__(
            self, application, "submit.{0}.html".format(
                kwargs.get('lang', 'fr')),
            request, **kwargs)
        val = self.get_argument('cpt_value', None)
        if val is None:
            raise ValueError(
                "cpt_value is not defined in the list of arguments.")
        self._tmpl_context['cpt_value'] = val
        self._tmpl_context['cptidname'] = self._db.get_competitions()


class UploadData(_TemplateHandler):
    """
    Upload data.
    """
    """
    Handlers for the form to upload dataset.
    """

    def __init__(self, application, request, **kwargs):
        """
        Constructor.
        """
        _TemplateHandler.__init__(
            self, application, "waiting.{0}.html".format(
                kwargs.get('lang', 'fr')),
            request, **kwargs)
        self._tmpl_context['waitgif'] = "/static/giphy.gif"

    @tornado.gen.coroutine
    def post(self):
        fileinfo = self.request.files['filearg'][0]
        self.info("fileinfo={0}".format(fileinfo))
        fname = fileinfo['filename']
        self.info("filename='{0}'".format(fname))
        content = fileinfo['body']
        self.info("downloaded size={0}".format(len(content)))


class CompetitionHandler(_TemplateHandler):
    """
    Handlers for the page on competitions.
    """

    def __init__(self, application, request, **kwargs):
        """
        Constructor.
        """
        _TemplateHandler.__init__(
            self, application, "challenge.{0}.html".format(
                kwargs.get('lang', 'fr')),
            request, **kwargs)
        val = self.get_argument('cpt_id', None)
        if val is None:
            raise ValueError(
                "cpt_id is not defined in the list of arguments.")
        self._tmpl_context['cpt'] = self._db.get_competition(val)
        self._tmpl_context['results'] = self._db.get_results(val)
