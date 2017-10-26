#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Python kontocheck package
#
# Copyright (c) 2013 by joonis new media <thimo.kraemer@joonis.de>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

"""Python ctypes wrapper of the konto_check library.

This module is based on `konto_check <http://kontocheck.sourceforge.net>`_,
a small library to check German bank accounts. It implements all check
methods and IBAN generation rules, published by the German Central Bank.

In addition it provides access to the SCL Directory and the possibility
to verify VAT-IDs by the German Federal Central Tax Office.

Example:

.. sourcecode:: python
    
    import kontocheck
    kontocheck.lut_load()
    bankname = kontocheck.get_name('37040044')
    iban = kontocheck.create_iban('37040044', '532013000')
    kontocheck.check_iban(iban)
    bic = kontocheck.get_bic(iban)
"""

from __future__ import division, absolute_import, print_function, unicode_literals

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    from io import open
    str = unicode
    chr = unichr
    range = xrange
    input = raw_input
    import itertools
    filter = itertools.ifilter
    map = itertools.imap
    zip = itertools.izip
    nativestring = bytes
    
    from xmlrpclib import ServerProxy
else:
    nativestring = str
    
    from xmlrpc.client import ServerProxy
import os, re
import atexit
import struct
from ctypes import c_char_p, c_int, c_void_p, create_string_buffer, \
                    POINTER, byref, CDLL, cdll, util, cast
c_int_p = POINTER(c_int)

__version__ = '6.01.0'

__all__ = ['get_version', 'lut_load', 'lut_is_valid', 'cleanup',
            'check_iban', 'create_iban', 'get_bic', 'get_name',
            'get_postalcode', 'get_city', 'scl_load', 'scl_get_routing',
            'scl_get_bankname', 'bff_check_vatid', 'KontoCheckError']


# Get the path to the default lut file
_PATH = os.path.dirname(os.path.abspath(__file__))
_LUT_PATH = os.path.join(_PATH, 'data', 'blz.lut2')
if not os.path.isfile(_LUT_PATH):
    _LUT_PATH = None

# Py2.6 requires a byte string
_PY_BIT = struct.calcsize(b'P') * 8


if os.name == 'nt':
    libc = cdll.msvcrt
else:
    libc = CDLL(util.find_library('c'))
libc.free.restype = None
libc.free.argtypes = (c_void_p,)


libpath = os.path.join(_PATH, 'lib')
libext = (os.name == 'nt' and '%s.dll' % _PY_BIT or '.so')
for libname in os.listdir(libpath):
    if libname.startswith('kontocheck') and libname.endswith(libext):
        libpath = os.path.join(libpath, libname)
        break
else:
    raise RuntimeError('kontocheck library not found')

libkontocheck = CDLL(libpath)
 
_SCL_DATA = {}

def scl_load(path=None, encoding='latin1'):
    """
    Loads the SCL directory from the file specified by *path*.
    If *path* is omitted the shipped SCL directory is used, published
    by the German Central Bank. It is loaded automatically by accessing
    the SCL functions.
    """
    if not path:
        path = os.path.join(_PATH, 'data', 'scl.csv')
    with open(path, 'r', encoding=encoding) as fh:
        # Skip first line
        fh.readline()
        # Check fields
        fields = fh.readline().strip()
        if fields != 'BIC;Name;Service SCT;Service SDD;Service COR1;Service B2B;Service SCC':
            raise RuntimeError('Unknown SCL file format')
        # Load data
        _SCL_DATA.clear()
        for line in fh.readlines():
            line = line.strip()
            if not line:
                continue
            bic, name, sct, sdd, cor1, b2b, scc = line.split(';')
            _SCL_DATA[bic.strip()] = {
                'name': name.strip(),
                'sct': bool(int(sct)),
                'sdd': bool(int(sdd)),
                'cor1': bool(int(cor1)),
                'b2b': bool(int(b2b)),
                'scc': bool(int(scc)),
            }

def scl_get_routing(bic):
    """
    Returns a dictionary with the SEPA routing information for the given
    BIC from the SCL directory, published by the German Central Bank.
    """
    if isinstance(bic, bytes):
        bic = bic.decode('ascii')
    bic = bic.upper()
    if len(bic) not in (8, 11):
        raise ValueError('invalid bic "%s"' % bic)
    bic = bic.ljust(11, 'X')
    if not _SCL_DATA:
        scl_load()
    result = _SCL_DATA.get(bic) or _SCL_DATA.get(bic[:8])
    if not result:
        raise ValueError('unknown bic "%s"' % bic)
    result = result.copy()
    return result

def scl_get_bankname(bic):
    """
    Returns the bank name for the given BIC from the SCL directory,
    published by the German Central Bank.
    """
    return scl_get_routing(bic)['name']


def bff_check_vatid(local_vatid, remote_vatid, company='', city='',
                        postalcode='', street='', request_mail=False):
    """
    Checks a VAT-ID for validity using the webservice provided by the
    German Federal Central Tax Office. For further information see
    https://evatr.bff-online.de/eVatR/xmlrpc/
    
    Performs a basic or qualified check depending on the given parameters
    as described on the following website:
    https://evatr.bff-online.de/eVatR/xmlrpc/schnittstelle
    
    Returns a dictionary with keys as described on the following website:
    https://evatr.bff-online.de/eVatR/xmlrpc/aufbau
    
    The webservice is available daily between 5:00 and 23:00 (CET).
    """
    server = ServerProxy('https://evatr.bff-online.de/')
    result = server.evatrRPC(local_vatid, remote_vatid, company, city,
                        postalcode, street, request_mail and 'ja' or 'nein')
    result = re.findall('<string>(.*?)</string>', result)
    result = [v.strip() for v in result]
    return dict(zip(*[iter(result)] * 2))


#~ /* Funktion get_kto_check_version() +§§§1 */
#~ /* ###########################################################################
#~ * #  Diese Funktion gibt die Version und das Datum der Kompilierung der     #
#~ * #  konto_check library als String zurück.                                .#
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.get_kto_check_version.restype = c_char_p
libkontocheck.get_kto_check_version.argtypes = None
def get_version():
    """
    Get the version of the compiled konto_check library.
    """
    return libkontocheck.get_kto_check_version().decode('latin1')

