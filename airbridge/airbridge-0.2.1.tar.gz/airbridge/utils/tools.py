# -*- coding: utf-8 -*-
import sys
import os
import traceback
import hashlib
import uuid
import time
import json
import re


if sys.version_info[0] == 2:
    from Cookie import SimpleCookie
    from urllib import urlencode, quote, unquote
    from urlparse import urlparse, parse_qs, urlunparse 
else:
    from http.cookies import SimpleCookie
    from urllib.parse import urlparse, parse_qs, urlunparse, quote, unquote, urlencode

from datetime import datetime
from airbridge.utils.user_agents import parse


def get_traceback_str():
    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    nstr = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('File "'):
            eles = lines[i].strip().split('"')
            basename = os.path.basename(eles[1])
            lastdir = os.path.basename(os.path.dirname(eles[1]))
            eles[1] = '%s/%s' % (lastdir,basename)
            rl.append('^\t%s %s' % (nstr,'"'.join(eles)))
            nstr = ''
        else:
            nstr += line
    return '\n'.join(rl)


def dict_to_single_depth(data, key=None):
    new_dict = {}
    for k, v in data.iteritems():
        if type(v) is dict:
            if key is not None:
                k = "{}.{}".format(key, k)
            new_dict.update(dict_to_single_depth(v, key=k))
        else:
            if key is None:
                # print "{}: {}".format(k, v)
                new_dict.update({k: v})
            else:
                # print "{}.{}: {}".format(key, k, v)
                if type(v) is list:
                    for idx, val in enumerate(v):
                        if type(val) is dict:
                            new_dict.update(dict_to_single_depth(val, "{}.{}.${}".format(key, k, str(idx))))
                        else:
                            new_dict.update({"{}.{}.${}".format(key, k, str(idx)): val})
                else:
                    new_dict.update({"{}.{}".format(key, k): v})

    return new_dict


def is_empty(text):
    emp_str = lambda s: s or ""
    if emp_str(text) == "":
        return True
    else:
        return False


def remove_trailing_br_tag(text):
    """Remove trailing <br/>(or </br>)
    """

    text = text.strip()

    if len(text) < 10:
        return text

    for i in range(10, len(text), 5):
        if text[-i] == "<" and text[-i:-i+5] in ['<br/>', '</br>']:
            continue
        else:
            return text[:-i+5]


def ret_one_row(rows, exception_str=None):
    # validate row counts
    if rows.rowcount < 1:
        raise Exception(exception_str)

    for row in rows:
        return row


def ret_one_row_without_exception(rows):
    if rows.rowcount < 1:
        return None

    for row in rows:
        return row


def parse_qsl(qs, keep_blank_values=0, strict_parsing=0, unquote_flag=True):
    """Parse a query given as a string argument.
    Arguments:
    qs: URL-encoded query string to be parsed
    keep_blank_values: flag indicating whether blank values in
        URL encoded queries should be treated as blank strings.  A
        true value indicates that blanks should be retained as blank
        strings.  The default false value indicates that blank values
        are to be ignored and treated as if they were  not included.
    strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.
    Returns a list, as G-d intended.
    """
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            # 기본적으로 unquote를 한다.
            if unquote_flag:
                name = unquote(nv[0].replace('+', ' '))
                value = unquote(nv[1].replace('+', ' '))
            else:
                name = nv[0].replace('+', ' ')
                value = nv[1].replace('+', ' ')
            r.append((name, value))

    return r


def parse_long_url_for_simplelink(url):
    if type(url) is unicode:
        url = str(url)

    o = urlparse(url)
    path = filter(None, o.path.split('/'))

    app_name = None
    label = None
    if len(path) == 1:
        app_name = detach_front_atsign(path[0])
    elif len(path) == 2:
        app_name = detach_front_atsign(path[0])
        label = path[1]
    else:
        raise Exception("longUrl format should be like 'http://abr.ge/<app_name>/<label>?query=..' (<label> could be omitted, but <app_name> should exist.)")

    return app_name, label, parse_qsl(o.query)


def detach_front_atsign(text):
    if not is_empty(text) and text[0] == '@':
        return text[1:]
    else:
        return text


def have_front_atsign(text):
    if not is_empty(text) and text[0] == '@':
        return True
    else:
        return False


def get_subdomain_detached_url(url):

    o = list(urlparse(url))

    if 's.' in o[1] and len(o[1]) > 2 and 's.' == o[1][:2]:
        o[1] = ".".join(o[1].split('s.')[1:])
        url = urlunparse(o)

    return url


def dict_to_param_string(query):
    return "&".join(["{}={}".format(key, value) for key, value in query.iteritems()])


def list_tuples_to_param_string(query):
    return "&".join(["{}={}".format(param[0], param[1]) for param in query])


