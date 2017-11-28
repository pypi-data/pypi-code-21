"""Conversion routines"""


__all__ = [
"str2bool", "bool2str", "chunk_string", "ordinal_suffix", "seconds2str", "make_fits_keys_dict",
"valid_fits_key", "eval_fieldnames", "expr_to_fieldname", "module_to_dict", "unicode_to_greek",
"greek_to_unicode", "make_code_readable", "int_to_superscript"]


import math
import re


# TODO maybe a str2bool_ex() and its counterpart

def str2bool(s):
    """Understands "T"/"F" only (case-sensitive). To be used for file parsing.

    **Note** This routine is limited on purpose for speed.
    """
    if s == "T":
        return True
    elif s == "F":
        return False
    raise ValueError("I don't understand '{0!s}' as a logical value".format(s))


def bool2str(x):
    """Converts bool variable to either "T" or "F".

    **Note** This routine is limited on purpose for speed.
    """
    assert isinstance(x, bool)
    return "T" if x else "F"


def make_code_readable(s):
    """Adds newlines at strategic places"""

    MAP = {",": ",\n", "{": "{\n ", "}": "\n}"}

    ll = []

    state = "open"
    flag_single = False
    flag_double = False
    flag_backslash = False
    for ch in s:
        if flag_backslash:
            flag_backslash = False
            continue

        if ch == "\\":
            flag_backslash = True
            continue

        if flag_single:
            if ch == "'":
                flag_single = False
        elif not flag_double and ch == "'":
            flag_single = True

        if flag_double:
            if ch == '"':
                flag_double = False
        elif not flag_single and ch == '"':
            flag_double = True

        if flag_single or flag_double:
            ll.append(ch)
        else:
            ll.append(MAP.get(ch, ch))

    return "".join(ll)


def chunk_string(string, length):
    """
    Splits a string into fixed-length chunks.

    This function returns a generator, using a generator comprehension. The
    generator returns the string sliced, from 0 + a multiple of the length
    of the chunks, to the length of the chunks + a multiple of the length
    of the chunks.

    Reference: http://stackoverflow.com/questions/18854620
    """
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def ordinal_suffix(i):
    """Returns 'st', 'nd', or 'rd'."""
    return 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'


def seconds2str(seconds):
    """Returns string such as 1h 05m 55s."""

    if seconds < 0:
        return "{0:.3g}s".format(seconds)
    elif math.isnan(seconds):
        return "NaN"
    elif math.isinf(seconds):
        return "Inf"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h >= 1:
        return "{0:g}h {1:02g}m {2:.3g}s".format(h, m, s)
    elif m >= 1:
        return "{0:02g}m {1:.3g}s".format(m, s)
    else:
        return "{0:.3g}s".format(s)


def make_fits_keys_dict(keys):
    """
    Returns a dictionary to translate to unique FITS header keys up to 8 characters long

    This is similar to Windows making up 8-character names for filenames that
    are longer than this

    "The keyword names may be up to 8 characters long and can only contain
    uppercase letters A to Z, the digits 0 to 9, the hyphen, and the underscore
    character." [1]

    Arguments:
        keys -- list of strings

    Returns:
        dictionary whose keys are the elements in the "keys" argument, and whose
        values are made-up uppercase names

    References:
        [1] http://fits.gsfc.nasa.gov/fits_primer.html
    """

    key_dict = {}
    new_keys = []
    for key in keys:
        # converts to valid FITS key according to reference [1] above
        fits_key = valid_fits_key(key)
        num_digits = 1
        i = -1
        i_max = 9
        while fits_key in new_keys:
            i += 1
            if i > i_max:
                i = 0
                i_max = i_max * 10 + 9
                num_digits += 1
            fits_key = fits_key[:(8 - num_digits)] + (("%0{0:d}d".format(num_digits)) % i)

        key_dict[key] = fits_key
        new_keys.append(fits_key)

    return key_dict


def valid_fits_key(key):
    """
    Makes valid key for a FITS header

    "The keyword names may be up to 8 characters long and can only contain
    uppercase letters A to Z, the digits 0 to 9, the hyphen, and the underscore
    character." (http://fits.gsfc.nasa.gov/fits_primer.html)
    """

    ret = re.sub("[^A-Z0-9\-_]", "", key.upper())[:8]
    if len(ret) == 0:
        raise RuntimeError("key '{0!s}' has no valid characters to be a key in a FITS header".format(key))
    return ret


