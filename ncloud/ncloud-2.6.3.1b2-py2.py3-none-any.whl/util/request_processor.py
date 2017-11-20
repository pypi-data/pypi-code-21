# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Helpers for making an API call
"""
from builtins import str
from collections import OrderedDict
from conditional import conditional
from functools import partial
import json
import logging
import os
import requests
import sys
import time

from ncloud.config import REQUEST_RETRIES, SSL_CERT_VERIFICATION
from ncloud.formatting.output import print_error, RequestError
from ncloud import __version__


class NcloudRequest(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self._stdout = sys.stdout
        self._reset_request_counter()

    def make_call(self, config, endpoint, method="GET", data=None,
                  params=None, files=None, headers={}, stream=False,
                  session=None, return_status_code=False, token_needed=True,
                  console_log_follow=False, add_ncloud_data=True,
                  return_json=False, hide_output=True):
        partial_api_call = partial(
            self.api_call, config, endpoint, method, data, params, files,
            headers, stream, session, return_status_code, token_needed,
            console_log_follow, add_ncloud_data)
        tries = 0
        results = None
        with conditional(hide_output, open(os.devnull, 'wb')) as null:
            self.devnull = null
            # capture stdout so as to hide the helium fail message
            self._stdout = sys.stdout
            while tries < self.request_retries:
                tries += 1
                if null:
                    sys.stdout = null
                # if helium isn't up yet, ncloud will sys exit
                try:
                    results = partial_api_call()
                except SystemExit:
                    sys.stdout = self._stdout
                    print("Server not responding...Retrying {}/{}"
                          .format(tries, self.request_retries))
                    time.sleep(3)
                    continue
                break
        sys.stdout = self._stdout
        self._reset_request_counter()

        if results:
            return json.loads(results, object_pairs_hook=OrderedDict) \
                if return_json else results
        if tries == self.request_retries:
            print("Unable to connect to server. Try again later.")
            sys.exit(1)

        # if we've gotten to this point we don't want ncloud to do any more
        # processing. Until systemExit gets refactored, exit with 0 exit code
        sys.exit(0)

    def api_call(self, config, endpoint, method, data, params, files, headers,
                 stream, session, return_status_code, token_needed,
                 console_log_follow, add_ncloud_data):
        # if we have console_log_follow, then don't do a sys.exit() despite
        # having no results to show yet
        if add_ncloud_data:
            sys.argv[0] = 'ncloud'
            ncloud_data = {
                'ncloud_cmd': ' '.join(sys.argv),
                'ncloud_version': __version__
            }
            if params:
                params.update(ncloud_data)
            else:
                params = ncloud_data

        url = config.api_url() + endpoint
        if token_needed:
            token = config.get_token(refresh=False)
        else:
            token = "no token needed"

        try:
            headers["Authorization"] = "Bearer " + token

            # check if we are keeping all api calls within the same session
            # this ensures that keep-alive is true
            if session:
                req = requests.Request(method, url, data=data, headers=headers,
                                       params=params, files=files)
                prepped = session.prepare_request(req)
                res = session.send(prepped, stream=stream,
                                   verify=SSL_CERT_VERIFICATION)
            else:
                res = requests.request(method, url, data=data, params=params,
                                       files=files, headers=headers,
                                       stream=stream,
                                       verify=SSL_CERT_VERIFICATION)
            # used in formatting new tests (add the data to a new txt file
            # in the test_system folder); ex:
            #     export NCLOUD_DEBUG=1; ncloud m l -t 0 > ncloud_m_l_t_0.txt
            if os.environ.get('NCLOUD_DEBUG', '') != '':
                sys.stdout = self._stdout
                self._print_debug(res)
                sys.stdout = self.devnull

            status_code = str(res.status_code)
            if res.status_code == 401:
                # token authentication failed, try to gen a new one and retry
                token = config.get_token(refresh=True)

                if session:
                    # if we are keeping the api_call inside of a session
                    prepped.headers["Authorization"] = "Bearer " + token
                    res = session.send(prepped, stream=stream)
                else:
                    headers["Authorization"] = "Bearer " + token
                    res = requests.request(method, url, data=data,
                                           params=params, files=files,
                                           headers=headers, stream=stream,
                                           verify=SSL_CERT_VERIFICATION)
            elif res.status_code == 204:
                sys.stdout = self._stdout
                print("Successfully done!")
            elif not status_code.startswith('2'):
                # if we are logging immediately, then we might not have
                # log files yet, in which case don't print that out + exit
                if not status_code == '503':
                    sys.stdout = self._stdout
                    print_error(res) if not console_log_follow else ''
                else:
                    sys.exit(1)
        except requests.exceptions.ConnectionError:
            self.logger.error("Unable to connect to server.")
            sys.exit(1)
        except requests.exceptions.RequestException as re:
            self.logger.error(re)
            sys.exit(1)
        except RequestError:
            return
        except Exception as e:
            self.logger.error(e)
            sys.exit(1)

        if res is not None:
            content_type = res.headers['content-type']

            if content_type == 'application/json':
                return res.text if not return_status_code else \
                    (res.text, res.status_code)
            else:
                # TODO: helium doesn't appear to set 'application/json' right
                if stream:
                    return res if not return_status_code else \
                        (res, res.status_code)
                elif res.encoding:
                    return res.content.decode(res.encoding) \
                        if not return_status_code else \
                        (res.content.decode(res.encoding), res.status_code)
                else:
                    return res.content if not return_status_code else \
                        (res.content, res.status_code)
        else:
            self.logger.error("No response received. Exiting.")
            sys.exit(1)

    def _reset_request_counter(self):
        self.request_retries = REQUEST_RETRIES
        self.api_call_attempts = 0

    def _print_debug(self, res):
        """Copy-paste this in for your tests. Only time this doesn't work is
           when we need a file to perform an operation on, in which case use:
           tests/test_system/test_data. Otherwise jenkins will complain.
           Ex: ['model', 'train', 'tests/test_system/test_data']
        """
        if len(sys.argv) > 1:
            print("%r" % sys.argv[1:])
        print("b%r" % res.content)
        print("%r" % res.text)
        print("%r" % res.encoding)
        print("%r" % res.headers)
        print("%r" % res.ok)
        print("%r" % res.reason)
        print("%r" % res.status_code)
        print('')
