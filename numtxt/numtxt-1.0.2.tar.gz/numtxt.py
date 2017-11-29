# numtxt - gives full and approximate written forms of numbers
# Copyright (C) 2017  Electrostatus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import log

# prefixes, suffixes and other words -----------------------
_noll_prefixes = {0: '',  # noll prefix definitions
  1: 'un',       10: 'dec',        100: 'cen',
  2: 'duo',      20: 'vigin',      200: 'duocen',
  3: 'tre',      30: 'trigin',     300: 'trecen',
  4: 'quattuor', 40: 'quadragin',  400: 'quadringen',
  5: 'quin',     50: 'quinquagin', 500: 'quingen',
  6: 'sex',      60: 'sexagin',    600: 'sescen',
  7: 'septen',   70: 'septuagin',  700: 'septingen',
  8: 'octo',     80: 'octogin',    800: 'octingen',
  9: 'novem',    90: 'nonagin',    900: 'nongen',}

_conway_prefixes = {0: ('', ''),  # conway-wechsler prefix definitions
  1: ('un', ''),       10: ('deci', 'n'),          100: ('centi', 'nx'),
  2: ('duo', ''),      20: ('viginti', 'ms'),      200: ('ducenti', 'n'),
  3: ('tre', 'sx'),    30: ('triginta', 'ns'),     300: ('trecenti', 'ns'),
  4: ('quattuor', ''), 40: ('quadraginta', 'ns'),  400: ('quadringenti', 'ns'),
  5: ('quin', ''),     50: ('quinquaginta', 'ns'), 500: ('quingenti', 'ns'),
  6: ('se', 'sx'),     60: ('sexaginta', 'n'),     600: ('sescenti', 'n'),
  7: ('septe', 'mn'),  70: ('septuaginta', 'n'),   700: ('septingenti', 'n'),
  8: ('octo', ''),     80: ('octoginta', 'mx'),    800: ('octingenti', 'mx'),
  9: ('nove', 'mn'),   90: ('nonaginta', ''),      900: ('nongenti', ''),}

# prefixes for noll and conway below 1000^10
_unts = ('n', 'm', 'b', 'tr', 'quadr', 'quint', 'sext', 'sept', 'oct', 'non')

_rowlett_prefixes = {0: '',  # rowlett prefix definitions (best guess)
  1: 'hen',   10: 'deka',       100: 'hecato',  # these prefixes should be
  2: 'do',    20: 'icosi',      200: 'diacosioi',  # checked
  3: 'tri',   30: 'triaconta',  300: 'triacosioi',
  4: 'tetra', 40: 'tetraconta', 400: 'tetracosioi',
  5: 'penta', 50: 'pentaconta', 500: 'pentacosioi',
  6: 'hexa',  60: 'hexaconta',  600: 'hexacosioi',
  7: 'hepta', 70: 'heptaconta', 700: 'heptacosioi',
  8: 'okta',  80: 'octaconta',  800: 'octacosioi',
  9: 'ennea', 90: 'enneaconta', 900: 'enneacosioi',}

_suffixes = {'noll': ('illion', 'tillion', 'illard', 'tillard'),
             'conway-wechsler': ('illion', 'illard'),
             'rowlett': ('illion',), 'knuth': ('yllion',)}

# 0-99 names - used in _tens function
_tn_ones =  ('', 'one', 'two', 'three', 'four', 'five', 'six',
            'seven', 'eight', 'nine')
_tn_tees = {10: 'ten', 11: 'eleven', 12: 'twelve',
           13: 'thir', 15: 'fif', 18: 'eigh'}
_tn_tens =  {2: 'twen', 3: 'thir', 5: 'fif', 8: 'eigh'}
_tn_teesuf, _tn_tensuf= 'teen', 'ty'

