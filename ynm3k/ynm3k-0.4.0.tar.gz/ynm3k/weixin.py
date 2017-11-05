'''
Echo the http request context.
'''
import hashlib
from .contrib import bottle

WEIXIN_CONFIG = {
    'TOKEN': ''
}


def generate_signature(timestamp, nonce, token):
    '''
    Generate weixin signatures.
    '''
    r = sorted([timestamp, nonce, token])
    signature = hashlib.sha1(''.join(r)).hexdigest()
    return signature



@bottle.route('/_tb/weixin/echo')
def status_code():
    timestamp = bottle.request.GET.get('timestamp', '')
    nonce = bottle.request.GET.get('nonce', '')
    token = WEIXIN_CONFIG['TOKEN']
    signature = bottle.request.GET.get('signature', '')
    echostr = bottle.request.GET.get('echostr', '')
    if signature != generate_signature(timestamp, nonce, token):
        return echostr
    else:
        return ''


@bottle.route('/_tb/weixin/wxconfig.js')
def wxconfig():
    debug = True if bottle.request.GET.get('debug') == '1' else False
    url = '' # referer
    ret = get_jsapi_config(url, debug)
'''
    ret = util.get_jsapi_url_signature(url, stage=stage, debug=debug)
    req._resp['Content-Type'] = 'application/x-javascript'
    req._resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req._resp["Pragma"] = "no-cache"
    req._resp["Expires"] = "0"
'''

    return 'wx.config(%s)' % json.dumps(ret)