#~ /* Funktion kto_check_encoding() +§§§1 */
#~ /* ###########################################################################
#~ * # Diese Funktion setzt die Kodierung für die konto_check Bibliothek fest. #
#~ * # Es wird sowohl die Kodierung für die Fehlermeldungen als auch die der   #
#~ * # LUT-Datei gesetzt. Innerhalb der LUT-Datei sind die Werte im Format     #
#~ * # ISO-8859-1 gespeichert; sie werden bei der Initialisierung konvertiert. #
#~ * #                                                                         #
#~ * # Für den Parameter mode werden die folgenden Werte akzeptiert:           #
#~ * #     1,'i','I':  ISO-8859-1                                              #
#~ * #     2,'u','U':  UTF-8                                                   #
#~ * #     3,'h','H':  HTML-Entities                                           #
#~ * #     4,'d','D':  DOS (CP850)                                             #
#~ * #     51          Fehlermeldungen als Makronamen, Rest in ISO-8859-1      #
#~ * #     52          Fehlermeldungen als Makronamen, Rest in UTF-8           #
#~ * #     53          Fehlermeldungen als Makronamen, Rest in HTML-Entities   #
#~ * #     54          Fehlermeldungen als Makronamen, Rest in DOS (CP850)     #
#~ * #                                                                         #
#~ * # Rückgabewert ist der aktuell gesetzte Modus (als Zahl). Falls die       #
#~ * # Funktion mit dem Parameter 0 aufgerufen wird, wird nur die aktuelle     #
#~ * # Kodierung zurückgegeben.                                                #
#~ * #                                                                         #
#~ * # Copyright (C) 2011 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.kto_check_encoding.restype = c_int
libkontocheck.kto_check_encoding.argtypes = (c_int,)
# Set encoding of returned data to latin1
libkontocheck.kto_check_encoding(1)

#~ /* Funktion lut_cleanup() +§§§1 */
#~ /* ###########################################################################
#~ * # lut_cleanup(): Aufräuarbeiten                                           #
#~ * # Die Funktion lut_cleanup() gibt allen belegten Speicher frei und setzt  #
#~ * # die entsprechenden Variablen auf NULL.                                  #
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_cleanup.restype = c_void_p
libkontocheck.lut_cleanup.argtypes = None
def cleanup():
    """
    Reset and free all loaded LUT data.
    
    It is called by default when the program exits.
    """
    return libkontocheck.lut_cleanup()
# Clean up at exit in any case
atexit.register(cleanup)

#~ /* Funktion lut_init()  */
#~ /* ###########################################################################
#~ * # Diese Funktion dient dazu, die konto_check Bibliothek zu initialisieren #
#~ * # und bietet ein (im Gegensatz zu kto_check_init) stark vereinfachtes     #
#~ * # Benutzerinterface (teilweise entlehnt von kto_check_init_p). Zunächst   #
#~ * # wird getestet, ob die Bibliothek schon mit der angegebenen Datei (bzw.  #
#~ * # genauer mit dem gewünschten Datensatz aus der Datei) initialisiert      #
#~ * # wurde (mittels der Datei-ID aus dem Infoblock des gewählten bzw.        #
#~ * # gültigen Sets). Falls die Datei-IDs nicht übereinstimmen, wird eine     #
#~ * # Neuinitialisierung gemacht, andernfalls (nur falls notwendig) eine      #
#~ * # inkrementelle Initialisierung, um noch benötigte Blocks nachzuladen.    #
#~ * # Falls schon alle gewünschten Blocks geladen sind, wird nichts gemacht.  #
#~ * #                                                                         #
#~ * # Copyright (C) 2008 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_init.restype = c_int
libkontocheck.lut_init.argtypes = (c_char_p, c_int, c_int)
def lut_load(field_set=5, path=None):
    """
    Load the given field set from a LUT file specified by *path*.
    
    If *path* is omitted or *None* the shipped LUT file is used.
    
    Available field sets (default is 5):
    
    =====  =============================================
    Value  Fields to load
    =====  =============================================
    0      BLZ, Prüfziffer und Filialen (always loaded)
    1      Kurzname
    2      Kurzname, BIC
    3      Name, PLZ, Ort
    4      Name, PLZ, Ort, BIC
    5      Name+Kurzname, PLZ, Ort, BIC
    6      Name+Kurzname, PLZ, Ort, BIC, Nachfolge-BLZ
    7      Name+Kurzname, PLZ, Ort, BIC, Nachfolge-BLZ,
           Änderungsdatum
    8      Name+Kurzname, PLZ, Ort, BIC, Nachfolge-BLZ,
           Änderungsdatum, Löschdatum
    9      Name+Kurzname, PLZ, Ort, BIC, Nachfolge-BLZ,
           Änderungsdatum, Löschdatum, PAN, Laufende Nr.
           des Datensatzes (kompletter Datensatz)
    =====  =============================================
    """
    path = path or _LUT_PATH
    if not path:
        raise ValueError('path to lut file required')
    if isinstance(path, str):
        path = path.encode(sys.getfilesystemencoding())
    retval = libkontocheck.lut_init(path, field_set, 0)
    if retval != KontoCheckError.OK:
        raise KontoCheckError(retval)


#~ /* Funktion lut_valid() +§§§1 */
#~ /* ###########################################################################
#~ * # Die Funktion lut_valid() testet, ob die geladene LUT-Datei aktuell      #
#~ * # gültig ist. Im Gegensatz zu lut_info wird kein Speicher allokiert.      #
#~ * #                                                                         #
#~ * # Rückgabewerte:                                                          #
#~ * #    LUT2_VALID:             Der Datenblock ist aktuell gültig            #
#~ * #    LUT2_NO_LONGER_VALID:   Der Datenblock ist nicht mehr gültig         #
#~ * #    LUT2_NOT_YET_VALID:     Der Datenblock ist noch nicht gültig         #
#~ * #    LUT2_NO_VALID_DATE:     Der Datenblock enthält kein Gültigkeitsdatum #
#~ * #    LUT2_NOT_INITIALIZED:   die library wurde noch nicht initialisiert   #
#~ * #                                                                         #
#~ * # Copyright (C) 2008 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_valid.restype = c_int
libkontocheck.lut_valid.argtypes = None
def lut_is_valid():
    """
    Check if the current LUT file is valid.
    
    If this function returns *False*, you should update the LUT file
    and/or the whole kontocheck library.
    
    Raises an exception if no LUT file was loaded.
    """
    retval = libkontocheck.lut_valid()
    if retval in (KontoCheckError.LUT2_NOT_INITIALIZED, KontoCheckError.LUT2_NO_VALID_DATE):
        raise KontoCheckError(retval)
    return retval == KontoCheckError.LUT2_VALID