def get_path_list_from_url(url):
    o = urlparse(url)
    return filter(None, o.path.split('/'))


def get_md5_hash(source_str):
    m = hashlib.md5()
    m.update(source_str)
    return m.hexdigest()


def get_url_with_additional_params_without_urlencode(url, query):
    if query is None:
        return url

    if type(url) is unicode:
        url = str(url)

    params = dict_to_param_string(query)
    url_parts = []
    url_parts = list(urlparse(url))
    url_parts[4] = list_tuples_to_param_string(parse_qsl(url_parts[4]) + parse_qsl(params, unquote_flag=False))

    # FIX BUG: urlunparse 안에서 딥링크 프로토콜이 path없이 들어오면 //가 사라짐
    url = urlunparse(url_parts)
    url = url.replace(':?', '://?')
    return url


def drop_bypass_params(url, bypass_str='dynamic'):
    params = get_query_string_as_dict(url, decoding=False)
    remained = {}
    bypassed = {}
    for key, value in params.iteritems():
        if bypass_str not in key:
            remained[key] = value
        else:
            bypassed[key] = value

    return get_url_with_additional_params_without_urlencode(url.split('?')[0], remained), bypassed


def get_query_string_as_dict(url, decoding=True):
    o = urlparse(url)
    if decoding:
        return dict(parse_qsl(unquote(str(o.query).decode('utf-8'))))
    else:
        return dict(parse_qsl(str(o.query)))


def get_key(item):
    return item[0]


def get_url_with_sorted_params(url):
    if type(url) is unicode:
        url = str(url)
    # print 'url => ' + url
    parsed = list(urlparse(url))
    # {, } 등이 들어있을 경우, unquote를 하지 않는 문제가 될 수 있음
    # custom landing url에 quote를 우리맘대로 풀면 안됨 (test_hotfix_gmarket.py)
    sorted_queries = sorted(parse_qsl(parsed[4], unquote_flag=False), key=get_key)

    queries = []
    for query in sorted_queries:
        # if 'https' in query[1] or 'http' in query[1]:
        if 'custom_landing_url' == query[0]:
            queries.append(query[0]+'='+quote(query[1]))
        else:
            queries.append(query[0]+'='+query[1])

    # parsed[4] = urlencode(sorted_queries) # for 블로그 제목. Do not urlencode
    parsed[4] = '&'.join(queries) # 네이버, 블로그 제목 longUrl에서 깨짐
    # print 'return url =>' + urlunparse(parsed)

    return urlunparse(parsed)


def get_client_ip(req):
    if req.headers.get('X-Forwarded-For') != None:
        x_forwarded_for = req.headers.get('X-Forwarded-For')
        if type(x_forwarded_for) in [str, unicode] and ',' in x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return x_forwarded_for
    elif req.remote_addr != None:
        return req.remote_addr
    else:
        return ''


def cookies_to_list(history_str):
    return history_str.split('||')


def get_client_info_from_request_object(request, request_url):
    try:
        cookie = request.headers['Cookie']
    except KeyError:
        # No cookie
        cookie = ""

    cookie_obj = SimpleCookie()
    cookie_obj.load(str(cookie))

    # get client_id from cookies or make one
    client_id = cookie_obj['ab180ClientId'].value if 'ab180ClientId' in cookie_obj else str(uuid.uuid4())

    raw_ua_string = request.headers.get('User-Agent') or ''
    ua_parser = parse(raw_ua_string)
    device = ua_parser.os.family.lower() # ios, android
    social = get_social_type_from_ua(raw_ua_string)

    return {
        'client_id': client_id,
        'client_history': request_url,
        'client_type': 1,
        'client_ip': get_client_ip(request),
        'client_device': device,
        'client_ua': raw_ua_string.encode('utf-8'),
        'client_ua_object': ua_parser,
        'social': social
    }


def get_https_market_url(url):
    if url == None:
        return None
    else:
        return url.replace("market://", "https://play.google.com/store/apps/").replace("itms-apps://", "https://")


def get_native_market_url(url):
    if url == None:
        return None
    else:
        return url.replace("https://play.google.com/store/apps/", "market://").replace("https://itunes", "itms-apps://itunes")


def get_market_url_with_params(market_url, query):
    params = urlencode(query)

    url_parts = []
    url_parts = list(urlparse(market_url))
    referrer_added_query = parse_qsl(url_parts[4]) + [('referrer','')] + parse_qsl(params)

    url_parts[4] = urlencode(referrer_added_query).replace('referrer=&','referrer=')

    return urlunparse(url_parts)


def quote_referrer_param(store_url):
    if 'referrer' in store_url:
        url_divided = store_url.split('referrer=')
        query = quote(url_divided[1])
        return url_divided[0] + 'referrer=' + query
    else:
        return store_url