# ordinals - used in ordinal function
_sh_ords = {0: 'th', 1: 'st', 2: 'nd', 3: 'rd'}
_lg_ords = {1: 'first', 2: 'second', 3: 'third', 5: 'fifth',
            8: 'eighth', 9: 'ninth', 12: 'twelfth', }

# other names - used in multiple functions
_zero, _hun, _thous = 'zero', 'hundred', 'thousand'
_neg = 'negative'#'minus'
# not every word is defined here, some are in the functions that use them

# quick lookup tables --------------------------------------
_qk_tens = {}; _qk_noll = {}  # these are populated as needed
_qk_conw = {}; _qk_rowt = {}
_max_table_size = 2500  # don't let the quick lookup tables get too large

# methods and rules ----------------------------------------
methods = ('conway-wechsler', 'noll', 'rowlett', 'knuth')
current_method = methods[0]

suffix_styles = ('short', 'long', 'british')
current_style = suffix_styles[0]
_short_suf = True  # True for short style suffix, False for long style
_sub_long_suf = False  # True for old British style (_short_suf must be False)

# other ----------------------------------------------------
refs = ('References and related',
        '\'The Mathematical Gardner\' published 1981, pg 310-325',
        '\'The Book of Numbers\' published 1996, pg 15-16',
        'http://www.isthe.com/chongo/tech/math/number/number.html',
        'http://www.unc.edu/~rowlett/units/large.html',
        'http://www.mrob.com/pub/math/largenum.html#conway-wechsler',
        'http://www.mrob.com/pub/math/largenum-2.html#yllion',
        'https://en.wikipedia.org/wiki/Numeral_prefix',
        'https://en.wikipedia.org/wiki/Names_of_large_numbers',
        'https://en.wikipedia.org/wiki/Ordinal_number_%28linguistics%29',
        )

__doc__ = """
number naming module
gives full and approximate written forms of numbers

There are currently four methods for naming numbers which can be set
 by setMethod. see 'methods' for a list of available methods to use.

 Default is 'conway-wechsler'.

Additionally, there are three styles for suffixes which can be set
 by setStyle. See 'suffix_styles' for a list of available styles.
 Note that not all naming methods adhere to these styles as some
 were made to remove the confusion the different styles can cause.

 Default is 'short'.
"""

__all__= ['approx', 'name', 'ordinal', 'setMethod', 'setStyle',
          'methods', 'current_method', 'suffix_styles', 'current_style',]