#~ /* Funktion lut_name() +§§§2 */
#~ /* ###########################################################################
#~ * # lut_name(): Banknamen (lange Form) bestimmen                            #
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_name.restype = c_char_p
libkontocheck.lut_name.argtypes = (c_char_p, c_int, c_int_p)

#~ /* Funktion lut_name_kurz() +§§§2 */
#~ /* ###########################################################################
#~ * # lut_name_kurz(): Kurzbezeichnung mit Ort einer Bank bestimmen           #
#~ * #                                                                         #
#~ * # Kurzbezeichnung und Ort sollen für die Empfängerangaben auf Rechnungen  #
#~ * # und Formularen angegeben werden. Hierdurch wird eine eindeutige Zu-     #
#~ * # ordnung der eingereichten Zahlungsaufträge ermöglicht. Auf Grund der    #
#~ * # Regelungen in den Richtlinien beziehungsweise Zahlungsverkehrs-Abkommen #
#~ * # der deutschen Kreditwirtschaft ist die Länge der Angaben für die        #
#~ * # Bezeichnung des Kreditinstituts begrenzt.                               #
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_name_kurz.restype = c_char_p
libkontocheck.lut_name_kurz.argtypes = (c_char_p, c_int, c_int_p)

def get_name(bankcode, short_form=False):
    """
    Get the name of a bank by a given bankcode (or German IBAN).
    
    Returns the short or long version of the name.
    """
    if isinstance(bankcode, str):
        bankcode = bankcode.encode('ascii')
    if bankcode.startswith(b'DE'):
        bankcode = bankcode[4:12]
    retval = c_int()
    if short_form:
        name = libkontocheck.lut_name_kurz(bankcode, 0, byref(retval))
    else:
        name = libkontocheck.lut_name(bankcode, 0, byref(retval))
    if not name and retval.value != KontoCheckError.OK:
        raise KontoCheckError(retval.value)
    return name.decode('latin1')

#~ /* Funktion lut_plz() +§§§2 */
#~ /* ###########################################################################
#~ * # lut_plz(): Postleitzahl bestimmen                                       #
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_plz.restype = c_int
libkontocheck.lut_plz.argtypes = (c_char_p, c_int, c_int_p)
def get_postalcode(bankcode):
    """
    Get the postalcode of a bank by a given bankcode (or German IBAN).
    """
    if isinstance(bankcode, str):
        bankcode = bankcode.encode('ascii')
    if bankcode.startswith(b'DE'):
        bankcode = bankcode[4:12]
    retval = c_int()
    postalcode = libkontocheck.lut_plz(bankcode, 0, byref(retval))
    if not postalcode and retval.value != KontoCheckError.OK:
        raise KontoCheckError(retval.value)
    return str(postalcode)

#~ /* Funktion lut_ort() +§§§2 */
#~ /* ###########################################################################
#~ * # lut_ort(): Sitz einer Bank bestimmen                                    #
#~ * #                                                                         #
#~ * # Copyright (C) 2007 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.lut_ort.restype = c_char_p
libkontocheck.lut_ort.argtypes = (c_char_p, c_int, c_int_p)
def get_city(bankcode):
    """
    Get the city of a bank by a given bankcode (or German IBAN).
    """
    if isinstance(bankcode, str):
        bankcode = bankcode.encode('ascii')
    if bankcode.startswith(b'DE'):
        bankcode = bankcode[4:12]
    retval = c_int()
    city = libkontocheck.lut_ort(bankcode, 0, byref(retval))
    if not city and retval.value != KontoCheckError.OK:
        raise KontoCheckError(retval.value)
    return city.decode('latin1')

#~ /* Funktion iban2bic() +§§§1 */
#~ /* ###########################################################################
#~ * # Die Funktion iban2bic extrahiert aus einer IBAN (International Bank     #
#~ * # Account Number) Kontonummer und Bankleitzahl, und bestimmt zu der BLZ   #
#~ * # den zugehörigen BIC. Voraussetzung ist natürlich, daß das BIC Feld in   #
#~ * # der geladenen LUT-Datei enthalten ist. BLZ und Kontonummer werden,      #
#~ * # falls gewünscht, in zwei Variablen zurückgegeben.                       #
#~ * #                                                                         #
#~ * # Die Funktion arbeitet nur für deutsche Banken, da für andere keine      #
#~ * # Infos vorliegen.                                                        #
#~ * #                                                                         #
#~ * # Parameter:                                                              #
#~ * #    iban:       die IBAN, zu der die Werte bestimmt werden sollen        #
#~ * #    retval:     NULL oder Adresse einer Variablen, in die der Rückgabe-  #
#~ * #                wert der Umwandlung geschrieben wird                     #
#~ * #    blz:        NULL, oder Adresse eines Speicherbereichs mit mindestens #
#~ * #                9 Byte, in den die BLZ geschrieben wird                  #
#~ * #    kto:        NULL, oder Adresse eines Speicherbereichs mit mindestens #
#~ * #                11 Byte, in den die Kontonummer geschrieben wird.        #
#~ * #                                                                         #
#~ * # Rückgabe:      der zu der übergebenen IBAN gehörende BIC                #
#~ * #                                                                         #
#~ * # Copyright (C) 2008 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.iban2bic.restype = c_char_p
libkontocheck.iban2bic.argtypes = (c_char_p, c_int_p, c_char_p, c_char_p)
def get_bic(iban):
    """
    Get the corresponding BIC to a given IBAN. 
    """
    if isinstance(iban, str):
        iban = iban.encode('ascii')
    retval = c_int()
    bankcode = create_string_buffer(9)
    account = create_string_buffer(11)
    bic = libkontocheck.iban2bic(iban, byref(retval), bankcode, account)
    if retval.value != KontoCheckError.OK:
        raise KontoCheckError(retval.value)
    return bic.decode('latin1')

