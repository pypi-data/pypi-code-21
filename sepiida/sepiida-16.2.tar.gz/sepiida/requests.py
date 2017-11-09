import collections
import logging
import re
import threading
import time
from urllib import parse

import flask
import requests
import requests.auth
import sepiida.context
import sepiida.environment
import sepiida.errors
import sepiida.session

LOGGER = logging.getLogger(__name__)

Request = collections.namedtuple('Request', ('method', 'url', 'params', 'data'))

class TrackedSession(requests.Session):
    "A requests Session that tracks requests that are made"
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay    = 0
        self.name     = name
        self.requests = []

    def cleanup(self):
        LOGGER.info("Made %d %s requests with %s seconds total delay", len(self.requests), self.name, self.delay)

    def request(self, method, url, *args, params=None, data=None, **kwargs): # pylint: disable=arguments-differ
        if not hasattr(self, 'requests'):
            LOGGER.warning("Somehow our tracked session does not have a list of requests. Re-creating that list")
            self.requests = []
        self.requests.append(Request(
            data    = data,
            method  = method,
            params  = params,
            url     = url,
        ))
        start = time.time()
        try:
            return super().request(method, url, *args, params=params, data=data, **kwargs)
        finally:
            if not hasattr(self, 'delay'):
                self.delay = 0
            self.delay += time.time() - start

SESSIONS = threading.local()
def add_request_handler(app):
    "Adds hooks to an app to keep track of the external requests it makes"
    def _clear_user_session():
        SESSIONS.privileged_session          = None
        SESSIONS.user_session                = None
    def _show_session_usage(response):
        if hasattr(SESSIONS, 'privileged_session') and SESSIONS.privileged_session:
            SESSIONS.privileged_session.cleanup()
        if hasattr(SESSIONS, 'user_session') and SESSIONS.user_session:
            SESSIONS.user_session.cleanup()
        return response
    app.before_request(_clear_user_session)
    app.after_request(_show_session_usage)
    user_session.reuse = True
    privileged_session.reuse = True

def remove_request_handler():
    "Only used for test cleanup, this just undoes all the work of add_request_handler"
    user_session.reuse = False
    privileged_session.reuse = False
    if hasattr(SESSIONS, 'privileged_session'):
        del SESSIONS.privileged_session
    if hasattr(SESSIONS, 'user_session'):
        del SESSIONS.user_session

def user_session(username=None, password=None, session=None, user=None):
    current_session = getattr(SESSIONS, 'user_session', None)
    if current_session and user_session.reuse:
        return current_session
    if not any([username, password, session, user]):
        if flask.has_request_context():
            credentials = sepiida.context.extract_credentials(flask.request)
            password    = credentials['password']
            session     = credentials['session']
            user        = credentials['user']
            username    = credentials['username']
        elif sepiida.backend.has_task_context():
            credentials = sepiida.backend.task_credentials()
            password    = credentials['password']
            session     = credentials['session']
            user        = credentials['user']
            username    = credentials['username']
        else:
            msg = ("You have attempted to create a user session without having a flask request context or a backend task context. "
                   "You must therefore supply your own credentials as parameters")
            raise Exception(msg)

    _user_session = TrackedSession('user_session')
    if username and password:
        LOGGER.debug("Using credentials %s %s for user session", username, password)
        _user_session.auth = requests.auth.HTTPBasicAuth(username, password)
    elif session:
        LOGGER.debug("Passing through session token")
        _user_session.cookies['session'] = session
    else:
        LOGGER.warning("User session requested, but I have no session data to use")
    _user_session.headers.update({'Request-ID': sepiida.session.current_request_id()})
    if hasattr(SESSIONS, 'user_session'):
        SESSIONS.user_session = _user_session
    return _user_session
user_session.reuse = False

class PrivilegedAuth(requests.auth.HTTPBasicAuth):
    def __call__(self, prepared_request):
        prepared_request = super(PrivilegedAuth, self).__call__(prepared_request)
        parts = parse.urlsplit(prepared_request.url)
        domains = sepiida.environment.get().TRUSTED_DOMAINS
        domains = '|'.join([re.escape(domain) for domain in domains])
        domains_regex = r'(.*)?\.({0})$'.format(domains)
        if not parts.scheme == 'https':
            raise InvalidPrivilegedScheme()
        if not re.fullmatch(domains_regex, parts.netloc):
            raise InvalidPrivilegedDomain()

        return prepared_request

def privileged_session(api_token=None):
    settings = sepiida.environment.get()
    current_session = getattr(SESSIONS, 'privileged_session', None)
    if current_session and privileged_session.reuse:
        return SESSIONS.privileged_session
    if not api_token:
        api_token = settings.API_TOKEN

    _session = TrackedSession('privileged_session')
    _session.auth = PrivilegedAuth('api', api_token)
    _session.headers.update({'Request-ID': sepiida.session.current_request_id()})
    if hasattr(SESSIONS, 'privileged_session'):
        SESSIONS.privileged_session = _session
    return _session
privileged_session.reuse = False

class InvalidPrivilegedDomain(sepiida.errors.Error):
    def __init__(self):
        super(
            InvalidPrivilegedDomain,
            self,
        ).__init__(
            "Privileged domain must be trusted",
            "invalid-privileged-domain"
        )

class InvalidPrivilegedScheme(sepiida.errors.Error):
    def __init__(self):
        super(
            InvalidPrivilegedScheme,
            self,
        ).__init__(
            "Privileged request requires https",
            "invalid-privileged-sheme"
        )
