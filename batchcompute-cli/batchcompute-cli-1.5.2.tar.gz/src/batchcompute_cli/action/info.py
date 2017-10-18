# -*- coding: utf-8 -*-
from ..const import VERSION
from .. import i18n_util
from xml.dom.minidom import parse
import xml.dom.minidom


try:
    import urllib.request as url_request
except:
    import urllib as url_request

import re
from terminal import green,magenta




URL = 'https://pypi.python.org/pypi?:action=doap&name=batchcompute-cli'

MSG=i18n_util.msg()

def getRemoteVersion():
    s = (url_request.urlopen(URL).read())

    try:
        DOMTree = xml.dom.minidom.parseString(s)
        Data = DOMTree.documentElement
        return Data.getElementsByTagName('revision')[0].childNodes[0].data
    except Exception as e:
        print(e)


def info():
    v = VERSION
    print('\n%s %s\n'%(magenta('AliCloud BatchCompute Cli'), v))

    v2 = getRemoteVersion()

    if check_version(v, v2):
        print('%s : %s' % ( MSG['info']['latest_version'], str(v2) ) )
        print('%s : %s' % ( MSG['info']['current_version'], str(v) ) )
        print(MSG['info']['has_upgrade'])
        print('%s\n' % MSG['info']['has_upgrade2'])
    else:
        print('  Nothing to update\n')

def to_int(s):
    return int(re.match('\\d+', s).group())

def check_version(v, v2):

    arr = v.split('.')
    arr2 = v2.split('.')

    arr = list(map(to_int, arr))
    arr2 = list(map(to_int, arr2))


    if arr2[0] > arr[0] or arr2[1] > arr[1] or arr2[2] > arr[2]:
        return True
    else:
        return False


