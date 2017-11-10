import requests
import json
import re

apiappend = ""
ctp_apikey = ""
ctp_if = ""
ctp_remap = ""
ctp_base = "http://api.ctext.org"
apisession = requests.Session()

def _ctpapicall(querystring):
    global apiappend
    response = apisession.get(ctp_base+"/"+querystring+apiappend).text
    data = json.loads(response)
    if('error' in data):
        raise Exception('CTP API Error', data['error']['code'], data['error']['description'])
    return data

def getcharacter(character):
    return _ctpapicall("getcharacter?char="+character)


def searchtexts(title):
    return _ctpapicall("searchtexts?title="+title)

def gettext(urn):
    return _ctpapicall("gettext?urn="+urn)

#
# Get a text as an array of strings of its subsections
#
def gettextasarray(urn):
    data = gettext(urn)
    asarray = []
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            asarray.append(gettextasstring(data['subsections'][subsec]))
    return asarray


def gettextaschapterlist(urn):
    text = gettext(urn)
    if 'fulltext' in text:
        asstring = ""
        for para in range(0, len(text['fulltext'])):
            asstring = asstring + text['fulltext'][para] + "\n\n"
        return [asstring]
    if 'subsections' in text:
        chapterlist = []
        for subsection in text['subsections']:
            chapterlist = chapterlist + gettextaschapterlist(subsection)
        return chapterlist
    return []


def gettextasparagrapharray(urn):
    return gettextasparagraphlist(urn)

#
# Get a text as an array of strings of all of its paragraphs
#
def gettextasparagraphlist(urn):
    data = gettextasstring(urn)
    asarray = re.compile("\n+").split(data)
    if len(asarray)>0:
        if asarray[-1] == '':
            asarray.pop()
    return asarray

def getlink(urn, search=None, redirect=False):
    reqstring = "getlink?urn="+urn
    if search:
        reqstring = reqstring + "&search=" + search
    if redirect:
        reqstring = reqstring + "&redirect=1"
    return _ctpapicall(reqstring)


def getstatus():
    return _ctpapicall("getstatus")

def getstats():
    return _ctpapicall("getstats")

def gettextinfo(urn):
    return _ctpapicall("gettextinfo?urn="+urn)

def gettexttitles():
    return _ctpapicall("gettexttitles")

def getcapabilities():
    return _ctpapicall("getcapabilities")

def readlink(url):
    return _ctpapicall("readlink?url="+url)


def gettextasobject(urn):
    data = gettext(urn)
    asarray = []
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            subtitle = None
            info = gettextinfo(data['subsections'][subsec])
            if('title' in info):
                subtitle = info['title']
            asarray.append({'title': subtitle, 'fulltext': gettextasstring(data['subsections'][subsec])})
    if('fulltext' in data):
        title = None
        info = gettextinfo(urn)
        if('title' in info):
            title = info['title']
        asstring = ""
        for para in range(0, len(data['fulltext'])):
            asstring = asstring + data['fulltext'][para] + "\n\n"
        asarray.append({'title': title, 'fulltext': asstring})
        return asarray
    return asarray

def gettextasstring(urn):
    data = gettext(urn)
    asstring = ""
    if('subsections' in data):
        for subsec in range(0, len(data['subsections'])):
            asstring = asstring + gettextasstring(data['subsections'][subsec])
    if('fulltext' in data):
        for para in range(0, len(data['fulltext'])):
            asstring = asstring + data['fulltext'][para] + "\n\n"
    return asstring

def setapikey(key):
    global ctp_apikey
    ctp_apikey = key
    _setappend()
    
def setlanguage(lang):
    global ctp_if
    ctp_if = lang
    _setappend()
    
def setremap(remap):
    global ctp_remap
    ctp_remap = remap
    _setappend()
    
def setapibase(base):
    global ctp_base
    ctp_base = base
    
def _setappend():
    global apiappend
    global ctp_apikey
    global ctp_if
    global ctp_remap
    apiappend = ""
    if ctp_apikey != "":
        apiappend = apiappend + "&apikey=" + ctp_apikey
    if ctp_if != "":
        apiappend = apiappend + "&if=" + ctp_if
    if ctp_remap != "":
        apiappend = apiappend + "&remap=" + ctp_remap
