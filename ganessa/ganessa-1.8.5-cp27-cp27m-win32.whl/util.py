# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)

from datetime import date, datetime, tzinfo, timedelta
from sys import version_info
from itertools import izip
import tempfile
from math import sqrt, floor
import shutil
import os
import os.path as OP
import re
import subprocess
_PTN_BLANKS = re.compile(r'\s+')
_PTN_NO_IDC = re.compile(r'\W+')
_PTN_SEQUEN = re.compile(r'(-+_+-*|_+-+_*)+')
import json

import locale
locale.setlocale(locale.LC_ALL, '')
_decimal_point = locale.localeconv()['decimal_point']

PY3 = version_info.major == 3

#****g* ganessa.util/About
# PURPOSE
#   The module ganessa.util provides useful functions used by the Ganessa tools.
# REMARK
#   Some of the functions must be preceded by  'import ganessa.sim'
#****
#****g* ganessa.util/functions
#****
#****g* ganessa.util/iterators
#****

#****f* functions/formatting: strf3, stri, hhmmss, strd, quotefilename
# SYNTAX
#   * txt = strf3(fval)
#   * txt = stri(ival)
#   * hms = hhmmss(val)
#   * dmy = strd(dval)
# ARGUMENT
#   * int or float val: number of seconds
#   * int ival: integer input value
#   * float fval: float input value
#   * date dval: datetime input value
# RESULT
#   * string txt: string representation of the input value
#   * string hms: representation of time in the form 'hh:mm:ss'
#   * string dmy: date time in the isoformat except TZ: YYYY-MM-DDTHH:MM:SS
# REMARK
#   The value 'fval' is rounded before conversion
#****
def hhmmss(seconds, rounded= False):
    if rounded:
        seconds = int(seconds + 0.5)
    sign = ''
    if seconds < 0:
        seconds, sign = -seconds, '-'
    m = int(seconds//60)
    return "{3}{0:02d}:{1:02d}:{2:02d}".format(int(m//60), m%60, int(seconds - 60*m), sign)

def strf3(val):
    "Formate une valeur float avec mantisse de taille raisonnable"
    if val == 0.0:
        return "0.0"
    elif abs(val) > 1.0:
        strg = "{0:.3f}".format(val)
    elif abs(val) > 0.01:
        strg = "{0:.6f}".format(val)
    else:
        return "{0:.7e}".format(val)
    if strg[-3:] == "000":
        return strg[:-3]
    elif strg[-2:] == "00":
        return strg[:-2]
    else:
        return strg

def strf2(val):
    "Formate une valeur float avec mantisse de taille raisonnable"
    if val == 0.0:
        return "0.0"
    elif abs(val) > 1.0:
        strg = "{0:.2f}".format(val)
    elif abs(val) > 0.01:
        strg = "{0:.4f}".format(val)
        if strg[-2:] == "00":
            return strg[:-2]
        elif strg[-1:] == "0":
            return strg[:-1]
        else:
            return strg
    else:
        return "{0:.7e}".format(val)
    if strg[-3:] == "000":
        return strg[:-3]
    elif strg[-2:] == "00":
        return strg[:-2]
    else:
        return strg

def _strloc(val):
    return _decimal_point.join(str(val).split('.'))

def _strf3loc(val):
    return _decimal_point.join(strf3(val).split('.'))

strloc = str if _decimal_point == '.' else _strloc
strf3loc = strf3 if _decimal_point == '.' else _strf3loc

def stri(val):
    "Retourne la chaine representant la valeur entiere"
    return '{0:d}'.format(val)

def strii(val):
    "Retourne la chaine representant la valeur entiere"
    return '{0:02d}'.format(val)

def strd(val):
    # return val.isoformat()
    return val.strftime("%Y-%m-%dT%H:%M:%S")

def quotefilename(fname):
    '''Quote a filename with doublequotes if not yet quoted and
    if a whitespace character appears in the filename. Added 150911'''
    if fname[0] not in ('"', "'") and ' ' in fname:
        fname = '"' + fname + '"'
    return fname

#****f* functions/ascii, unistr
# SYNTAX
#   * atxt = ascii(input_str)
#   * utxt = unistr(input_str)
#   * utxt = str2uni(input_str)
# ARGUMENT
#   unicode or string input_str: string value to be converted to ascii or unicode
# RESULT
#   * unicode or string atxt: string of same type as input_str where non-ascii charcacters
#     have been replaced with the best match (i.e. 'e' is replaced with 'e')
#   * unicode utxt: unicode string decoded from input_str (multiple codecs tried in turn);
#     unistr tries cp1252 the utf-8; str2uni tries utf-8 then cp1252.
#****
def unistr(input_str):
    if PY3:
        if isinstance(input_str, str):
            return input_str
        elif isinstance(input_str, bytes):
            for codec in ('cp1252', 'iso-8859-1', 'utf-8', 'utf-16'):
                try:
                    return str(input_str, codec)
                except UnicodeError:
                    continue
        else:
            return str(input_str)
    else:
        if isinstance(input_str, basestring):
            if isinstance(input_str, unicode):
                return input_str
            for codec in ('cp1252', 'iso-8859-1', 'utf-8', 'utf-16'):
                try:
                    return unicode(input_str, codec)
                except UnicodeError:
                    continue
        else:
            return unicode(input_str)

def str2uni(input_str):
    if PY3:
        if isinstance(input_str, str):
            return input_str
        elif isinstance(input_str, bytes):
            for codec in ('utf-8', 'cp1252', 'iso-8859-1', 'utf-16'):
                try:
                    return str(input_str, codec)
                except UnicodeError:
                    continue
        else:
            return str(input_str)
    else:
        if isinstance(input_str, basestring):
            if isinstance(input_str, unicode):
                return input_str
            for codec in ('utf-8', 'cp1252', 'iso-8859-1', 'utf-16'):
                try:
                    return unicode(input_str, codec)
                except UnicodeError:
                    continue
        else:
            return unicode(input_str)

def ascii(input_str):
    import unicodedata
    nkfd_form = unicodedata.normalize('NFKD', unistr(input_str))
    filtred = [c for c in nkfd_form if not unicodedata.combining(c)]
    if PY3 or isinstance(input_str, unicode):
        return u''.join([c.encode('ASCII', 'replace').decode() for c in filtred])
    else:
        return b''.join([c.encode('ASCII', 'replace') for c in filtred])
#****f* functions/codewinfile, winstr, utf, utf2uni
# SYNTAX
#   out_txt = winstr(input_str)
#   out_txt = utf(input_str)
#   uni_txt = utf2uni(input_str)
# ARGUMENT
#   unicode or string input_str: string value to be converted to windows-compatible string
# RESULT
#   out_txt encoded into Windows-1252 or utf-8 (no change if no accent or special character)
# REMARK
#   codewinfile and winstr are synonyms
#****
def winstr(input_str):
    return str(input_str, 'cp1252') if PY3 else unistr(input_str).encode('cp1252')  # Windows-1252
codewinfile = winstr

def utf(input_str):
    return str(input_str, 'utf-8') if PY3 else unistr(input_str).encode('utf-8')

def utf2uni(input_str):
    if PY3:
        if isinstance(input_str, str):
            return input_str
        elif isinstance(input_str, bytes):
            return str(input_str, 'utf-8')
        else:
            return str(input_str)
    else:
        if isinstance(input_str, basestring):
            if isinstance(input_str, unicode):
                return input_str
            else:
                return unicode(input_str, 'utf-8')
        else:
            return unicode(input_str)

#****f* functions/toidpic
# SYNTAX
#   out_str = toidpic(input_str)
# ARGUMENT
#   unicode or string input_str: string value to be converted to a Piccolo ID
# RESULT
#   ascii string where blank, comma, equal are replaced with underscore, other
#   non litteral or digit are replaced with minus.
#****
def toidpic(txt):
    'Returns a Piccolo/Picalor compatible ID'
    txt = txt.strip()
    if len(txt) == 0:
        return u'_EMPTY_'
    txt = ascii(txt)
    txt = _PTN_BLANKS.sub('_', txt)
    txt = _PTN_NO_IDC.sub('-', txt)
    txt = _PTN_SEQUEN.sub('-', txt)
    return txt

def toidpic_old(txt):
    'Returns a Piccolo/Picalor compatible ID'
    txt = txt.strip()
    if txt == '':
        return u'_EMPTY_'
    txt = ascii(txt.replace('  ','_').replace(' ','_')
                    .replace(',','_').replace('=','_')
                    .replace('.','-').replace('/','-')
                    .replace('(','-').replace(')','-')
                    .replace('_-_','-'))
    return txt

#****f* functions/gfloat, gint, gbool
# SYNTAX
#   * fval = gfloat(input_string)
#   * ival = gint(input_string)
#   * bval = gbool(input_string)
# ARGUMENT
#   string input_str: string value to be converted to a float or int or bool. 
#   The decimal separator can either be '.' or ','.
# RESULT
#   * float fval or int ival: numerical value after conversion
#   * bool bval: semantic boolean value. 
#     Unlike bool builtin, gbool('False'), gbool('n') and gbool('0') return False
# HISTORY
#   171127: gbool added
#****
def gfloat(strg):
    "Conversion d'une chaine en float avec '.' ou ',' en separateur decimal"
    try:
        return float(strg)
    except ValueError:
        return float(strg.replace(',','.',1))

def gint(strg):
    "Conversion d'une chaine en int avec '.' ou ',' en separateur decimal"
    try:
        return int(strg)
    except ValueError:
        return int(gfloat(strg))

def gbool(val):
    if isinstance(val, basestring):
        val = val.lower()
        if val in ("true", "oui", "yes", "o", "ok", "y", "1"):
            return True
        elif val in ("false", "non", "no", "n", "0"):
            return False
    return bool(val)

#****f* functions/list2file
# SYNTAX
#   fname = list2file(idlist [, header] [, footer] [, folder] [, suffix])
# ARGUMENT
#   * idlist: list of id (unicode str).
#   * header: optional string to be placed before the list
#   * footer: optional string to be placed after the list
#   * folder: optional folder to create the file (default temp folder).
#   * suffix: optional string to be used as a suffix for fname. Defaults to 'IDs.txt'
# RESULT
#   str fname: name of a temporary file containing header if any, elements of idlist,
#   footer if any, one per line.
#****
def list2file(idlist, header= None, footer= None, folder= None, suffix= u'IDs.txt'):
    'Converts a str list into a file'
    with tempfile.NamedTemporaryFile(delete= False, suffix= suffix) as fsel:
        if header is not None:
            fsel.write(header + u'\n')
        fsel.write(u'\n'.join(idlist))
        if footer is not None:
            fsel.write(u'\n' + footer)
    if folder is not None and OP.exists(folder):
        name = OP.basename(fsel.name)
        shutil.move(fsel.name, OP.join(folder, name))
    else:
        return fsel.name

#****f* functions/XMLduration
# SYNTAX
#   ival = XMLduration(input_string)
# ARGUMENT
#   string input_str: XML duration string value to be converted to a number of seconds.
#
#   The input format is [-]PnYnMnDTnHnMnS where:
#   * leading 'P' is mandatory,
#   * at least one duration item must be present
#   * 'T' is mandatory if any hour, minute, second is present
#   * all items are integers except second that may be either int or float.
# RESULT
#   int ival: number of seconds
#****
def XMLduration(arg):
    # import re
    # from datetime import timedelta
    if not arg:
        return 0.0
    elif arg[0] != 'P':
        raise ValueError
    else:
        regex  = re.compile('(?P<sign>-?)P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?')
        # Fetch the match groups with default value of 0 (not None)
        duration = regex.match(arg).groupdict(0)
        # Create the timedelta object from extracted groups
        delta = timedelta(days=int(duration['days']) + (int(duration['months']) * 30) + (int(duration['years']) * 365),
                          hours=int(duration['hours']),
                          minutes=int(duration['minutes']),
                          seconds=int(duration['seconds']))
        if duration['sign'] == "-":
            delta *= -1
        return delta.days * 86400 + delta.seconds

#****f* functions/decode_time, decode_date
# SYNTAX
#   * fval = decode_time(input_tstring [, factor])
#   * dval = decode_date(input_dstring)
# ARGUMENT
#   * string input_tstr: duration in the form of float or hh:mm:ss or XML duration string.
#   * optional float factor: multiplier (default to 1)
#   * string input_dstr: date in a versatile format YYYY/MM/DD hh:mm:ss or DD/MM/YYYY hh:mm:ss
#     or the iso format YYYY-MM-DDThh:mm:ss where 'T' can be replaced with a blank ' '.
# RESULT
#   * float fval: number of seconds. The result is multiplied by factor only if input_string is a float.
#   * date dval: date. The exception 'ValueError' is raised if the date cannot be read.
#****
def decode_time(strg, facteur=1.0):
    "Retourne le nombre de secondes 'hh:mm:ss' or 'nombre' * facteur "
    # if len(strg) < 10:
    champs = strg.split(":")
    if len(champs) == 1:
        # champ numerique ou PTxHyMz.zzS
        try:
            duree = float(strg) * facteur
        except ValueError:
            duree = XMLduration(strg)
    else:
        # hh:mm[:ss]
        duree = 60*(float(champs[1]) + 60*float(champs[0]))
        if len(champs) == 3:
            duree = duree + float(champs[2])
    return duree

def decode_date(strin):
    """ Transforme une date ASCII en datetime
        Produit l'exception ValueError si le format n'est pas reconnu"""
    # from datetime import datetime
    strg = strin.replace('/', '-').replace(' ', 'T').rstrip('Z')
    try :
        result = datetime.strptime(strg,"%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            result = datetime.strptime(strg,"%d-%m-%YT%H:%M:%S")
        except ValueError:
            champs = strg.split('T')
            try:
                jjmmaa = datetime.strptime(champs[0],"%Y-%m-%d")
            except ValueError:
                jjmmaa = datetime.strptime(champs[0],"%d-%m-%Y")
#                try:
#                    jjmmaa = datetime.strptime(champs[0],"%d-%m-%Y")
#                except ValueError:
#                    return datetime(2222,11,22,11,22,11)
            if len(champs) > 1:
                hhmmss = champs[1].split(':')
                result = jjmmaa.replace(hour=int(hhmmss[0]), minute=int(hhmmss[1]))
            else:
                result = jjmmaa
        if len(strin) > 20:
            # decoder le tzinfo
            pass
    return result

class TZ(tzinfo):
    def utcoffset(self, dt): return timedelta(minutes=-dt)

#****f* functions/envoi_msg
# SYNTAX
#   status = envoi_msg(exp, dst, objet, texte [, serveur])
# ARGUMENT
#   * string exp: adresse expediteur du message
#   * string dst: adresse destinataire (ou [dst1, dst2 ... ])
#   * string objet: objet
#   * string texte: texte du message
#   * string serveur (optionnel): serveur d'envoi
# RESULT
#   * bool status: True si le message est parti sans erreur
#****
def envoi_msg(exp, dst, objet, texte, serveur='smtp.safege.net'):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Create the enclosing message
    msg = MIMEMultipart()
    msg['Subject'] = objet
    if '@' not in exp:
        exp += '@safege.com'
    msg['From'] = exp
    if isinstance(dst,list) or isinstance(dst,tuple):
        msg['To'] = ";".join(dst)
    else:
        msg['To'] = dst
    msg.preamble = "SUEZ Consulting - DCS 2017"
    # Texte du message
    msg.attach(MIMEText(texte,'plain','utf-8'))

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP()
    try:
        s.connect(serveur)
        s.sendmail(exp, dst, msg.as_string())
        s.close()
        return True
    except:
        return False

#****f* functions/lec_csv
# SYNTAX
#   header, content = lec_csv(filename [, sep=','])
# ARGUMENT
#   * string filename: input file name
#   * string sep: optional column separator
# RESULT
#   * header: list of strings read from the 1st line
#   * content: list of lines, each being a list of text fields
# REMARK
#   The entire file is read into 'content'
#****
def lec_csv(fichier, sep=','):
    '''
Lecture d'un fichier CSV et retour du contenu
    argument:
        fichier: nom complet du ficher
        sep:     separeteur optionnel (defaut virgule)
    retour :
        entete: premiere ligne (liste de champs)
        corps:  listes des lignes, chacune etant une liste de champs
    '''
    import csv
    with open(fichier, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=sep)
        entete = reader.next()
        corps = []
        for texte in reader:
            corps.append(texte)
        return entete, corps
    del csv

#****f* functions/FichInfo, banner
# SYNTAX
#   * fi = FichInfo(filename)
#   * txt = fi.banner()
# ARGUMENT
#   string filename: input file name - expects the name of the caller '__file__'
# RESULT
#   a class member containing the following fields and method:
#   * nom: basename of the input filename without extension
#   * vers: date of last modification of filename in the form 'YYMMDD'
#   * pyvers: current version of python 'x.y.z'
#   * banner() returns a string containing all the elements above
#****
class FichInfo(object):
    """FichInfo:
        nom = nom de fichier
        vers = date de modification au format (AAAAMMJJ)
        pyvers = version de Python
    """
    def __init__(self, nom, version= ''):
        from os import stat
        self.full = nom
        self.nom = OP.splitext(OP.basename(nom))[0]
        self.vers = version + ' ' if version else ''
        self.vers += date.fromtimestamp(stat(nom).st_mtime).strftime("(%Y%m%d)")
        self.pyvers = '.'.join(map(str, version_info[0:3]))
        self.wkdir = OP.dirname(nom)
        del stat
    def banner(self):
        return ' '.join((self.nom, self.vers, '- Python', self.pyvers))

#****f* functions/IniFile, get, set, save
# SYNTAX
#   * mycfg = IniFile(filename)
#   * txt = mycfg.get(group, key, default)
#   * mycfg.set(group, key, value)
#   * mycfg.save()
# ARGUMENT
#   * string filename: input file name - expects the name of the caller '__file__'
#     in order to get the same file path and name with extension .json 
#   * string group: group of keys
#   * string key, value: value of key to be stored/retrieved
# RESULT
#   * mycfg = IniFile(filename): loads the init file and returns the groups of keys
#   * val = mycfg.get(group, key, val) allows to update val if the value of group/key
#     is defined.
#   * set() allows to set key with value
#   * save() saves the files back
# HISTORY
#   Default format changed from .xml to .json in aug 2017; 
#   previous settings will be converted.
#****
class _jsonIniFile(object):
    ''' Gestion d'un fichier de parametres initiaux en JSON'''
    def __init__(self, fname):
        pname = OP.splitext(fname)[0]
        self.fname = pname + '.json'
        if OP.exists(self.fname):
            with open(self.fname, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = dict()
        del pname

    def get(self, groupname, keyname, default):
        try:
            return self.data[groupname][keyname]
        except KeyError:
            return default 

    def set(self, groupname, keyname, value):
        try:
            self.data[groupname][keyname] = value
        except KeyError:
            self.data[groupname] = {keyname: value}

    def save(self, encoding= 'utf-8'):
        with open(self.fname, 'w') as f:
            json.dump(self.data, f, indent= 2, encoding=encoding)

class _xmlIniFile(object):
    ''' Gestion d'un fichier de parametres initiaux en XML'''
    def __init__(self, fname):
        from xml.etree.ElementTree import parse, Element, ElementTree
        pname = OP.splitext(fname)[0]
        self.fname = pname + '.xml'
        if OP.exists(self.fname):
            self.tree = parse(self.fname)
            self.root = self.tree.getroot()
        else:
            self.root = Element(OP.basename(pname))
            self.tree = ElementTree(self.root)
        del parse, Element, ElementTree, pname

    def get(self, groupname, keyname, default):
        return self.root.findtext(groupname + '/' + keyname, default)

    def set(self, groupname, keyname, value):
        from xml.etree.ElementTree import SubElement
        group = self.root.find(groupname)
        if group == None:
            group = SubElement(self.root,groupname)
        item = group.find(keyname)
        if item == None:
            item = SubElement(group, keyname)
        item.text = value

    def save(self, encoding= 'utf-8', xml_declaration= True):
        self.tree.write(self.fname, encoding, xml_declaration)
            
class IniFile(_jsonIniFile):
    ''' Gestion d'un fichier de parametres initiaux en XML /JSON
    Conversion en JSON'''
    def __init__(self, fname):
        _jsonIniFile.__init__(self, fname)
        pname, ext = OP.splitext(fname)
        TYPES = ('.json', '.xml')
        if ext.lower() not in TYPES:
            for ext in TYPES:
                if OP.exists(pname + ext):
                    break
            else:
                ext = '.json'      
        if ext.lower() != '.json':
            xml = _xmlIniFile(fname)
            # conversion XML en dict --> JSON
            self.data = dict()
            for group in xml.root:
                self.data[group.tag] = dict(((item.tag, item.text) for item in group))
            del xml
        del pname, ext           
            
def tsadd(t1, v1, n1, t2, v2, n2):
    import numpy as np
    t, v = [], []
    k1, k2 = 0, 0
    p1, p2 = v1[0], v2[0]
    while True:
        if t1[k1] < t2[k2]:
            t.append(t1[k1])
            p1 = v1[k1]
            k1 += 1
        elif t1[k1] > t2[k2]:
            t.append(t2[k2])
            p2 = v2[k2]
            k2 += 1
        else:
            t.append(t1[k1])
            p1, p2 = v1[k1], v2[k2]
            k1 += 1
            k2 += 1
        v.append(p1+p2)
        if k1 == n1 or k2 == n2:
            break
    return np.array(t), np.array(v), len(t)

#****f* functions/layout
# PURPOSE
#   Determines the number of pages, lines and columns of a figure
# SYNTAX
#   npages, nlines, ncols = layout(nbplots [, nlmax=6 ] [, ncmax= 4])
# ARGUMENT
#   * int nbplots: number of graph to plot
#   * int nlmax (optional, default 6): max nb of graphs per column
#   * int ncmax (optional, default 4): max nb of graphs per line
# RESULT
#   * int npages:  number of pages to plot
#   * int nlines:  number of lines per page
#   * int ncols:   number of columns per page
# EXAMPLE
#   - nf, nl, nc = layout(len(mes))
#   - for i in range(nf):
#   -     plotmes(graphs[i*nl*nc:(i+1)*nl*nc] , ...)
#****
def layout(nbplots, nlmax=6, ncmax=4):
    'Calcul du nb de pages, lignes et de colonnes du plot'
    if nbplots < 2:
        return 1, 1, 1
    nf = (nbplots + nlmax*ncmax - 1) // (nlmax*ncmax)
    nbplots = (nbplots + nf - 1) // nf
    nc = min(ncmax, int(floor(sqrt(nbplots))))
    nl = (nbplots + nc -1) // nc
    return nf, nl, nc

#****f* functions/roundval, scaladjust
# PURPOSE
#   Computes a rounded approximation of a float number
# SYNTAX
#   * rmin, rbest, rmax = roundval(val, reltol= 0.01)
#   * rval = scaladjust(val)
# ARGUMENT
#   * float val: value to be rounded
# RESULT
#   * float rmin, rmax: lower and upper values approximations (rmax - rmin < reltol*|val|)
#   * float rbest: best approximation (one of rmin, rmax)
#   * float rval: value rounded at 1., 2. or 5. in the order of magnitude of val.
# REMARK
#   scaladjust is used to determine the grid interval for plots as scaladjust(0.25*(ymax-ymin))
#****
def roundval(val, reltol= 0.01):
    'Calcul d\'une valeur arrondie proche a reltol pres'
    from math import log
    tol = reltol * abs(val)
    d = log(tol, 10.) + 0.0001
    n = int(d)
    if n < 0: n -= 1
    base = 10**n
    rest = tol / base + 0.0001
    for x in (7.5, 5.0, 4.0, 2.5, 2.0, 1.5, 1.0):
        if x <= rest: break
    rest = base*x
    r1 = rest * (val//rest)
    if val >= 0.0:
        r2 = r1 + rest
    else:
        r1, r2 = r1-rest, r1
    r3 = r1 if r2-val > val-r1 else r2
    return (r1, r3, r2)

def scaladjust(val):
    'Renvoi d\'une valeur arrondie a 1 2 5 pres'
    from math import log
    val = abs(val)
    n = int(log(val, 10.))
    e = 10.0**n
    m = val / e
    if m < 1.5:
        m = 1.0
    elif m < 3.0:
        m = 2.0
    elif m < 7.5:
        m = 5.0
    else:
        m = 10.0
    return m * e

#****f* functions/plotmes, plotmesx, pageplot
# PURPOSE
#   * plotmes plots one or more time series of the same kind in a single page.
#   * plotmesx plots one or more time series of the same kind on one or more figures.
#     it makes use of layout in order to determine the number of pages.
#   * pageplot plots a table of time series.
#   * plot_close allows to clean up matplotlib scraps and should be called 
#     before the script ends.
# SYNTAX
#   * plotmes(mes, attr  [, nl=3 ]  [, nc=2 ] [, cmt='' ] [, fgname=''] [, inter=True] )
#   * plotmesx(mes, attr [, nlx=6 ] [, ncx=4 ] [, cmt='' ] [, fgname=''] [, inter=True] )
#   * pageplot(tsl, title [, nl=3 ] [, nc=2 ] fgname=''] [, inter=True] [, lang='FR'] )
#   * plot_close()
# ARGUMENT
#   * list mes: either a list of element ids, for which the result time series
#     will be retrieved from the result file. If a measurement is associated
#     with an id, it will also be displayed on the same id graph.
#   * or a list of (id, ftime, fval), in which case the additional
#     time serie (ftime, fval) will be plotted on the id graph.
#   * list tsl: list of (id, tvec, vvec) to be plotted, one per graph.
#   * string attr: attribute to be plotted
#    (or attr:DA for residual or attr:DR for relative residual)
#   * ln, cn: number of lines and columns of plots in the page (plotmes only)
#   * lnx, cnx: maximum number of lines and columns of plots in the page (plotmesx only)
#   * cmt: optional comment appended to the title
#   * string fgname: output file name - if not nul, the plot will be saved
#     into a filename with extension '.png'.
#   * bool inter: if False, no plot is displayed
# REMARK
#   Type of data and units are displayed (in french) in the figure title
# HISTORY
#   - 170426: improvement of x axis labels when time horizon > 24h
#   - 170618 (1.7.6): added pageplot
#   - 171120 (1.8.5): added plot_close
#****

def plotmesx(mes, symbattr, nlx=6, ncx=4, cmt=u'', fgname=None, inter=True):
    if fgname:
        from os.path import splitext
        fnam, fext = splitext(fgname)
        fnam += '_' + symbattr.strip()
        fgni = fnam + fext
    else:
        fgni = None
    nf, nl, nc = layout(len(mes), nlx, ncx)
    if nf == 1:
        plotmes(mes, symbattr, nl, nc, cmt=cmt, fgname=fgni, inter=inter)
        return
    else:
        for i in range(nf):
            si = '_' + str(i+1)
            if fgname:
                fgni = fnam + si + fext
            plotmes(mes[i*nl*nc:(i+1)*nl*nc], symbattr, nl, nc, cmt=cmt + si,
                    fgname=fgni, inter=inter)

def plot_close():
    '''Ends up matplotlib'''
    # close matplotlib in order to avoid the error:
    # Fatal Python error: PyEval_RestoreThread: NULL tstate
    from sys import modules
    if 'matplotlib.pyplot' in modules:
        print('Closing matplotlib...')
        import matplotlib.pyplot as plt
        plt.close('all')

def plotmes(mes, symbattr, nl=3, nc=2, cmt=u'', fgname=None, inter=True):
    ''' Trace de series de donnees Piccolo
        mes: liste des points e tracer, chacun se presentant:
            soit sous forme d'un identifiant 'id'
                -> l'attribut symb sera trace
            soit sous forme d'un tuple ('id', vecteur dates, vecteur valeurs de reference)
                -> l'attribut symb sera trace ainsi que le vecteur de reference
            si une mesure est presente e ce point, elle sera tracee
        symb: symbole Piccolo du type de variable tracee ('Q', 'V', 'CH', 'P', 'NC' etc.)
        nl, nc: disposition du graphe en nl lignes par nc colonnes
        cmt: texte ajoute dans le titre
        fgname: nom du fichier resultat pour sauvegarde en plt
        inter: permet de ne pas afficher la courbe
    '''
    from sys import modules
    if 'ganessa.sim' not in modules:
        print(u'*** plotmes(x) must be used with "ganessa.sim".')
        return
    else:
        gans = modules['ganessa.sim']
    del modules

    def hours(t):
        'Conversion de seconde en heures avec arrondi'
        return 0.01*int(0.5 + t/36.)

    nbts = gans.tslen()
    if nbts == 0:
        print(u'*** plotmes(x): no EPS results available - quitting.')
        return

    tmin, tmax, _nb = gans.tsinterv()
    # step = 180.
    nbmes = len(mes)
    if inter: print (u' plotting {:d} time serie(s) of {:d} steps on [{:.3s}, {:.3s}] hours'.format(
                    nbmes, nbts, strf3(hours(tmin)), strf3(hours(tmax))))
    if nbmes == 0: return

    # Utilisation de MatPlotLib
    # import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, ScalarFormatter
    # from time import sleep

    typmes = {'Q': gans.LINK, 'V': gans.LINK,
              'P': gans.NODE, 'CH': gans.NODE, 'C1': gans.NODE,
              'VC':gans.TANK, 'NC':gans.TANK, 'V%':gans.TANK, 'H':gans.TANK}
    libmes = {'Q': 'Debit', 'V': 'Vitesse',
              'P': 'Pression', 'CH': 'Charge', 'C1': 'Chlore',
              'VC':'Volume', 'NC':'Niveau', 'V%':'% remplissage', 'H':'Hauteur'}

    diff = symbattr.upper().split(':')
    symb = diff[0]
    bresidu = len(diff) > 1

    strattr = gans.nodeattrs
    try:
        if typmes[symb] == gans.BRANCH: strattr = gans.branchattrs
    except KeyError:
        print('*** plotmes: unknown symbol:', symb)
        return
    # ajustement ponctuel du nb de graphes
    if nbmes > nc*nl:
        nl += 1
        if nbmes > nc*nl:
            nc += 1
    fx, fy, ftop, fbottom, fleft, fright = 16, 9, 0.9, 0.1, 0.075, 0.95
    if nc == 1: fx, fleft, fright = 6, 0.125, 0.9
    elif nc == 2: fx, fleft, fright = 11, 0.1, 0.925
    if nl == 1: fy, ftop, fbottom = 3, 0.8, 0.2
    elif nl == 2: fy, ftop, fbottom = 6, 0.85, 0.15
    fig = plt.gcf()
    if nc > 1 or nl > 2 or not fig:  #  or inter:
        if fig: plt.close(fig)
        fig = plt.figure(figsize=(fx, fy))
    else:
        fig.clf()
        fig.figsize = (fx, fy)
    y_formatter = ScalarFormatter(useOffset= False)
    if bresidu and diff[1] == 'DR':
        unit = ''
    else:
        unit = gans.getunitname(symb)
        if unit[0:2] == 'm3': unit = u'$m^3' + unit[2:] +'$'
    title_plt = libmes[symb] + u' (' + unit + u')'
    if cmt: title_plt += u' ' + cmt
    plt.suptitle(title_plt, fontsize=18.)
    i = 0
    for item in mes[0:nl*nc]:
        if isinstance(item, tuple):
            eid, tr, r = item
        else:
            eid = item
        nom = strattr(eid, 'NO')
        if not isinstance(nom, unicode):
            nom = unicode(nom,'cp1252')
        id_titre = eid
        if len(nom) > 0 and nom != eid:
            if len(nom) + len(eid) < 100 / nc:
                id_titre = eid + u' (' + nom + u')'
            else:
                id_titre = u'(' + nom + u')'
        i += 1
        if i > nl*nc:
            if inter: print ('*** Cannot plot: ', id_titre, ' - increase nc and/or nl')
            continue
        else:
            if inter: print (' plotting: ', eid, winstr(nom))
        nbm = gans.mslen(typmes[symb], eid, symb)
        if nbm == 0 and bresidu:
            continue
        ax = plt.subplot(nl, nc, i)
        plt.rcParams['legend.loc'] = 'best'
        # Nota available in mpl 1.2
        # plt.rcParams['axes.formatter.useoffset'] = False
        # print ('    ... Found {:d} MS for id: {:s}'.format(nbm,eid))
        tv, v, nv = gans.ts(typmes[symb], eid, symb, nbts) # int(0.5+(tmax - tmin)/step)+1, step)
        if not bresidu:
            ax.plot(tv/3600.,v,'b-', label='Simulation')
            ymin, ymax = min(v), max(v)
        if isinstance(item, tuple):
            ax.plot(tr/3600.,r,'g-', label='Reference')
            ymin, ymax = min(ymin, min(r)), max(ymax, max(r))
        if nbm > 0:
            tm, m, nm = gans.ms(typmes[symb], eid, symb, nbm)
            ymin, ymax = min(ymin, min(m)), max(ymax, max(m))
            if bresidu:
                tm, r, nm = tsadd(tm, -m, nm, tv, v, nv)
                mmax = max(abs(m)) * 0.0001
                if diff[1] == 'DA':
                    ax.plot(tm/3600.,r,'g-', label= 'Simulation - Mesure')
                else:
                    tm, s, nm = tsadd(tm, abs(m), nm, tv, abs(v), nv)
                    s = r/(s+mmax)
                    ax2 = ax.twinx()
                    ax2.plot(tm/3600.,s,'g-', label= u'Difference relative (S-M)')
                    dy2grid = 0.25*(max(s) - min(s))
                    if dy2grid == 0.0: dy2grid = 1.0
                    ax2.yaxis.set_major_locator(MultipleLocator(scaladjust(dy2grid)))
                    ax2.yaxis.set_major_formatter(y_formatter)
                    for t2 in ax2.get_yticklabels():
                        t2.set_color('g')
            else:
                ax.plot(tm/3600.,m,'r.', label= 'Mesure')
        plt.xlim(hours(tmin), hours(tmax))
        plt.legend(fontsize=6.)
        if (i > min(nc*nl,nbmes)-nc): plt.xlabel(u'temps (h)')
        # plt.ylabel(ylab)
        plt.title(id_titre, fontsize= 2.*fx/nc * min(1., 42./(len(id_titre)+1)))
        dygrid = 0.25*(ymax - ymin)
        if dygrid == 0.0: dygrid = 1.0
        nbh = hours(tmax) - hours(tmin)
        xstep = 6 if nbh < 40 else (12 if nbh < 80 else (24 if nbh < 160 else 48))
        ax.xaxis.set_major_locator(MultipleLocator(xstep))
        ax.yaxis.set_major_locator(MultipleLocator(scaladjust(dygrid)))
        ax.yaxis.set_major_formatter(y_formatter)
        plt.grid(True)
    plt.subplots_adjust(hspace=0.5, wspace=0.25,
                top=ftop, bottom=fbottom, left=fleft, right=fright)

    if fgname and len(fgname):
        from os.path import splitext
        plt.savefig(splitext(fgname)[0] + '.png')
    if inter:
        plt.ion()
        plt.show()
        # plt.close(fig)
    else:
        plt.clf()
        # plt.close(fig)
    del tv, v

def pageplot(mes, cmt, nl=3, nc=2, fgname=None, inter=True, lang= 'FR'):
    ''' Trace de series de donnees
        mes: liste des points e tracer, chacun se presentant:
            sous forme d'un tuple ('id', vecteur dates, vecteur valeurs de reference)
                -> l'attribut symb sera trace ainsi que le vecteur de reference
        nl, nc: disposition du graphe en nl lignes par nc colonnes
        fgname: nom du fichier resultat pour sauvegarde en plt
        inter: permet de ne pas afficher la courbe
    '''

    def hours(t):
        'Conversion de seconde en heures avec arrondi'
        return 0.01*int(0.5 + t/36.)

    nbmes = len(mes)
    if nbmes == 0: 
        return
    t = mes[0][1]
    tmin, tmax = min(t), max(t)
    for _s, t, r in mes[1:]:
        tmin, tmax = min(tmin, min(t)), max(tmax, max(t))
    if inter: 
        print (u' plotting {:d} time serie(s) on [{:.3s}, {:.3s}] hours'.format(
                    nbmes, strf3(hours(tmin)), strf3(hours(tmax))))

    # Utilisation de MatPlotLib
    # import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator, ScalarFormatter
    # from time import sleep

    # ajustement ponctuel du nb de graphes
    if nbmes > nc*nl:
        nl += 1
        if nbmes > nc*nl:
            nc += 1
    fx, fy, ftop, fbottom, fleft, fright = 16, 9, 0.9, 0.1, 0.075, 0.95
    if nc == 1: fx, fleft, fright = 6, 0.125, 0.9
    elif nc == 2: fx, fleft, fright = 11, 0.1, 0.925
    if nl == 1: fy, ftop, fbottom = 3, 0.8, 0.2
    elif nl == 2: fy, ftop, fbottom = 6, 0.85, 0.15
    fig = plt.gcf()
    if nc > 1 or nl > 2 or not fig:  #  or inter:
        if fig: plt.close(fig)
        fig = plt.figure(figsize=(fx, fy))
    else:
        fig.clf()
        fig.figsize = (fx, fy)
    y_formatter = ScalarFormatter(useOffset= False)
    plt.suptitle(cmt, fontsize=18.)
    i = 0
    time_legend = 'temps' if lang.upper() == 'FR' else 'time'
    for eid, tr, r in mes[0:nl*nc]:
        id_titre = eid
        i += 1
        if i > nl*nc:
            if inter: print ('*** Cannot plot: ', id_titre, ' - increase nc and/or nl')
            continue
        else:
            if inter: print (' plotting: ', eid)
        ax = plt.subplot(nl, nc, i)
        plt.rcParams['legend.loc'] = 'best'
        ax.plot(tr/3600.,r,'g-')
        ymin, ymax = min(r), max(r)
        plt.xlim(hours(tmin), hours(tmax))
        plt.legend(fontsize=6.)
        if (i > min(nc*nl,nbmes)-nc):
            plt.xlabel(time_legend + ' (h)')
        # plt.ylabel(ylab)
        plt.title(id_titre, fontsize= 2.*fx/nc * min(1., 42./(len(id_titre)+1)))
        dygrid = 0.25*(ymax - ymin)
        if dygrid == 0.0: dygrid = 1.0
        nbh = hours(tmax) - hours(tmin)
        xstep = 6 if nbh < 40 else (12 if nbh < 80 else (24 if nbh < 160 else 48))
        ax.xaxis.set_major_locator(MultipleLocator(xstep))
        ax.yaxis.set_major_locator(MultipleLocator(scaladjust(dygrid)))
        ax.yaxis.set_major_formatter(y_formatter)
        plt.grid(True)
    plt.subplots_adjust(hspace=0.5, wspace=0.25,
                top=ftop, bottom=fbottom, left=fleft, right=fright)

    if fgname and len(fgname):
        from os.path import splitext
        plt.savefig(splitext(fgname)[0] + '.png')
    if inter:
        plt.ion()
        plt.show()
        # plt.close(fig)
    else:
        plt.clf()
        # plt.close(fig)
    
    
#****f* functions/dist_to_poly, dist_p_seg, dist
# PURPOSE
#   Computes the distance of a point (xn, yn) to a polyline or a segment
# SYNTAX
#   * d, s1, s2 = dist_to_poly(xn, yn, xpoly, ypoly)
#   * d, s, slen = dist_p_seg(xn, yn, x1, y1, x2, y2)
#   * d = dist(x1, y1, x2, y2)
# ARGUMENTS
#   * double xn, yn: point coordinates
#   * double[] xpoly, ypoly: vertices of the polyline
#     (number of vertices in the polyline >= 2; 2 for a plain segment)
#   * double x1, y1, x2, y2: coordinates of a segment extremities
# RESULT
#   * double d: distance of point to the polyline or segment
#   * double s1, s2: curvilinear position of the point projection on the polyline, from each extremity
#   * double s: curvilinear position of the point projection on the segment, starting from (x1, y1)
#   * double slen: length of the segment (x1, y1), (x2, y2)
# REMARKS
#   * d= 0 means that the point is on the polyline.
#   * s1>0 and s2>0 means that the point projection is at least on one of the segments.
#  HISTORY
#   * 1.7.1 (170223) introduced compiled versions of these 3 functions;
#                    pure python versions names are prefixed with '_'
#****
def _dist(x1, y1, x2, y2):
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def _dist_p_seg (px, py, x1, y1, x2, y2):
    '''computes minimum distance from a point and a line segment '''
    # adapted from:
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
    seglen = _dist(x1, y1, x2, y2)

    if seglen < 0.00001:
        distpseg = _dist(px, py, x1, y1)
        return distpseg, 0.0 , seglen

    u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
    u = u1 / (seglen * seglen)

    if (u < 0.00001) or (u > 1):
        #// closest point does not fall within the line segment, take the shorter distance
        #// to an endpoint
        ix = _dist(px, py, x1, y1)
        iy = _dist(px, py, x2, y2)
        if ix > iy:
            distpseg = iy
            abscisse = seglen
        else:
            distpseg = ix
            abscisse = 0.0
    else:
        # Intersecting point is on the line, use the formula
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        distpseg = _dist(px, py, ix, iy)
        abscisse = _dist(x1, y1, ix, iy)
    return distpseg, abscisse, seglen

def _dist_to_poly(xn, yn, nb, xpoly, ypoly):
    '''computes minimum distance from a point and a polyline
    i.e. browsing consecutive segments of the polyline.
    Returns the distance, and curvilinear position from extremities'''
    x1, y1 = xpoly[0], ypoly[0]
    dmin = _dist(xn, yn, x1, y1)
    smin, totlen = 0.0, 0.0
    # Browse the segments
    for x2, y2 in izip(xpoly[1:], ypoly[1:]):
        d, s, slen = dist_p_seg(xn, yn, x1, y1, x2, y2)
        if d < dmin:
            # closest segment: remember the abscisse and distance
            smin = totlen + s
            dmin = d
        # update the total length
        totlen += slen
        x1, y1 = x2, y2
    return dmin, smin, totlen-smin

try:
    import ganessa._pyganutl as _utl
except ImportError:
    dist = _dist
    dist_p_seg = _dist_p_seg
    dist_to_poly = _dist_to_poly
else:
    dist = _utl.dist
    dist_p_seg = _utl.dist_p_seg
    def dist_to_poly(x, y, n, xp, yp):
        return _utl.dist_to_poly(x, y, xp, yp, n)

#****k* iterators/group
# SYNTAX
#   for items in group(iterable, count= 2):
# ARGUMENT
#   * iterable: iterable:
#   * int count: group size
# RESULT
#   this iterator allows to return the elements of iterable grouped
#   by lists of size count. The last list may contain less than group elements
# HISTORY
#   1.7.6 (170613): iterator added
#****
def group(iterable, count):
    '''returns elements from the iterable grouped by count
    The last set, possibly incomplete, is also returned'''
    itr = iter(iterable) 
    while True:
        # yield tuple([itr.next() for i in range(count)])
        chunk = []
        for _i in range(count):
            try:
                chunk.append(itr.next())
            except StopIteration:
                if not chunk:
                    raise
        yield chunk

def copyright_years(startyear, sep= '-'):
    '''Returns the years interval from start year'''
    syear = int(startyear)
    cyear = date.today().year
    ret = str(syear)
    if cyear != syear:
        ret += sep + str(cyear)
    return ret

def cmp_version(actual, target):
    '''Compares version numbers'''
    if isinstance(target, list):
        tgt = target
    elif isinstance(target, tuple):
        tgt = list(target)
    else:
        tgt = map(int, target.split('.'))
    return cmp(map(int, actual.split('.')), tgt)

#****f* functions/update_package
# SYNTAX
#   stat = update_package(package_name, minvers [, pypi_name=None] [, deps= False] [, https_proxy= None])
# ARGUMENT
#   * string package_name: name of the package as used in the import statement
#   * string minvers: minimum version required, in the form x.y[.z]
#   * optional string pypi_name: package name in pypi, if different from package_name
#   * optional bool deps: set to True to install the dependencies
#   * optional string https_proxy: url and port of the proxy if required.
# RESULT
#   bool stat: true if the package has been installed or updated
# REMARKS
#   * minvers can also be provided as a list or tuple of ints
# HISTORY
#   1.8.1 (171009) added
#****

def update_package(package_name, minvers, pypi_name=None, deps= False, https_proxy= None):
    '''Update package using pip if too old - returns True if updated'''
    from importlib import import_module
    from sys import prefix as pyroot
    try:
        pkg = import_module(package_name)
    except ImportError:
        vers = ''
    else:
        try:
            vers = pkg.__version__
        except AttributeError:
            try:
                vers = pkg.__VERSION__
            except AttributeError:
                vers = '0.0'
        del pkg
    # Do nothing if already installed or match version
    if pypi_name is None:
        pypi_name = package_name
    cmd = [OP.join(pyroot, 'Scripts', 'pip'), 'install', '--default-timeout', '2', pypi_name]
    if not deps:
        cmd[4:4] = ['--no-deps']
    if vers:
        cmd[4:4] = ['--upgrade']
        if minvers and cmp_version(vers, minvers) >= 0:
            print(package_name, 'is already installed and >= ', minvers)
            return False
        else:
            print(package_name, 'is being updated')
    else:
        print(package_name, 'is being installed')
    
    proxy = b'HTTPS_PROXY'
    envir = dict(os.environ)
    if https_proxy is None:
        print('  Using current proxy settings')
    elif https_proxy:
        envir[proxy] = str(https_proxy)
        print('  Using proxy:', https_proxy)
    else:
        if proxy in envir:
            del envir[proxy]
        print('  Connection without proxy')
    print('  running pip')
    subprocess.call(cmd, env= envir)
    return True
    

_logo_SUEZ_b64 = '''
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
'''

def logo_SUEZ_b64():
    return _logo_SUEZ_b64
    