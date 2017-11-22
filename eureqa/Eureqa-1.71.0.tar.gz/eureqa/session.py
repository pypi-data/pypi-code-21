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

import sys
import requests
import json
import time
import warnings

from versions import API_VERSION
from passwords import _CredentialGetter
from utils import utils

def sanitize_name(name):
    #return re.sub(r'[^A-Za-z0-9._]+', '_', name)
    return name

class Http504Exception(Exception):
    pass

class Http404Exception(Exception):
    pass

class Http400Exception(Exception):
    def __init__(self, body):
        try:
            body_json = json.loads(body)
            message = body_json['message']
        except:
            body_json = {}
            message = body
        if 'details' in body_json:
            self.message = message + body_json['details']
        super(Exception, self).__init__(message)

class _Session:

    def __init__(self, url, user, password, key, verbose, save_credentials, organization, verify_ssl_certificate,
                 retries, timeout_seconds, session_key, interactive_mode):
        """
        Create a new Session object

        Arguments:
            session_key (string): Existing session key

        """
        self.url = url
        self.organization = organization
        self.verbose = verbose
        self.interactive_mode= interactive_mode
        self._session = requests.session()
        self._session.headers["X-nu-api"] = str(API_VERSION)
        self._session.verify = verify_ssl_certificate
        if not verify_ssl_certificate:
            # It is OK to disable warnings because user know what he or she is doing
            # because they explicitly asked to disable SSL verification.
            try:
                requests.packages.urllib3.disable_warnings()
            except Exception:
                warnings.warn("Unable to disable SSL warnings.  Extraneous warnings may be printed.  Try upgrading your 'requests' package.")
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        if session_key is None:
            self._login(user, password, key, save_credentials, organization)
        else:
            self.user = user
            self._set_cookies(user, session_key)
        self._last_response = None

    def _is_root(self): return self.user == "root"

    def execute(self, endpoint, method='POST',args=None, files=None, raw_data=None, raw_returnfile=None, raw_return=False, raw_url=False):
        """Internal function to send a request to the Kerpler instance.

        Arguments:
            endpoint (string): The directory and point to execute on (e.g. '/data1/search3/start')
            method   (string): Type of request, should be 'GET', 'PUT', 'POST', or 'DELETE'
            args     (dict):   The command arguements and values (e.g. { 'start_row':2, 'row_count':10 })
            files    (dict):   Any files to be sent, example: files={'file': open('report.csv', 'rb')}
            raw_data (str):    A JSON string which will be included in a PUT/POST
            raw_return (bool): Return the data as a raw bytestring (str())
            raw_returnfile (str): Optional filepath to save results to
            raw_url (bool):    Treat the URL as-is; don't attempt to prepend '/api' or do other convenience normalization

        Returns:
            The response JSON on success (raises exception otherwise)
        """

        if not endpoint.startswith('/api/v2/') and not raw_url:
            if endpoint.startswith('/api/'):
                api_pos = len('/api/')
                endpoint = endpoint[:api_pos] + 'v2/' + endpoint[api_pos:]
            else:
                endpoint = '/api/v2/%s%s' % (self.organization, endpoint)

        if self.verbose:
            print endpoint

        if self.verbose:
            msg = "\n%4s %s %s" % (method, self.url, endpoint)
            if args:     msg += ' ARGS='     + json.dumps(args, default=str)
            if files:    msg += ' FILES='    + str(files)
            if raw_data: msg += ' RAW_DATA=' + str(raw_data)
            #print(msg[:1000])

        if args and raw_data: raise Exception('Cannot specify both data and raw data')

        url  = self.url + endpoint
        data = None
        if raw_data is not None:
            data = raw_data
        elif args is not None:
            data = json.dumps(args, default=str)

        try:
            if   method == 'GET':    r = self._retry(lambda :self._session.get(url, params=args, timeout=self._timeout_seconds, stream=True))
            elif method == 'PUT':    r = self._retry(lambda :self._session.put(url, data=data, files=files, timeout=self._timeout_seconds, stream=True))
            elif method == 'POST':   r = self._retry(lambda :self._session.post(url, data=data, files=files, timeout=self._timeout_seconds, stream=True))
            elif method == 'DELETE': r = self._retry(lambda :self._session.delete(url, params=args, timeout=self._timeout_seconds, stream=True))
            else: raise Exception('Unknown request method: '+method)
        except requests.exceptions.ConnectionError as e:
            print('COULD NOT SEND REQUEST TO SERVER. Check if the web UI is reachable and the server is operational.')
            raise e

        # save response object for debug
        self._last_response = r

        if r.status_code == 504: raise Http504Exception('%s request to URL \'%s\' timed out' % (method, url))
        if r.status_code == 404: raise Http404Exception('URL \'%s\' is not found: \n%s' % (url, r.text.encode('utf-8')))
        if r.status_code == 400: raise Http400Exception(r.text)
        if r.status_code != 200: raise Exception('Request unsuccessful (status code %i):\n%s' % (r.status_code, str(r.text)))

        # optionally save to a file
        # do this before logging the response body -- if we're saving to a file, we stream the body, so we don't want to log it
        if raw_returnfile:
            if self.verbose: print('RESPONSE ' + str(r.status_code) + ' (written to ' + repr(raw_returnfile) + ')')
            with open(raw_returnfile, 'wb') as fd:
                for chunk in r.iter_content(20):
                    fd.write(chunk)
            return

        r.raw.decode_content = True
        page_text = r.raw.read()
        if self.verbose: print('RESPONSE ' + str(r.status_code) + ':\n' + page_text[:1000] + '\n')

        # optionally return raw bytes
        if raw_return:
            return page_text

        try:
            json_value = json.loads(page_text)
            if isinstance(json_value, dict) and json_value.get('warnings'):
                for w in json_value['warnings']:
                    warnings.warn(w)
            return json_value
        except ValueError:
            return page_text

    def _retry(self, function):
        retries_left = self._retries
        while True:
            try:
                return function()
            except:
                if(retries_left == 0):
                    raise
                time.sleep(1)
                retries_left -= 1

    def _get_user_details(self, user):
        """Get details for a user"""
        self.report_progress('Getting details for user: \'%s\'.' % user)
        result = self.execute('/api/v2/auth/user/' + utils.quote(user), 'GET')
        return result

    def _login(self, user_name=None, password=None, key=None, save_credentials=False, organization=None):
        """Login to a Eureqa instance and store session cookie and organization."""

        if password:
            password = password.encode('base64')

        # lookup or prompt for username/password
        login = _CredentialGetter.get_login(self.url, user_name, password, key)

        try_again = True
        while try_again:
            try:
                self.report_progress('Logging in as user: \'%s\'.' % login.get('username'))
                result = self.execute('/api/v2/auth/login', 'POST', login)
                self._set_cookies(login.get('username'), result['session_key'])
                try_again = False
            except requests.exceptions.ConnectionError as e:
                raise e
            except Exception as e:
                if self.interactive_mode == False:
                    raise e
                elif "two_factor_auth_expected_one_time_password" in e.message:
                    login = _CredentialGetter.prompt_one_time_password(login)
                elif "two_factor_auth_incorrect_one_time_password" in e.message:
                    print e
                    print('\nINCORRECT ONE-TIME PASSWORD. TRY AGAIN OR HIT [ENTER] TO QUIT.\n')
                    login = _CredentialGetter.prompt_one_time_password(login)
                else:
                    print e
                    print('\nLOGIN FAILED. TRY AGAIN OR HIT [ENTER] TO QUIT.\n')
                    login = _CredentialGetter.get_login(self.url, user_name, password, force_prompt=True)

        if save_credentials:
            _CredentialGetter.store_login(self.url, login)

        # get the organization
        user_details_obj = self._get_user_details(login['username'])
        if organization==None:
            self.organization = user_details_obj['organizations'][0] # use first organization
        else:
            self.organization=organization

        self.user = login['username']

    def _set_cookies(self, user_name, session_key):
        """ Set http request cookies for username and session_key """
        cookies = {
            'ncloud_session_key': session_key,
            #Need to pass user name as a cookie, because currently
            #backend misses logic that can infer the current user name
            #from the session data. So it uses value from the cookie.
            'nu_user': user_name.encode('base64')
            #encode('base64') adds trailing new line symbol
            #but the REST end-point does not expect it.
            .rstrip('\n')
        }
        self._session.cookies = requests.utils.cookiejar_from_dict(cookies)


    def _get_session_key(self):
        return self._session.cookies.get('ncloud_session_key')

    def report_progress(self, message, warning=False):
        if warning:
            print >> sys.stderr, "Warning:", message
        elif self.verbose:
            print message

    def report_warning(self, message): self.report_progress(message, warning=True)