def get_utm_params(params):
    if type(params) == dict:
        params_str = urlencode(params)
    else:
        params_str = params

    params_str = re.sub("(^source=)", "utm_\\1", params_str)
    params_str = re.sub("(^campaign=)", "utm_\\1", params_str)
    params_str = re.sub("(^medium=)", "utm_\\1", params_str)
    params_str = re.sub("(^term=)", "utm_\\1", params_str)
    params_str = re.sub("(^content=)", "utm_\\1", params_str)

    params_str = re.sub("([^\w])(source=)", "\\1utm_\\2", params_str)
    params_str = re.sub("([^\w])(campaign=)", "\\1utm_\\2", params_str)
    params_str = re.sub("([^\w])(medium=)", "\\1utm_\\2", params_str)
    params_str = re.sub("([^\w])(term=)", "\\1utm_\\2", params_str)
    params_str = re.sub("([^\w])(content=)", "\\1utm_\\2", params_str)

    if type(params) == dict:
        return dict(parse_qsl(params_str))
    else:
        return params_str


def remove_parameter_from_url(url):
    parsed_url = list(urlparse(url))
    parsed_url[4] = ''
    return urlunparse(parsed_url)


def remove_empty_values(dict_data):
    return dict((k, v) for k, v in dict_data.iteritems() if v)



def get_now_str():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def get_time_stamp(time_format=None):
    if time_format == 'micro':
        return int(time.time() * 10**6)
    elif time_format == 'milli':
        return int(time.time() * 10**3)
    else:
        return int(time.time())


def get_datetime_from_ms(ms):
    if ms is None:
        return None

    if len(str(ms)) == 16:
        # microseconds
        return datetime.fromtimestamp(int(ms)/1000000.0)
    elif len(str(ms)) == 13:
        # milliseconds
        return datetime.fromtimestamp(int(ms)/1000.0)
    else:
        # seconds
        return datetime.fromtimestamp(int(ms))


def totimestamp(dt, epoch=datetime(1970,1,1,hour=9)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**3  # micro


def quote_referrer_param(store_url):
    if 'referrer' in store_url:
        url_divided = store_url.split('referrer=')
        query = quote(url_divided[1])
        return url_divided[0] + 'referrer=' + query
    else:
        return store_url


def is_samsung_default_browser(raw_ua_string):
    return "SamsungBrowser" in raw_ua_string


def is_webview(raw_ua_string):
    return "; wv)" in raw_ua_string or "Version/4.0" in raw_ua_string


def get_social_type_from_ua(raw_ua_string):
    raw_ua_string = raw_ua_string or ''
    social = ""

    if "KAKAOTALK" in raw_ua_string:
        social = "Kakaotalk"
    elif "FB" in raw_ua_string:
        social = "FB"
    elif "Line" in raw_ua_string:
        social = "Line"
    elif "NAVER" in raw_ua_string:
        social = "Naver"
    else:
        social = ""

    return social


def remove_parameter_from_url(url):
    parsed_url = list(urlparse(url))
    parsed_url[4] = ''
    return urlunparse(parsed_url)


def get_url_with_additional_params(url, query):
    if query is None:
        return url

    if type(url) is unicode:
        url = str(url)

    params = urlencode(query) # urlencode를 하면 {sub_id}가 encode됨.
    url_parts = []
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(parse_qsl(url_parts[4]) + parse_qsl(params))

    # FIX BUG: urlunparse 안에서 딥링크 프로토콜이 path없이 들어오면 //가 사라짐
    url = urlunparse(url_parts)
    url = url.replace(':?', '://?')
    return url


def is_external_scraper(request):
    client = get_client_info_from_request_object(request, request.url)
    ua_parser = client['client_ua_object']
    if 'kakaotalk-scrap' in ua_parser.ua_string or\
        'facebookexternalhit' in ua_parser.ua_string or\
        'Googlebot' in ua_parser.ua_string or\
        'Facebot' in ua_parser.ua_string:
        return True
    else:
        return False


def get_ab180_client_id(headers, uuid=None):
    try:
        cookie = headers['Cookie']
    except KeyError:
        cookie = ""

    cookie_obj = SimpleCookie()
    cookie_obj.load(str(cookie))
    uuid = str(get_uuid()) if uuid is None else uuid
    return cookie_obj['ab180ClientId'].value if 'ab180ClientId' in cookie_obj else uuid


def send_work_to_queue(queue_session, queue_name, what_to_do, delay_seconds=0, **kwargs):
    payloads = {
        'what_to_do': what_to_do,
        'kwargs': kwargs
    }

    q = queue_session.get_queue_by_name(QueueName=queue_name)
    res = q.send_message(MessageBody=json.dumps(payloads, ensure_ascii=False).encode('utf-8'), DelaySeconds=delay_seconds)
    return res