def eval_fieldnames(string_, varname="fieldnames"):
    """Evaluates string_, must evaluate to list of strings. Also converts field names to uppercase"""
    ff = eval(string_)
    if not isinstance(ff, list):
        raise RuntimeError("{0!s} must be a list".format(varname))
    if not all([isinstance(x, str) for x in ff]):
        raise RuntimeError("{0!s} must be a list of strings".format(varname))
    ff = [x.upper() for x in ff]
    return ff


def expr_to_fieldname(expr):
    """Keeps the rightmost part of the class name after the "_" """
    return expr[:expr.index("(")].strip().split("_")[-1]


def module_to_dict(module):
    """Creates a dictionary whose keys are module.__all__

    Returns: {"(attribute name)": attribute, ...}
    """

    lot = [(key, module.__getattribute__(key)) for key in module.__all__]
    ret = dict(lot)
    return ret



# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Greek alphabet-related routines

# Source:
#     "A Python dictionary mapping the Unicode codes of the greek alphabet to their names"
#     https://gist.github.com/beniwohli/765262
#
_UNICODE_GREEK = (
('\u0391', 'Alpha'),
('\u0392', 'Beta'),
('\u0393', 'Gamma'),
('\u0394', 'Delta'),
('\u0395', 'Epsilon'),
('\u0396', 'Zeta'),
('\u0397', 'Eta'),
('\u0398', 'Theta'),
('\u0399', 'Iota'),
('\u039A', 'Kappa'),
('\u039B', 'Lamda'),
('\u039C', 'Mu'),
('\u039D', 'Nu'),
('\u039E', 'Xi'),
('\u039F', 'Omicron'),
('\u03A0', 'Pi'),
('\u03A1', 'Rho'),
('\u03A3', 'Sigma'),
('\u03A4', 'Tau'),
('\u03A5', 'Upsilon'),
('\u03A6', 'Phi'),
('\u03A7', 'Chi'),
('\u03A8', 'Psi'),
('\u03A9', 'Omega'),
('\u03B1', 'alpha'),
('\u03B2', 'beta'),
('\u03B3', 'gamma'),
('\u03B4', 'delta'),
('\u03B5', 'epsilon'),
('\u03B6', 'zeta'),
('\u03B7', 'eta'),
('\u03B8', 'theta'),
('\u03B9', 'iota'),
('\u03BA', 'kappa'),
('\u03BB', 'lamda'),
('\u03BC', 'mu'),
('\u03BD', 'nu'),
('\u03BE', 'xi'),
('\u03BF', 'omicron'),
('\u03C0', 'pi'),
('\u03C1', 'rho'),
('\u03C3', 'sigma'),
('\u03C4', 'tau'),
('\u03C5', 'upsilon'),
('\u03C6', 'phi'),
('\u03C7', 'chi'),
('\u03C8', 'psi'),
('\u03C9', 'omega'),
)

_UNICODE_TO_GREEK = dict(_UNICODE_GREEK)
_GREEK_TO_UNICODE = dict([(x[1], x[0]) for x in _UNICODE_GREEK])

def unicode_to_greek(s):
    """Converts unicode single code, e.g., '\u03A3' to Greek letter name, e.g. 'Sigma'"""

    # "?" is the "zero-element"
    if s == "?":
        return s

    return _UNICODE_TO_GREEK[s]

def greek_to_unicode(s):
    """Converts Greek letter name, e.g., 'Sigma', to unicode character, e.g. '\u03A3' """

    # "?" is the "zero-element"
    if s == "?":
        return s

    return _GREEK_TO_UNICODE[s]



# superscript numbers
_INT_TO_SUPERSCRIPT = {
 0: "\u2070",
 1: "\u2071",
 2: "\u00b2",
 3: "\u00b3",
 4: "\u2074",
 5: "\u2075",
 6: "\u2076",
 7: "\u2077",
 8: "\u2078",
 9: "\u2079",
}

def int_to_superscript(i):
    """int_to_superscript(i) --> str"""

    return "".join((_INT_TO_SUPERSCRIPT[int(ch)] for ch in str(i)))










