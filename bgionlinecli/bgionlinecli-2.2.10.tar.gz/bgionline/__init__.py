# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import platform
import requests
import exceptions
import api
import logging
import sys
import time
from requests.packages.urllib3.packages.ssl_match_hostname import match_hostname
from requests.packages import urllib3
reload(sys)
sys.setdefaultencoding('utf8')

urllib3.disable_warnings(category=urllib3.exceptions.InsecurePlatformWarning)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s) %(filename)s[line:%(lineno)d] ')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s) %(filename)s[line:%(lineno)d] ')
logger = logging.getLogger()

_DEBUG = 0  # debug verbosity level
from bgionline.version import client_version

API_VERSION = '1.0.0'
USER_AGENT = "{name}/{version} ({platform})".format(name=__name__,
                                                    version=client_version,
                                                    platform=platform.platform())

DEFAULT_RETRIES = 6
DEFAULT_TIMEOUT = 60
API_SERVER_HOST = None
API_SERVER_PORT = None
API_SERVER_PROTOCOL = None
STORAGE_HOST = "oss-cn-shenzhen.aliyuncs.com"
API_SERVER = None
USERNAME = None
CREDENTIALS, WORKSPACE_ID, PROJECT_CONTEXT_ID = None, None, None


def configure_urllib3():
    # Disable verbose urllib3 warnings and log messages
    urllib3.disable_warnings(category=urllib3.exceptions.InsecurePlatformWarning)

    def _match_hostname(cert, hostname):
        if hostname == "112.74.38.235" or '112.74.182.190' or '39.108.90.31':
            hostname = "bgionline.cn"
        if hostname == "52.201.214.105":
            hostname = "bgionline.cn"
        match_hostname(cert, hostname)

    urllib3.connection.match_hostname = _match_hostname


configure_urllib3()


def APIRequest(resource, data=None, params=None, json=None, method="POST", headers=None, auth=True, prepend_srv=True,
               timeout=DEFAULT_TIMEOUT,max_retries=DEFAULT_RETRIES, always_retry=False, want_full_response=False, **kwargs):
    global API_SERVER

    if headers is None:
        headers = {}
    # headers["Content-Type"] = "application/json"

    if config.security_token:
        headers["Authorization"] = get_auth_token()

    url = API_SERVER + resource if prepend_srv else resource
    method = method.upper()

    if platform.system().lower() == 'windows':
        def to_zhcn(msg):
            os_codepage = sys.getfilesystemencoding()
            try:
                return msg.decode('utf8').encode(os_codepage)
            except:
                try:
                    return msg.encode()
                except:
                    return msg

        import unicodedata
        import chardet

        class UnicodeStreamFilter:
            def __init__(self, target):
                self.target = target
                self.encoding = 'utf-8'
                self.errors = 'replace'
                self.encode_to = self.target.encoding

            def write(self, s):
                if type(s) == str:
                    s = s.decode("utf-8")
                s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
                self.target.write(s)

        def getCharset(s):
            return chardet.detect(s)['encoding']

        if sys.stdout.encoding == 'cp936':
            sys.stdout = UnicodeStreamFilter(sys.stdout)

        if sys.getdefaultencoding() != 'gbk':
            reload(sys)
            sys.setdefaultencoding('gbk')

        try:
            if data:
                for i in data.keys():
                    if isinstance(data[i], str):
                        data[i] = (unicode(to_zhcn(data[i])))
            if params:
                for i in params.keys():
                    if isinstance(params[i], str):
                        params[i] = (unicode(to_zhcn(params[i])))
            if json:
                for i in json.keys():
                    if isinstance(json[i], str):
                        json[i] = (unicode(to_zhcn(json[i])))
        except:
            pass

    #print (url+'         '+str(data or '')+'      '+str(params or '')+'      '+str(json or ''))

    retry = 0
    while retry < max_retries:
        try:
            if retry > 0:
                sys.stderr.write("retry %s times , %ss later\n" % (retry, retry * 10))
                time.sleep(retry * 10)
            requests.packages.urllib3.disable_warnings()
            response = requests.request(method, url, verify=False, params=params, data=data, json=json, headers=headers, timeout=timeout, **kwargs)

            # parse error and retry
            if response.status_code // 100 != 2:
                raise exceptions.APIError(url, response.json())
            else:
                break
        except requests.exceptions.ConnectTimeout:
            retry += 1
            if not always_retry or retry == max_retries:
                raise
        except Exception as e:
            retry += 1
            if not always_retry or retry == max_retries:
                if vars().has_key('response'):
                    raise exceptions.APIError(url, response.json())
                else:
                    raise
            print e
    # todo how to deal with empty response
    if not response.text and response.status_code == 204:
        return {}

    if want_full_response:
        return response
    else:
        try:
            return response.json()
        except ValueError:
            raise exceptions.BadJSONFormat("Invalid JSON received from server")


def set_server_info(host=None, port=None, protocol=None, storage_host=None):
    global API_SERVER, API_SERVER_HOST, API_SERVER_PORT, API_SERVER_PROTOCOL, STORAGE_HOST

    if host:
        API_SERVER_HOST = host
    if port:
        API_SERVER_PORT = port
    if protocol:
        API_SERVER_PROTOCOL = protocol
    if storage_host:
        STORAGE_HOST = storage_host

    API_SERVER = "%s://%s:%s" % (API_SERVER_PROTOCOL, API_SERVER_HOST, API_SERVER_PORT)
    logger.debug("try to update server info: %s" % API_SERVER)


from utils.config import BOConfig

config = BOConfig()


def update_server_info(config_dir=None):
    global API_SERVER_HOST, API_SERVER_PORT, API_SERVER_PROTOCOL
    config.host = API_SERVER_HOST
    config.port = API_SERVER_PORT
    config.protocol = API_SERVER_PROTOCOL
    config.storage_host = STORAGE_HOST
    config.save(config_dir)


def set_username(name, config_dir=None):
    global USERNAME
    USERNAME = config.username = name
    config.save(config_dir)
    USERNAME = name


def set_auth_token(token, config_dir=None):
    global CREDENTIALS
    CREDENTIALS = config.security_token = token
    config.save(config_dir)
    CREDENTIALS = token


def get_auth_token():
    return "Bearer %s" % config.security_token
