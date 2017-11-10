import hashlib
import sys


import requests


from .base import NanoBase


if sys.version_info < (3, 0, 0):
    # We're on Py2, get Py3-style super()
    from builtins import super


class User(NanoBase):
    """
    A NanoBase object for representing NaNoWriMo participants.
    """
    # Endpoint URLs for user objects
    _primary_url = 'https://nanowrimo.org/wordcount_api/wc/{name}'
    _history_url = 'https://nanowrimo.org/wordcount_api/wchistory/{name}'
    _writeapi_url = 'https://nanowrimo.org/api/wordcount'

    __secret_key = None

    def __init__(self, name, secret_key=None, **kwargs):
        super().__init__(name, **kwargs)

        self.secret_key = secret_key

    @property
    def id(self):
        """The User's id.

        This property corresponds to `uid` in the API.

        :rtype: string
        """
        return self._fetch_element('uid')

    @property
    def name(self):
        """The User's username.

        This property corresponds to `uname` in the API.

        :rtype: string
        """
        return self._fetch_element('uname')

    @property
    def wordcount(self):
        """The User's current word count.

        This property corresponds to `user_wordcount` in the API.

        :rtype: int
        """
        return int(self._fetch_element('user_wordcount'))

    @wordcount.setter
    def wordcount(self, val):
        """Update the User's current word count.

        This uses the NaNoWriMo WriteAPI and the User's `secret_key` to update
        the wordcount on the NaNoWriMo website.

        :param int val: The User's new word count
        """
        if self.secret_key is None:
            raise ValueError('secret_key must be set before wordcount can be')

        if val != self.wordcount:
            val = int(val)
            name = self.name
            key = self.__secret_key

            h = hashlib.sha1()
            h.update(key.encode())
            h.update(name.encode())
            h.update(str(val).encode())

            data = {
                'hash': h.hexdigest(),
                'name': name,
                'wordcount': val,
            }

            r = requests.put(self._writeapi_url, data=data)

            if not r.ok:
                r.raise_for_status()

    @property
    def winner(self):
        """The User's "winner" status.

        This property corresponds to `winner` in the API.

        :rtype: bool
        """
        return self._fetch_element('winner') == 'true'

    @property
    def secret_key(self):
        """The User's WriteAPI key.

        This is not actually returned; if the key has been set you will get a
        string of '*' characters. Returns None if no key has been set.

        :rtype: string
        """
        if self.__secret_key is not None:
            return '*' * len(self.__secret_key)

        return None

    @secret_key.setter
    def secret_key(self, val):
        """Set the User's WriteAPI key.

        :param string val: The User's WriteAPI secret key
        """
        self.__secret_key = val

