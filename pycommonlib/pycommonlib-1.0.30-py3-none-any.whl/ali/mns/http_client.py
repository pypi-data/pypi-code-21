import requests, base64, hashlib, time, logging, hmac
from django.conf import settings
from pycommonlib.ali import exceptions
from urllib import parse

_logger = logging.getLogger('ALI-MNS')

_VERSION = "2015-06-06"


def _parse_response(r, valid_codes):
    if r.status_code in valid_codes:
        return (r.status_code, r.text)
    else:
        raise exceptions.APIError()

def get(url, params=None, valid_codes=(200,)):
    return _send_request('get', url, '', params, valid_codes)
    
def post(url, data, params=None, valid_codes=(200,)):
    return _send_request('post', url, data, params, valid_codes)

def delete(url, data, params=None, valid_codes=(200,)):
    return _send_request('delete', url, data, params, valid_codes)

def _send_request(method, url, data='', params=None, valid_codes=(200,)):
    args = {}
    if not params:
        params = {}
    args['params'] = params
    if data:
        args['data'] = data
    urlcomponents = parse.urlsplit(url)
    resourse = urlcomponents.path
    if params:
        resourse = '{}?{}'.format(resourse, parse.urlencode(params))
    args['headers'] = _build_header(method.upper(), urlcomponents.hostname, resourse, data)
    r = getattr(requests, method)(url, **args)
    _logger.debug('request url:{}, \n method:{} \n heaeder:{} \n body: {}'.format(r.request.url, r.request.method, r.request.headers, r.request.body))
    _logger.debug('response:\n status:{}\n body:{}'.format(r.status_code, r.text))
    responseData = _parse_response(r, valid_codes)
    return responseData

def _build_header(method, host, resourse, data):
    header = {'host':host}
    if data != "":
        header["content-md5"] = str(base64.b64encode(hashlib.md5(data).hexdigest().encode()), 'utf-8')
        header["content-type"] = "text/xml;charset=UTF-8"
    header["x-mns-version"] = _VERSION
    header["date"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    header["Authorization"] = _get_signature(method, header, resourse)
    return header
        
        
def _get_signature(method, headers, resource):
    content_md5 = headers.get('content-md5', '')
    content_type = headers.get('content-type', '')
    date = headers.get('date', '')
    canonicalized_resource = resource
    canonicalized_mns_headers = ""
    if len(headers) > 0:
        x_header_list = sorted(headers.keys())
        for k in x_header_list:
            if k.startswith('x-mns-'):
                canonicalized_mns_headers += k + ":" + headers[k] + "\n"
    string_to_sign = "{}\n{}\n{}\n{}\n{}{}".format(method, content_md5, content_type, date, canonicalized_mns_headers, canonicalized_resource)
    h = hmac.new(settings.ALIYUN['ACCESS_KEY_SECRET'].encode(), string_to_sign.encode(), hashlib.sha1)
    signature = str(base64.b64encode(h.digest()), 'utf-8')
    signature = "MNS " + settings.ALIYUN['ACCESS_KEY_ID'] + ":" + signature
    return signature

