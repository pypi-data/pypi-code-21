# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import getpass
import json
import os
import os.path
import sys

class _CredentialGetter:
    @staticmethod
    def _get_password_file():
        # store password file outside of the source directory
        PASSWORD_FILE = '.eureqa_passwd'
        path = os.path.expanduser("~")
        return path + '/' + PASSWORD_FILE

    @classmethod
    def _clear_passwords(cls):
        try: os.remove(cls._get_password_file())
        except: return

    @classmethod
    def _load_passwords(cls):
        try:
            with open(cls._get_password_file(), 'rb') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def login_timestamp(login):
        try:
            return datetime.datetime(login['last_used'])
        except:
            return datetime.datetime(2000, 1, 1)

    @classmethod
    def _find_login(cls, data, url, username=None):
        if url not in data: return None

        max_date = None
        max_date_i = None
        for i, login in enumerate(data[url]):
            if username and login['username'] != username:
                continue
            date = cls.login_timestamp(login)
            if not max_date or date > max_date:
                max_date = date
                max_date_i = i
        return max_date_i

    @staticmethod
    def _prompt_username():
        username = raw_input('ENTER USERNAME: ')
        if not username:
            raise Exception('Login cancelled by user')
        return username

    @staticmethod
    def _prompt_password_spyder():
        return raw_input('ENTER PASSWORD: ').encode('base64')

    @staticmethod
    def _prompt_password():
        if any('SPYDER' in name for name in os.environ) or 'pythonw.exe' in sys.executable:
            password = _prompt_password_spyder()
        else:
            password = getpass.getpass('ENTER PASSWORD: ').encode('base64')
        if not password: raise Exception('Login cancelled by user')
        return password

    ### MAIN FUNCTIONALITY: ###

    @staticmethod
    def prompt_one_time_password(login):
        password = raw_input('ENTER ONE_TIME PASSWORD SENT BY SMS: ')
        if not password: raise Exception('Login cancelled by user')
        login['one_time_password'] = password
        return login

    @classmethod
    def store_login(cls, url, login):
        """Saves login credentials to they are used automatically next time.
        Credentials are saved to a file your home directory.

        :param str url: URL to login destination.
        :param dict login: Login credentials as dictionary.
        """
        if login.has_key('one_time_password'): del login['one_time_password']
        data = cls._load_passwords()
        if url not in data: data[url] = []
        login['last_used'] = str(datetime.datetime.now())
        index = cls._find_login(data, url, login['username'])
        if index is None:
            data[url].append(login)
        else:
            data[url][index] = login
        with open(cls._get_password_file(), 'wb') as f:
            json.dump(data, f, indent=4, default=str)

    @classmethod
    def get_login(cls, url, username=None, password=None, key=None, force_prompt=False):
        """Returns (username, password) for a Eureqa SaaS url and prompts user for
        credentials if not found. Passwords should be base64 encoded.

        :param str url: URL for login connection.
        :param str username: Login username or most recently used if not provided.
        :param str password: Password for login.
        :param str key: Access key for login.  This is the preferred method.
        :param bool force_prompt: Whether the user will always be prompted to enter credentials.

        """
        data = cls._load_passwords()

        index = cls._find_login(data, url, username)
        login = data[url][index] if index is not None and (username is None or password is None) else {'username': username, 'password': password}
        if key:
            login['key'] = key

        ask_username = force_prompt or not login['username']
        ask_password = (force_prompt or not login['password']) and not key

        if ask_username or ask_password: print('PLEASE LOGIN,')
        if ask_username:
            login['username'] = cls._prompt_username()
        elif ask_password:
            print('LOGGING IN WITH USERNAME: ' + login['username'])
        if ask_password: login['password'] = cls._prompt_password()

        if login.has_key('one_time_password'): del login['one_time_password']

        return login