#~ /* Funktion iban_check() +§§§1 */
#~ /* ###########################################################################
#~ * # Die Funktion iban_check prüft, ob die Prüfsumme des IBAN ok ist und     #
#~ * # testet außerdem noch die BLZ/Konto Kombination. Für den Test des Kontos #
#~ * # wird keine Initialisierung gemacht; diese muß vorher erfolgen.          #
#~ * #                                                                         #
#~ * # Parameter:                                                              #
#~ * #    iban:       IBAN die getestet werden soll                            #
#~ * #    retval:     NULL oder Adresse einer Variablen, in die der Rückgabe-  #
#~ * #                wert der Kontoprüfung geschrieben wird                   #
#~ * #                                                                         #
#~ * # Copyright (C) 2008 Michael Plugge <m.plugge@hs-mannheim.de>             #
#~ * ###########################################################################
#~ */
libkontocheck.iban_check.restype = c_int
libkontocheck.iban_check.argtypes = (c_char_p, c_int_p)
def check_iban(iban, error=False):
    """
    Check an IBAN for validity.
    
    For German IBANs also the check digit of the account number is
    verified. If *error* is set to *True*, an exception is raised
    on failure.
    """
    if isinstance(iban, str):
        iban = iban.encode('ascii')
    retval = c_int()
    result = libkontocheck.iban_check(iban, byref(retval))
    result = result or retval.value
    if not error:
        return result == KontoCheckError.OK
    if result != KontoCheckError.OK:
        raise KontoCheckError(result)
    return True

#~ /* Funktion iban_gen(), iban_bic_gen() und iban_bic_gen1 +§§§1 */
#~ /* ###########################################################################
#~ * # Die Funktion iban_gen generiert aus Bankleitzahl und Kontonummer eine   #
#~ * # IBAN (International Bank Account Number). Die Funktion ist lediglich    #
#~ * # zum Test der anderen IBAN-Routinen geschrieben, und sollte nicht zum    #
#~ * # Generieren realer IBANs benutzt werden (s.u.).                          #
#~ * #                                                                         #
#~ * # Update Juni 2011:                                                       #
#~ * # Es wird die Verbotsliste der Sparkassen ausgewertet, so daß für         #
#~ * # Institute, die einer Selbstberechnung nicht zugestimmt haben, keine     #
#~ * # IBAN berechnet wird. Damit dürften die Berechnungen (falls die "rote    #
#~ * # Liste" in der LUT-Datei vorhanden ist und ausgewertet wird) doch        #
#~ * # brauchbar sein.                                                         #
#~ * #                                                                         #
#~ * # Update Mai 2013:                                                        #
#~ * # Von der Bundesbank sind jetzt die IBAN-Regeln veröffentlicht, so daß    #
#~ * # eine zuverlässige Berechnung der IBAN in den meisten Fällen möglich     #
#~ * # ist. Bei einer Reihe Banken wird in der IBAN-Regel die BLZ, und manch-  #
#~ * # mal auch die Kontonummer durch einen anderen Wert ersetzt, wodurch      #
#~ * # sich natürlich auch der BIC ändert. Daher gibt es zusätzlich zu der     #
#~ * # alten Funktion iban_gen() jetzt noch eine weitere Funktion              #
#~ * # iban_bic_gen(), bei der in drei zusätzlichen Parametern noch der BIC    #
#~ * # sowie die benutzte BLZ und Kontonummer zurückgegeben wird (es ließe     #
#~ * # sich auch mit der Funktion iban2bic() machen, aber so hat man nur einen #
#~ * # einzigen Funktionsaufruf dafür).                                        #
#~ * #                                                                         #
#~ * # Die Funktion iban_bic_gen1() entspricht der Funktion iban_bic_gen(),    #
#~ * # nur werden die neue Kontonummer und BLZ nicht zurückgegeben. Diese      #
#~ * # Funktion wird für VC# und VB.net benutzt, um die Parameterübergabe      #
#~ * # möglich zu machen.                                                      #
#~ * #                                                                         #
#~ * # Parameter:                                                              #
#~ * #    blz:        Bankleitzahl. Falls der Bankleitzahl ein + vorangestellt #
#~ * #                wird, wird die entsprechende Bankverbindung nicht auf    #
#~ * #                Korrektheit getestet (ansonsten schon; dies ist zum      #
#~ * #                Debuggen der konto_check Bibliothek gedacht).            #
#~ * #                                                                         #
#~ * #                Falls der Bankleitzahl ein @ vorangestellt wird, wird    #
#~ * #                nicht geprüft, ob die Bank einer Selbstberechnung der    #
#~ * #                IBAN zugestimmt hat. Das Ergebnis kann dann u.U. fehler- #
#~ * #                haft sein.                                               #
#~ * #                                                                         #
#~ * #    blz2:       Für die Generierung der IBAN benutzte BLZ. Die BLZ wird  #
#~ * #                durch viele IBAN-Regeln geändert und wird in dieser      #
#~ * #                Variablen zurückgegeben. Für die Variable muß die        #
#~ * #                aufrufende Funktion Speicher bereitstellen (z.B. ein     #
#~ * #                lokales char-Array), der Wert für blz2 wird nur in       #
#~ * #                den angegebenen Speicher kopiert. Falls für die Variable #
#~ * #                NULL übergeben wird, wird sie ignoriert.                 #
#~ * #                                                                         #
#~ * #                                                                         #
#~ * #    kto2:       Für die Generierung der IBAN benutzte Kontonummer. Auch  #
#~ * #                die Kontonummmer wird von manchen Regeln geändert; die   #
#~ * #                benutzte Kontonummer kann mit dieser Variablen ermittelt #
#~ * #                werden. Der Speicher muß ebenfalls von der aufrufenden   #
#~ * #                Funktion bereitgestellt werden. Falls für die Variable   #
#~ * #                NULL übergeben wird, wird sie ignoriert.                 #
#~ * #                                                                         #
#~ * #    bic:        NULL oder Adresse einer Variablen, in die der aktuelle   #
#~ * #                BIC geschrieben wird (nur bei iban_bic_gen() ).          #
#~ * #                                                                         #
#~ * #    kto:        Kontonummer                                              #
#~ * #    retval:     NULL oder Adresse einer Variablen, in die der Rückgabe-  #
#~ * #                wert der Kontoprüfung geschrieben wird                   #
#~ * #                                                                         #
#~ * # Rückgabe:      die erzeugte IBAN. Für die Rückgabe wird Speicher        #
#~ * #                allokiert; dieser muß nach der Benutzung wieder frei-    #
#~ * #                gegeben werden. Falls der Test der Bankverbindung        #
#~ * #                fehlschlägt, wird der entsprechende Fehlercode in die    #
#~ * #                Variable retval geschrieben und NULL zurückgegeben.      #
#~ * #                                                                         #
#~ * # Copyright (C) 2008,2013 Michael Plugge <m.plugge@hs-mannheim.de>        #
#~ * ###########################################################################
#~ */
libkontocheck.iban_bic_gen.restype = c_void_p # c_char_p
libkontocheck.iban_bic_gen.argtypes = (c_char_p, c_char_p,
                POINTER(c_char_p), c_char_p, c_char_p, c_int_p)
