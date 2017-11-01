# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import inspect
import os
import time
from copy import deepcopy
import traceback

import sys
import requests
from requests.exceptions import ReadTimeout
from . import settings, global_cache_map

from ..uqer import session
from ..config import *

csv_encoding = 'gb2312'
request_encoding = 'UTF-8'

timeout = 5
retry_interval = 2
max_retries = 5

def get_real_string(input_string):
    if sys.version_info.major == 2:
        out = input_string.encode('utf-8')
    else:
        out = input_string
    return out


def get_http_result(httpClient, requestString, gw, max_retries=max_retries):
 
    for i in range(1, max_retries + 1):
        try:
            source = 'mercury_sdk:' + os.environ.get('DatayesPrincipalName', 'invalid_user')
            result = session.get("https://%s:%d/data/v1%s" % (httpClient[2], httpClient[3], requestString),
                                  headers={'Connection': 'close', "Authorization": "Bearer " + get_token(), 'SOURCE': source},
                                  timeout=timeout)
            return result

        except Exception as e:
            time.sleep(retry_interval)


def __getCSV__(requestString, httpClient, gw=True):
    try:
        result = get_http_result(httpClient, requestString, gw)
        if result.status_code == 400:
            raise Exception('请检查输入参数，可能某列表输入参数过长')
        if int(result.headers.get('dyes-rsp-count', 0)) == 500000:
            result2 = get_http_result(httpClient, requestString + '&pagenum=2', gw)
            if int(result2.headers.get('dyes-rsp-count', 0)) > 0:
                raise Exception('返回数据量过大，请修改参数减小返回数据量')
        return result.text
    except ReadTimeout:
        raise Exception('查询服务超时')
    except Exception as e:
        raise e

def get_cache_key(frame):
    args, _, _, values = inspect.getargvalues(frame)
    func_name = inspect.getframeinfo(frame)[2]
    cache_key = hash([values[arg] for arg in args].__str__())
    return func_name, cache_key

def get_data_from_cache(func_name, cache_key):
    return

def put_data_in_cache(func_name, cache_key, data):
    return

def splist(l, s):
    return [l[i:i+s] for i in range(len(l)) if i %s == 0]

def is_no_data_warn(csvString, print_msg):
    if csvString.startswith('-1:No Data Returned'):
        if print_msg:
            print('没有数据返回。请检查输入参数，若仍有问题，可联系service.uqer@datayes.com')
        return True
    return False

def handle_error(csvString, api_id):
    if csvString.startswith('-403:Need privilege'):
        result = '您没有该API的使用权限，请联系service.uqer@datayes.com咨询购买，' \
                 '或者直接登录https://app.wmcloud.com/datamkt/datapreview/%d' % api_id
    elif csvString.startswith('-403:Need login'):
        result = '您未登陆'
    elif csvString.startswith('-2:Invalid Request Parameter'):
        result = '无效的请求参数。请检查输入参数，若仍有问题，可联系service.uqer@datayes.com'
    elif csvString.startswith('-3:Service Suspend'):
        result = '服务终止。请联系service.uqer@datayes.com'
    elif csvString.startswith('-4:Internal Server Error'):
        result = '内部服务器错误。请联系service.uqer@datayes.com'
    elif csvString.startswith('-5:Server Busy'):
        result = '服务器拥堵。可能是海量用户在同一时间集中调用该数据造成，可稍后再次尝试。' \
                 '如长时间未改善，或频繁出现该问题，可联系sevice.uqer@datayes.com'
    elif csvString.startswith('-6:Trial Times Over'):
        result = '试用次数达到限制。您对该数据的试用权限已经到期,' \
                 '您可以前往https://app.wmcloud.com/datamkt/datapreview/%d' % api_id
    elif csvString.startswith('-7:Query Timeout'):
        result = '请求超时。可能您请求的数据量较大或服务器当前忙'
    elif csvString.startswith('-8:Query Failed'):
        result = '请求失败，请联系service.uqer@datayes.com'
    elif csvString.startswith('-9:Required Parameter Missing'):
        result = '必填参数缺失。请仔细复核代码，将其中的参数补充完整后再次尝试'
    elif csvString.startswith('-11:The number of API calls reached limit'):
        result = '当日调用次数达到上限，请优化代码调用逻辑。每日0点重新计数'
    else:
        result = csvString
    err_msg = result
    print (err_msg)

    raise Exception(get_real_string(err_msg))

def get_token():
    import os
    ACCESS_TOKEN = "access_token"
    DataAPI_TOKEN = "dataapi_token"

    if os.environ.get(DataAPI_TOKEN):
        return os.environ[DataAPI_TOKEN]

    if os.environ.get(ACCESS_TOKEN):
        access_token = os.environ[ACCESS_TOKEN]
        r2 = None
        try:
            r2 = session.post(TOKEN_URL,
                               data={'grant_type': 'permanent'})
            token = r2.json()['access_token']
            os.environ[DataAPI_TOKEN] = token

            return token
        except:
            print ('获取通联数据商场权限凭证出错，可能是您的token无效或者token过期，请重新登录\n')

            return ''
    else:
        print ('当前环境下没有 token，可能是您未登录，请先登录哦')
        return ''

def __getConn__():
    return server

def __formatDate__(inputDate):
    return inputDate

def lowcase_keys(d):
    result = {}
    for key, value in d.items():
        lower_key = key.lower()
        result[lower_key] = value
    return result

def is_pro_user():
    return True


def showtraceback(self, exc_tuple=None, filename=None, tb_offset=None,
                  exception_only=False):
    import traceback
    import sys

    etype, value, tb = self._get_exc_info(exc_tuple)
    listing = traceback.format_exception(etype, value, tb)
    last_message = ''
    lineno = None
    text = ''

    if listing:
        last_message = listing[-1].decode('utf-8')
    
    except_msg = 'Exception:'
    if last_message.startswith(except_msg):
        last_message = '异常:' + last_message[len(except_msg):]

    for filename, lineno, module, text in traceback.extract_tb(tb):
        if filename.startswith('<mercury-input') and \
           not text.startswith('display=True, return_quartz_data=True'):
            break

    if lineno:
        print('行号: %s\n代码: %s\n%s' %(lineno, text, last_message))
    else:
        print(last_message)


def pretty_traceback():
    if not settings.pretty_traceback_enabled:
        return
    import os
    if os.environ.get('env') in ['qa', 'stg', 'prd']:
        try:
            import IPython
            IPython.core.interactiveshell.InteractiveShell.showtraceback = showtraceback
        except:
            pass