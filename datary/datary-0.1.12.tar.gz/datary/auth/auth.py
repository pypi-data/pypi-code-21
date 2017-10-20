# -*- coding: utf-8 -*-
"""
Datary sdk Auth File
"""
from urllib.parse import urljoin
from datary.requests import DataryRequests
import structlog

logger = structlog.getLogger(__name__)


class DataryAuth(DataryRequests):
    """
    Class DataryAuth
    """

    def __init__(self, **kwargs):
        """
        DataryAuth Init method
        """
        super(DataryAuth, self).__init__(**kwargs)
        self._username = kwargs.get('username', '')
        self._password = kwargs.get('password', '')
        self._token = kwargs.get('token', '')
        self._commit_limit = int(kwargs.get('commit_limit', 30))

        # call to sign-in
        self.sign_in()

    @property
    def username(self):
        """
        Username getter
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Username setter
        """
        self._username = username

    @property
    def password(self):
        """
        Password getter
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Password setter
        """
        self._password = password

    @property
    def token(self):
        """
        Token getter
        """
        return self._token

    @token.setter
    def token(self, token):
        """
        Token setter
        """
        self._token = token
        self.attach_token_header()

    @property
    def commit_limit(self):
        """
        Commit_limit getter
        """
        return self._commit_limit

    @commit_limit.setter
    def commit_limit(self, commit_limit):
        """
        Commit_limit setter
        """
        self._commit_limit = commit_limit

    def attach_token_header(self):
        """
        Class method to attach datary token to requests headers.
        """
        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)

    def get_user_token(self, user=None, password=None):
        """
        ===========   =============   ================================
        Parameter     Type            Description
        ===========   =============   ================================
        user          str             Datary username
        password      str             Datary password
        ===========   =============   ================================

        Returns:
            (str) User's token given a username and password.
        """

        payload = {
            "username": user or self.username,
            "password": password or self.password,
        }

        url = urljoin(self.URL_BASE, "/connection/signIn")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.request(
            url, 'POST', **{'headers': self.headers, 'data': payload})

        # Devuelve el token del usuario.
        user_token = str(response.headers.get("x-set-token", ''))

        return user_token

    def sign_in(self):
        """
        Sign-in and assert has a token in requests headers.
        """

        if self.token:
            self.attach_token_header()

        elif self.username and self.password:
            self.token = self.get_user_token()
            self.attach_token_header()

        else:
            logger.error(
                'Can`t sign-in, useraname or password incorrect',
                username=self.username,
                password=self.password)

    def sign_out(self):
        """
        Sign-out and invalidate the actual token.

        """
        url = urljoin(self.URL_BASE, "connection/signOut")

        # Make sign_out request.
        response = self.request(url, 'GET')

        if response:
            self.token = None
            logger.info('Sign Out Succesfull!')

        else:
            logger.error(
                "Fail to make Sign Out succesfully :(",
                response=response)