def create_iban(bankcode, account, get_bic=False):
    """
    Create a valid IBAN by given bank code and account.
    
    If *get_bic* evaluates to *True*, a 2-tupel of (IBAN, BIC) is returned.
    """
    if isinstance(bankcode, str):
        bankcode = bankcode.encode('ascii')
    if isinstance(account, str):
        account = account.encode('ascii')
    bic = c_char_p(b'\0'*12)
    bankcode2 = create_string_buffer(9)
    account2 = create_string_buffer(11)
    retval = c_int()
    iban_p = libkontocheck.iban_bic_gen(bankcode, account,
                    byref(bic), bankcode2, account2, byref(retval))
    iban = cast(iban_p, c_char_p).value
    libc.free(iban_p)
    if retval.value < KontoCheckError.OK:
        raise KontoCheckError(retval.value)
    iban = iban.decode('latin1')
    iban = iban.replace(' ', '')
    if get_bic:
        bic = bic.value.decode('latin1')
        return iban, bic
    return iban


class KontoCheckError(Exception):
    """
    The konto_check library returned an error.
    """
    
    # Ungültiges Handle angegeben
    INVALID_HANDLE = -150
    # Ungültiger Index für die biq_*() Funktionen
    INVALID_BIQ_INDEX = -149
    # Der Array-Index liegt außerhalb des gültigen Bereichs
    ARRAY_INDEX_OUT_OF_RANGE = -148
    # Es werden nur deutsche IBANs unterstützt
    IBAN_ONLY_GERMAN = -147
    # Falscher Parametertyp für die Funktion
    INVALID_PARAMETER_TYPE = -146
    # Es werden nur deutsche BICs unterstützt
    BIC_ONLY_GERMAN = -145
    # Die Länge des BIC muß genau 8 oder 11 Zeichen sein
    INVALID_BIC_LENGTH = -144
    # Die IBAN-Prüfsumme stimmt, die BLZ sollte aber durch eine zentrale BLZ ersetzt werden.
    # Die Richtigkeit der IBAN kann nur mit einer Anfrage bei der Bank ermittelt werden
    IBAN_CHKSUM_OK_RULE_IGNORED_BLZ = -143
    # Die IBAN-Prüfsumme stimmt, konto_check wurde jedoch noch nicht initialisiert (Kontoprüfung nicht möglich)
    IBAN_CHKSUM_OK_KC_NOT_INITIALIZED = -142
    # Die IBAN-Prüfsumme stimmt, die BLZ ist allerdings ungültig
    IBAN_CHKSUM_OK_BLZ_INVALID = -141
    # Die IBAN-Prüfsumme stimmt, für die Bank gibt es allerdings eine (andere) Nachfolge-BLZ
    IBAN_CHKSUM_OK_NACHFOLGE_BLZ_DEFINED = -140
    # es konnten nicht alle Datenblocks die für die IBAN-Berechnung notwendig sind geladen werden
    LUT2_NOT_ALL_IBAN_BLOCKS_LOADED = -139
    # Der Datensatz ist noch nicht gültig, außerdem konnten nicht alle Blocks geladen werden
    LUT2_NOT_YET_VALID_PARTIAL_OK = -138
    # Der Datensatz ist nicht mehr gültig, außerdem konnten nicht alle Blocks geladen werdeng
    LUT2_NO_LONGER_VALID_PARTIAL_OK = -137
    # ok, bei der Initialisierung konnten allerdings ein oder mehrere Blocks nicht geladen werden
    LUT2_BLOCKS_MISSING = -136
    # falsch, es wurde ein Unterkonto hinzugefügt (IBAN-Regel)
    FALSE_UNTERKONTO_ATTACHED = -135
    # Die BLZ findet sich in der Ausschlussliste für IBANBerechnungen
    BLZ_BLACKLISTED = -134
    # Die BLZ ist in der Bundesbank-Datei als gelöscht markiert und somit ungültig
    BLZ_MARKED_AS_DELETED = -133
    # Die IBAN-Prüfsumme stimmt, es gibt allerdings einen Fehler in der eigenen IBAN-Bestimmung (wahrscheinlich falsch)
    IBAN_CHKSUM_OK_SOMETHING_WRONG = -132
    # Die IBAN-Prüfsumme stimmt, eine IBAN-Berechnung ist allerdings nicht erlaubt (wahrscheinlich falsch)
    IBAN_CHKSUM_OK_NO_IBAN_CALCULATION = -131
    # Die IBAN-Prüfsumme stimmt, es wurde allerdings eine IBAN-Regel nicht beachtet (wahrscheinlich falsch)
    IBAN_CHKSUM_OK_RULE_IGNORED = -130
    # Die IBAN-Prüfsumme stimmt, es fehlt aber ein Unterkonto (wahrscheinlich falsch)
    IBAN_CHKSUM_OK_UNTERKTO_MISSING = -129
    # Die BLZ passt nicht zur angegebenen IBAN-Regel
    IBAN_INVALID_RULE = -128
    # Die Kontonummer ist nicht eindeutig (es gibt mehrere Möglichkeiten)
    IBAN_AMBIGUOUS_KTO = -127
    # Die IBAN-Regel ist noch nicht implementiert
    IBAN_RULE_NOT_IMPLEMENTED = -126
    # Die IBAN-Regel ist nicht bekannt
    IBAN_RULE_UNKNOWN = -125
    # Für die Bankverbindung ist keine IBAN-Berechnung erlaubt
    NO_IBAN_CALCULATION = -124
    # Die Bankverbindung ist mit der alten BLZ stimmig, mit der Nachfolge-BLZ nicht
    OLD_BLZ_OK_NEW_NOT = -123
    # Das Feld IBAN-Regel wurde nicht initialisiert
    LUT2_IBAN_REGEL_NOT_INITIALIZED = -122
    # Die Länge der IBAN für das angegebene Länderkürzel ist falsch
    INVALID_IBAN_LENGTH = -121
    # Keine Bankverbindung/IBAN angegeben
    LUT2_NO_ACCOUNT_GIVEN = -120
    # Ungültiges Zeichen ()+-/&.,'\ für die Volltextsuche gefunden
    LUT2_VOLLTEXT_INVALID_CHAR = -119
    # Die Volltextsuche sucht jeweils nur ein einzelnes Wort, benutzen Sie lut_suche_multiple() zur Suche nach mehreren Worten
    LUT2_VOLLTEXT_SINGLE_WORD_ONLY = -118
    # die angegebene Suchresource ist ungültig
    LUT_SUCHE_INVALID_RSC = -117
    # Suche: im Verknüpfungsstring sind nur die Zeichen a-z sowie + und - erlaubt
    LUT_SUCHE_INVALID_CMD = -116
    # Suche: es müssen zwischen 1 und 26 Suchmuster angegeben werden
    LUT_SUCHE_INVALID_CNT = -115
    # Das Feld Volltext wurde nicht initialisiert
    LUT2_VOLLTEXT_NOT_INITIALIZED = -114
    # das Institut erlaubt keine eigene IBANBerechnung
    NO_OWN_IBAN_CALCULATION = -113
    # die notwendige Kompressions-Bibliothek wurden beim Kompilieren nicht eingebunden
    KTO_CHECK_UNSUPPORTED_COMPRESSION = -112
    # der angegebeneWert für die Default-Kompression ist ungültig
    KTO_CHECK_INVALID_COMPRESSION_LIB = -111
    # (nicht mehr als Fehler, sondern positive Ausgabe-Dummy für den alten Wert)
    OK_UNTERKONTO_ATTACHED_OLD = -110
    # Ungültige Signatur im Default-Block
    KTO_CHECK_DEFAULT_BLOCK_INVALID = -109
    # Die maximale Anzahl Einträge für den Default-Block wurde erreicht
    KTO_CHECK_DEFAULT_BLOCK_FULL = -108
    # Es wurde noch kein Default-Block angelegt
    KTO_CHECK_NO_DEFAULT_BLOCK = -107
    # Der angegebene Schlüssel wurde im Default-Block nicht gefunden
    KTO_CHECK_KEY_NOT_FOUND = -106
    # Beide Datensätze sind nicht mehr gültig, dieser ist aber jünger als der andere
    LUT2_NO_LONGER_VALID_BETTER = -105
    # Die Auftraggeber-Kontonummer des C-Datensatzes unterscheidet sich von der des A-Satzes
    DTA_SRC_KTO_DIFFERENT = -104
    # Die Auftraggeber-Bankleitzahl des C-Datensatzes unterscheidet sich von der des A-Satzes
    DTA_SRC_BLZ_DIFFERENT = -103
    # Die DTA-Datei enthält (unzulässige) Zeilenvorschübe
    DTA_CR_LF_IN_FILE = -102
    # ungültiger Typ bei einem Erweiterungsblock eines C-Datensatzes
    DTA_INVALID_C_EXTENSION = -101
    # Es wurde ein C-Datensatz erwartet, jedoch ein E-Satz gefunden
    DTA_FOUND_SET_A_NOT_C = -100
    # Es wurde ein C-Datensatz erwartet, jedoch ein E-Satz gefunden
    DTA_FOUND_SET_E_NOT_C = -99
    # Es wurde ein C-Datensatzerweiterung erwartet, jedoch ein C-Satz gefunden
    DTA_FOUND_SET_C_NOT_EXTENSION = -98
    # Es wurde ein C-Datensatzerweiterung erwartet, jedoch ein E-Satz gefunden
    DTA_FOUND_SET_E_NOT_EXTENSION = -97
    # Die Anzahl Erweiterungen paßt nicht zur Blocklänge
    DTA_INVALID_EXTENSION_COUNT = -96
    # Ungültige Zeichen in numerischem Feld
    DTA_INVALID_NUM = -95
    # Ungültige Zeichen im Textfeld
    DTA_INVALID_CHARS = -94
    # Die Währung des DTA-Datensatzes ist nicht Euro
    DTA_CURRENCY_NOT_EURO = -93
    # In einem DTA-Datensatz wurde kein Betrag angegeben
    DTA_EMPTY_AMOUNT = -92
    # Ungültiger Textschlüssel in der DTA-Datei
    DTA_INVALID_TEXT_KEY = -91
    # Für ein (alphanumerisches) Feld wurde kein Wert angegeben
    DTA_EMPTY_STRING = -90
    # Die Startmarkierung des A-Datensatzes wurde nicht gefunden
    DTA_MARKER_A_NOT_FOUND = -89
    # Die Startmarkierung des C-Datensatzes wurde nicht gefunden
    DTA_MARKER_C_NOT_FOUND = -88
    # Die Startmarkierung des E-Datensatzes wurde nicht gefunden
    DTA_MARKER_E_NOT_FOUND = -87
    # Die Satzlänge eines C-Datensatzes muß zwischen 187 und 622 Byte betragen
    DTA_INVALID_SET_C_LEN = -86
    # Die Satzlänge eines A- bzw. E-Satzes muß 128 Byte betragen
    DTA_INVALID_SET_LEN = -85
    # als Währung in der DTA-Datei ist nicht Euro eingetragen
    DTA_WAERUNG_NOT_EURO = -84
    # das Ausführungsdatum ist zu früh oder zu spät (max. 15 Tage nach Dateierstellung)
    DTA_INVALID_ISSUE_DATE = -83
    # das Datum ist ungültig
    DTA_INVALID_DATE = -82
    # Formatfehler in der DTA-Datei
    DTA_FORMAT_ERROR = -81
    # die DTA-Datei enthält Fehler
    DTA_FILE_WITH_ERRORS = -80
    # ungültiger Suchbereich angegeben (unten>oben)
    INVALID_SEARCH_RANGE = -79
    # Die Suche lieferte kein Ergebnis
    KEY_NOT_FOUND = -78
    # BAV denkt, das Konto ist falsch (konto_check hält es für richtig)
    BAV_FALSE = -77
    # User-Blocks müssen einen Typ > 500 haben
    LUT2_NO_USER_BLOCK = -76
    # für ein LUT-Set sind nur die Werte 0, 1 oder 2 möglich
    INVALID_SET = -75
    # Ein Konto kann kann nur für deutsche Banken geprüft werden
    NO_GERMAN_BIC = -74
    # Der zu validierende strukturierete Verwendungszweck muß genau 20 Zeichen enthalten
    IPI_CHECK_INVALID_LENGTH = -73
    # Im strukturierten Verwendungszweck dürfen nur alphanumerische Zeichen vorkommen
    IPI_INVALID_CHARACTER = -72
    # Die Länge des IPI-Verwendungszwecks darf maximal 18 Byte sein
    IPI_INVALID_LENGTH = -71
    # Es wurde eine LUT-Datei im Format 1.0/1.1 geladen
    LUT1_FILE_USED = -70
    # Für die aufgerufene Funktion fehlt ein notwendiger Parameter
    MISSING_PARAMETER = -69
    # Die Funktion iban2bic() arbeitet nur mit deutschen Bankleitzahlen
    IBAN2BIC_ONLY_GERMAN = -68
    # Die Prüfziffer der IBAN stimmt, die der Kontonummer nicht
    IBAN_OK_KTO_NOT = -67
    # Die Prüfziffer der Kontonummer stimmt, die der IBAN nicht
    KTO_OK_IBAN_NOT = -66
    # Es sind nur maximal 500 Slots pro LUT-Datei möglich (Neukompilieren erforderlich)
    TOO_MANY_SLOTS = -65
    # Initialisierung fehlgeschlagen (init_wait geblockt)
    INIT_FATAL_ERROR = -64
    # Ein inkrementelles Initialisieren benötigt einen Info-Block in der LUT-Datei
    INCREMENTAL_INIT_NEEDS_INFO = -63
    # Ein inkrementelles Initialisieren mit einer anderen LUT-Datei ist nicht möglich
    INCREMENTAL_INIT_FROM_DIFFERENT_FILE = -62
    # Die Funktion ist nur in der Debug-Version vorhanden
    DEBUG_ONLY_FUNCTION = -61
    # Kein Datensatz der LUT-Datei ist aktuell gültig
    LUT2_INVALID = -60
    # Der Datensatz ist noch nicht gültig
    LUT2_NOT_YET_VALID = -59
    # Der Datensatz ist nicht mehr gültig
    LUT2_NO_LONGER_VALID = -58
    # Im Gültigkeitsdatum sind Anfangs- und Enddatum vertauscht
    LUT2_GUELTIGKEIT_SWAPPED = -57
    # Das angegebene Gültigkeitsdatum ist ungültig (Soll: JJJJMMTT-JJJJMMTT)
    LUT2_INVALID_GUELTIGKEIT = -56
    # Der Index für die Filiale ist ungültig
    LUT2_INDEX_OUT_OF_RANGE = -55
    # Die Bibliothek wird gerade neu initialisiert
    LUT2_INIT_IN_PROGRESS = -54
    # Das Feld BLZ wurde nicht initialisiert
    LUT2_BLZ_NOT_INITIALIZED = -53
    # Das Feld Filialen wurde nicht initialisiert
    LUT2_FILIALEN_NOT_INITIALIZED = -52
    # Das Feld Bankname wurde nicht initialisiert
    LUT2_NAME_NOT_INITIALIZED = -51
    # Das Feld PLZ wurde nicht initialisiert
    LUT2_PLZ_NOT_INITIALIZED = -50
    # Das Feld Ort wurde nicht initialisiert
    LUT2_ORT_NOT_INITIALIZED = -49
    # Das Feld Kurzname wurde nicht initialisiert
    LUT2_NAME_KURZ_NOT_INITIALIZED = -48
    # Das Feld PAN wurde nicht initialisiert
    LUT2_PAN_NOT_INITIALIZED = -47
    # Das Feld BIC wurde nicht initialisiert
    LUT2_BIC_NOT_INITIALIZED = -46
    # Das Feld Prüfziffer wurde nicht initialisiert
    LUT2_PZ_NOT_INITIALIZED = -45
    # Das Feld NR wurde nicht initialisiert
    LUT2_NR_NOT_INITIALIZED = -44
    # Das Feld Änderung wurde nicht initialisiert
    LUT2_AENDERUNG_NOT_INITIALIZED = -43
    # Das Feld Löschung wurde nicht initialisiert
    LUT2_LOESCHUNG_NOT_INITIALIZED = -42
    # Das Feld Nachfolge-BLZ wurde nicht initialisiert
    LUT2_NACHFOLGE_BLZ_NOT_INITIALIZED = -41
    # die Programmbibliothek wurde noch nicht initialisiert
    LUT2_NOT_INITIALIZED = -40
    # der Block mit der Filialenanzahl fehlt in der LUT-Datei
    LUT2_FILIALEN_MISSING = -39
    # es wurden nicht alle Blocks geladen
    LUT2_PARTIAL_OK = -38
    # Buffer error in den ZLIB Routinen
    LUT2_Z_BUF_ERROR = -37
    # Memory error in den ZLIB-Routinen
    LUT2_Z_MEM_ERROR = -36
    # Datenfehler im komprimierten LUT-Block
    LUT2_Z_DATA_ERROR = -35
    # Der Block ist nicht in der LUT-Datei enthalten
    LUT2_BLOCK_NOT_IN_FILE = -34
    # Fehler beim Dekomprimieren eines LUT-Blocks
    LUT2_DECOMPRESS_ERROR = -33
    # Fehler beim Komprimieren eines LUT-Blocks
    LUT2_COMPRESS_ERROR = -32
    # Die LUT-Datei ist korrumpiert
    LUT2_FILE_CORRUPTED = -31
    # Im Inhaltsverzeichnis der LUT-Datei ist kein Slot mehr frei
    LUT2_NO_SLOT_FREE = -30
    # Die (Unter)Methode ist nicht definiert
    UNDEFINED_SUBMETHOD = -29
    # Der benötigte Programmteil wurde beim Kompilieren deaktiviert
    EXCLUDED_AT_COMPILETIME = -28
    # Die Versionsnummer für die LUT-Datei ist ungültig
    INVALID_LUT_VERSION = -27
    # ungültiger Prüfparameter (erste zu prüfende Stelle)
    INVALID_PARAMETER_STELLE1 = -26
    # ungültiger Prüfparameter (Anzahl zu prüfender Stellen)
    INVALID_PARAMETER_COUNT = -25
    # ungültiger Prüfparameter (Position der Prüfziffer)
    INVALID_PARAMETER_PRUEFZIFFER = -24
    # ungültiger Prüfparameter (Wichtung)
    INVALID_PARAMETER_WICHTUNG = -23
    # ungültiger Prüfparameter (Rechenmethode)
    INVALID_PARAMETER_METHODE = -22
    # Problem beim Initialisieren der globalen Variablen
    LIBRARY_INIT_ERROR = -21
    # Prüfsummenfehler in der blz.lut Datei
    LUT_CRC_ERROR = -20
    # falsch (die BLZ wurde außerdem gelöscht)
    FALSE_GELOESCHT = -19
    # ok, ohne Prüfung (die BLZ wurde allerdings gelöscht)
    OK_NO_CHK_GELOESCHT = -18
    # ok (die BLZ wurde allerdings gelöscht)
    OK_GELOESCHT = -17
    # die Bankleitzahl wurde gelöscht
    BLZ_GELOESCHT = -16
    # Fehler in der blz.txt Datei (falsche Zeilenlänge)
    INVALID_BLZ_FILE = -15
    # undefinierte Funktion, die library wurde mit THREAD_SAFE=0 kompiliert
    LIBRARY_IS_NOT_THREAD_SAFE = -14
    # schwerer Fehler im Konto_check-Modul
    FATAL_ERROR = -13
    # ein Konto muß zwischen 1 und 10 Stellen haben
    INVALID_KTO_LENGTH = -12
    # kann Datei nicht schreiben
    FILE_WRITE_ERROR = -11
    # kann Datei nicht lesen
    FILE_READ_ERROR = -10
    # kann keinen Speicher allokieren
    ERROR_MALLOC = -9
    # die blz.txt Datei wurde nicht gefunden
    NO_BLZ_FILE = -8
    # die blz.lut Datei ist inkosistent/ungültig
    INVALID_LUT_FILE = -7
    # die blz.lut Datei wurde nicht gefunden
    NO_LUT_FILE = -6
    # die Bankleitzahl ist nicht achtstellig
    INVALID_BLZ_LENGTH = -5
    # die Bankleitzahl ist ungültig
    INVALID_BLZ = -4
    # das Konto ist ungültig
    INVALID_KTO = -3
    # die Methode wurde noch nicht implementiert
    NOT_IMPLEMENTED = -2
    # die Methode ist nicht definiert
    NOT_DEFINED = -1
    # falsch
    FALSE = 0
    # ok
    OK = 1
    # ok, ohne Prüfung
    OK_NO_CHK = 2
    # ok, für den Test wurde eine Test-BLZ verwendet
    OK_TEST_BLZ_USED = 3
    # Der Datensatz ist aktuell gültig
    LUT2_VALID = 4
    # Der Datensatz enthält kein Gültigkeitsdatum
    LUT2_NO_VALID_DATE = 5
    # Die Datei ist im alten LUT-Format (1.0/1.1)
    LUT1_SET_LOADED = 6
    # ok, es wurde allerdings eine LUT-Datei im alten Format (1.0/1.1) generiert
    LUT1_FILE_GENERATED = 7
    # In der DTAUS-Datei wurden kleinere Fehler gefunden
    DTA_FILE_WITH_WARNINGS = 8
    # ok, es wurde allerdings eine LUT-Datei im Format 2.0 generiert (Compilerswitch)
    LUT_V2_FILE_GENERATED = 9
    # ok, derWert für den Schlüssel wurde überschrieben
    KTO_CHECK_VALUE_REPLACED = 10
    # wahrscheinlich ok, die Kontonummer kann allerdings (nicht angegebene) Unterkonten enthalten
    OK_UNTERKONTO_POSSIBLE = 11
    # wahrscheinlich ok, die Kontonummer enthält eine Unterkontonummer
    OK_UNTERKONTO_GIVEN = 12
    # ok, die Anzahl Slots wurde auf SLOT_CNT_MIN (60) hochgesetzt
    OK_SLOT_CNT_MIN_USED = 13
    # ok, ein(ige) Schlüssel wurden nicht gefunden
    SOME_KEYS_NOT_FOUND = 14
    # Die Bankverbindung wurde nicht getestet
    LUT2_KTO_NOT_CHECKED = 15
    # Es wurden fast alle Blocks (außer den IBANRegeln) geladen
    LUT2_OK_WITHOUT_IBAN_RULES = 16
    # ok, für die BLZ wurde allerdings die Nachfolge-BLZ eingesetzt
    OK_NACHFOLGE_BLZ_USED = 17
    # ok, die Kontonummer wurde allerdings ersetzt
    OK_KTO_REPLACED = 18
    # ok, die Bankleitzahl wurde allerdings ersetzt
    OK_BLZ_REPLACED = 19
    # ok, die Bankleitzahl und Kontonummer wurde allerdings ersetzt
    OK_BLZ_KTO_REPLACED = 20
    # ok, die Bankverbindung ist (ohne Test) als richtig anzusehen
    OK_IBAN_WITHOUT_KC_TEST = 21
    # ok, für IBAN ist (durch eine Regel) allerdings ein anderer BIC definiert
    OK_INVALID_FOR_IBAN = 22
    # ok, für die BIC-Bestimmung der ehemaligen Hypo-Bank für IBAN wird i.A. zusätzlich die Kontonummer benötigt
    OK_HYPO_REQUIRES_KTO = 23
    # ok, die Kontonummer wurde ersetzt, die neue Kontonummer hat keine Prüfziffer
    OK_KTO_REPLACED_NO_PZ = 24
    # ok, es wurde ein (weggelassenes) Unterkonto angefügt
    OK_UNTERKONTO_ATTACHED = 25

    def __init__(self, code):
        message = self._error_codes.get(code, 'Unknown error (%s)' % code)
        Exception.__init__(self, message)
        self.code = code

KontoCheckError._error_codes = {}
for name, value in KontoCheckError.__dict__.items():
    if not name.startswith('_'):
        KontoCheckError._error_codes[value] = name