# supporting functions and naming systems ------------------
def _noll(n):
    "noll naming system\nreturns name of 1000^n"
    # http://www.isthe.com/chongo/tech/math/number/number.html
    # published 1994? (earliest date on website)
    if not n: return ''
    if n == 1: return _thous
    card = int(abs(n)) - 1  # cardinal is always one less

    prfs, unts = _noll_prefixes, _unts  # prefixes

    # suffix handling
    if current_method == 'knuth':  # knuth's method can be dependent on
        th, sfx = '', _suffixes['knuth'][0]  # noll's (default: conway's)
    else:
        sufs = _suffixes['noll']
        th, suf1, suf2 = '', sufs[0], sufs[1]
        if not _short_suf:  # long style
            if card % 2 or _sub_long_suf: pass
            else: suf1, suf2 = sufs[2], sufs[3]
            if _sub_long_suf and not card % 2 and card > 1:
                th = _thous + ' '  # old British style
            card = card // 2 + card % 2
        sfx = suf1 if 20 > (card % 100) > 9 or card < 11 else suf2

    name, mil = '', 0  # prefix construction
    if card < 10: return th + unts[card] + sfx
    while card:
        card, r = divmod(card, 1000)
        one, ten, hun = r % 10, ((r % 100) // 10) * 10, (r // 100) * 100
        sect = prfs[hun] + prfs[one] + prfs[ten]
        name = sect + ('milli' * mil if r else '') + name
        mil += 1

    un = prfs[1]  # name does not start with this when above 1000^1000
    if mil > 1 and name.startswith(un): name = name.replace(un, '', 1)
    return th + name + sfx

def _conway(n):
    "conway-wechsler naming system\nreturns name of 1000^n"
    # http://www.mrob.com/pub/math/largenum.html#conway-wechsler
    # published 1996, pg 15-16 in 'The Book of Numbers'
    if not n: return ''
    if n == 1: return _thous
    card = int(abs(n)) - 1  # cardinal is always one less
    prfs, unts = _conway_prefixes, _unts  # prefixes

    # suffix handling
    if current_method == 'knuth':
        th, suf = '', _suffixes['knuth'][0]
    else:
        sufs = _suffixes['conway-wechsler']
        th, suf = '', sufs[0]
        if not _short_suf:  # suffix handling
            if card % 2 or _sub_long_suf: pass
            else: suf = sufs[1]
            if _sub_long_suf and not card % 2 and card > 1:
                th = _thous + ' '
            card = card // 2 + card % 2

    name = ''  # prefix construction
    while card:
        card, r = divmod(card, 1000)
        if r < 10: sect = unts[r]
        else:
            one, ten, hun = r % 10, ((r % 100) // 10) * 10, (r // 100) * 100
            ost, tst, hst = prfs[one], prfs[ten], prfs[hun]

            # check for matching joining letter (1 and 10 or 1 and 100 only)
            if one and ten: let = set(ost[1]) & set(tst[1])
            elif one and hun: let = set(ost[1]) & set(hst[1])
            else: let = set()

            ter = let.pop() if let else ''
            if one == 3 and ter: ter = 's'  # special case rule for 3
            sect = ost[0] + ter + tst[0] + hst[0]

        if sect[-1] in 'aeiou': sect = sect[:-1]  # strip last vowel
        name = sect + 'illi' + name if name else sect + name
    return th + name + suf

def _rowlett(n):
    "rowlett naming system\nreturns name of 1000^n"
    # http://www.unc.edu/~rowlett/units/large.html - published 2001
    n = int(abs(n))

    # this method does not have short/long style suffixes
    suf, prfs = _suffixes['rowlett'][0], _rowlett_prefixes
    if n < 4: return ('', _thous, 'm' + suf, 'g' + suf)[n]  # special cases

    if n > 999:
        v = ValueError('input is too large')
        raise v  # rowlett did not give details for going above 1000^999

    mil, name = 0, ''  # prefix construction
    while n:
        n, r = divmod(n, 1000)

        one, ten, hun = r % 10, ((r % 100) // 10) * 10, (r // 100) * 100
        if r < 20: sect = prfs[one] + prfs[ten]  # guessing
        else: sect = prfs[ten] + prfs[one]

        sect = prfs[hun] + sect

        # my extension to this system (otherwise would stop at 1000^999)
        name = sect + ('chilia' * mil if r else '') + name
        mil += 1

    un = prfs[1]  # name does not start with this when above 1000^1000
    if mil > 1 and name.startswith(un): name = name.replace(un, '', 1)
    return name.rstrip('aeiou') + suf  # strip ending vowels (guessing)

def _knuth(n, condensed=False, lvl=0, comma=False, is_log=False):
    "knuth naming system"
    #last three variables are not for user use!
    # lvl - tracker for recursion level, used by self
    # is_log - flag for if n is the power of 1e4, 10000^n; used in approx func
    # comma - when to add a comma to the name, used by self
    # http://www.mrob.com/pub/math/largenum-2.html#yllion
    # published 1981, pg 310-325 in 'The Mathematical Gardner'
    if not n: return ''
    if n < 10000 and not is_log:
        if condensed:
            return str(n)
        else:
            a = _tens(n // 100) if n // 100 else ''
            b = _tens(n % 100) if n % 100 else ''
            if a: a += (' ' + _hun) + (' ' if b else '')
            return a + b

    if is_log:
        p = int(log(n, 2))
        base = 2 ** p
    else:  # p is also the deepest the recursion can go
        p = int(log(log(n, 10000), 2))
        base = 10000 ** (2 ** p)
    d, r = divmod(n, base)

    # if called directly but method was not set to knuth
    prior_setting = None
    if not lvl and setMethod() != 'knuth':
        prior_setting = setMethod()
        setMethod('knuth')

    # knuth's method can use either noll's or conway's
    # but should use conway's as that follows
    # Roman syntax more closely than noll's
    if p: pfx = _conway(p+1)#_noll(p+1)
    else: pfx = 'myriad'
    if not is_log: pfx += (', ' if not comma else ' ')

    recur = _knuth
    if is_log:
        if n == 1: return pfx
        frnt = recur(r, 0, lvl+1, 0, is_log)
        back = ''
    else:
        frnt = recur(d, condensed, lvl+1, comma+1)
        back = recur(r, condensed, lvl+1, comma)

    name = filter(None, (frnt, ' ' + pfx, back))
    if not lvl and prior_setting: setMethod(prior_setting)
    return ''.join(name).strip(', ')

def _tens(n):
    "converts 0 to 99 to their names"
    name, n = '', abs(n) % 100
    if not n: return _zero
    elif n < 10: return _tn_ones[n]
    elif 9 < n < 20:
        if n in [13, 15, 18]: return _tn_tees[n] + _tn_teesuf
        elif n > 13: return _tn_ones[n-10] + _tn_teesuf
        else: return _tn_tees[n]
    else:
        if n // 10 in [2, 3, 5, 8]: name = _tn_tens[n // 10] + _tn_tensuf
        else: name =_tn_ones[n // 10] + _tn_tensuf
        if not n % 10: return name
        else: return name + '-' + _tn_ones[n % 10]

# main functions -------------------------------------------
def approx(n):
    """approximates n
    if n is a string, returns the name of 1000^n instead*

    *returns name of 10000^n if naming method is knuth
    """
    sgn, mthd = '', current_method
    base = 10000 if mthd == 'knuth' else 1000  # in order to be correct

    # parse input
    if type(n).__name__ in ('str', 'unicode'):  # power of 1000
        n = n.replace(',', '.')
        if '-' in n:  # negative power, return with ordinal
            n = n.replace('-', '')
            return approx(n) + _sh_ords[0]
        if '.' in n:  # floating power
            c, a = n.split('.')
            pwr = int(c)
            apx = base ** float('0.' + a)
        else:  # whole power
            pwr = int(n)
            apx = 1
    elif not n or abs(n) < base:  # small value
        return str(int(round(n)))
    else:  # ints, floats, longs
        if n < 0: sgn, n = '-', abs(n)
        lgg = round(log(n, base), 9)
        pwr = int(lgg)
        apx = base ** (lgg - pwr)

    # select method and use
    apx_fmt = '{:0.3f} '#'{: 7.3f} '
    if mthd == 'noll':
        try:
            nme = _qk_noll[pwr]  # lookup table
        except KeyError:
            nme = _noll(pwr)  # fallback
            if len(_qk_noll) < _max_table_size:
                _qk_noll[pwr] = nme  # store for next time

    elif mthd in ('conway', 'conway-wechsler'):
        try:
            nme = _qk_conw[pwr]
        except KeyError:
            nme = _conway(pwr)
            if len(_qk_conw) < _max_table_size:
                _qk_conw[pwr] = nme

    elif mthd == 'rowlett':
        try:
            nme = _qk_rowt[pwr]
        except KeyError:
            nme = _rowlett(pwr)
            if len(_qk_rowt) < _max_table_size:
                _qk_rowt[pwr] = nme

    elif mthd == 'knuth':
        nme = _knuth(pwr, is_log=True)
        apx_fmt = '{:0.4f} '

    else:  # any undefined method defaults to conway
        nme = _conway(pwr)

    return sgn + apx_fmt.format(apx) + nme

def name(n, condensed=False):
    """returns the cardinal name of n
    12000000 -> 'twelve million' (condensed=False)
    12000000 -> '12 million' (condensed=True)
    """
    if not n: return _zero
    sgn = '' if n > 0 else ('- ' if condensed else _neg + ' ')
    n, nam, pwr = abs(int(n)), '', 0
    mthd = current_method

    # select method
    if mthd == 'noll':
        func = _noll
        tabl = _qk_noll
    elif mthd in ('conway', 'conway-wechsler'):
        func = _conway
        tabl = _qk_conw
    elif mthd == 'rowlett':
        func = _rowlett
        tabl = _qk_rowt
    elif mthd == 'knuth':  # this method's build is in the func, so return it
        return sgn + _knuth(n, condensed).strip(' ,')
    else: func = _conway  # any undefined method defaults to conway

    while n:  # build name
        n, r = divmod(n, 1000)

        # don't have 'zero -illion' names
        if not r and pwr:
            pwr += 1
            continue

        # section name
        if condensed:
            sect = str(r) + ' ' if r else ''
        else:
            t, h = r // 100, r % 100
            try:  # lookup table
                tn = _qk_tens[t]
                hu = _qk_tens[h]
            except KeyError:  # fallback
                tn = _tens(t)
                hu = _tens(h)
                _qk_tens[t] = tn  # store for next time
                _qk_tens[h] = hu

            hun = (tn + ' ' + _hun + ' ') if t else ''
            ten = (hu + ' ') if h else ''
            sect = hun + ten

        # power name
        try:
            tho = tabl[pwr]
        except KeyError:
            tho = func(pwr)
            if len(tabl) < _max_table_size:
                tabl[pwr] = tho  # store for later use

        nam = sect + tho + ', ' + nam
        pwr += 1

    return (sgn + nam).strip(' ,')

def ordinal(n, short=False):
    """returns the ordinal name of n
    3 -> 'third' (short=False)
    3 -> '3rd' (short=True)
    """
    so, lo = _sh_ords, _lg_ords
    if short:
        th = so[0] if 9 < abs(n) % 100 < 14 else so.get(abs(n) % 10, so[0])
        nme = str(n) + th
    else:
        nme, lst = name(n), abs(n) % 100

        if lst > 19 and lst % 10: lst %= 10

        if lst in lo:  # special cases
            nme = nme.rsplit(name(lst), 1)[0]
            nme += lo[lst]
        elif not lst % 10 and lst > 19:  # 20, 30, 40, ...
            nme = nme.replace('y', 'ieth')
        else: nme += so[0]
    return nme

# settings functions ---------------------------------------
def setMethod(method=None):
    """sets the naming method
    pass None to see current method
    """
    global current_method, methods
    mthds = methods + ('conway', )  # shortened form for conway-wechsler

    if str(method).lower() not in mthds and method != None:
        v = TypeError('invalid method')
        raise v

    if method != None: current_method = method.lower()
    return current_method

def setStyle(style=None):
    """sets the suffix style
    pass None to see current style

    'short' -> million, billion, trillion, quadrillion...
    'long' -> million, milliard, billion, billiard...
    'british' -> million, thousand million, billion, thousand billion...
    """
    global _short_suf, _sub_long_suf, suffix_styles, _cur_suf_style
    global _qk_noll, _qk_conw  # these change based on the style

    if str(style).lower() not in suffix_styles and style != None:
        v = TypeError('invalid style')
        raise v

    if style is None:
        return _cur_suf_style
    elif style.lower() == 'short':
        _short_suf = True
        _sub_long_suf = False
    elif style.lower() == 'long':
        _short_suf = False
        _sub_long_suf = False
    elif style.lower() == 'british':
        _short_suf = False
        _sub_long_suf = True

    _qk_noll = {}; _qk_conw = {}  # must be cleared to match new style
    _cur_suf_style = style.lower()
    return _cur_suf_style
