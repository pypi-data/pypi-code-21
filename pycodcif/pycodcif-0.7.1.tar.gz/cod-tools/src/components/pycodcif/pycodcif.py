# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.10
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_pycodcif')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_pycodcif')
    _pycodcif = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_pycodcif', [dirname(__file__)])
        except ImportError:
            import _pycodcif
            return _pycodcif
        if fp is not None:
            try:
                _mod = imp.load_module('_pycodcif', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _pycodcif = swig_import_helper()
    del swig_import_helper
else:
    import _pycodcif
del _swig_python_version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0


import warnings
warnings.filterwarnings('ignore', category=UnicodeWarning)

def parse(filename,*args):
    import re

    prog = '-'
    try:
        import sys
        prog = sys.argv[0]
    except IndexError:
        pass

    options = {}
    if len(args) > 0:
        options = args[0]

    parse_results = parse_cif(filename,prog,options)
    data = parse_results['datablocks']
    messages = parse_results['messages']
    nerrors = parse_results['nerrors']

    for datablock in data:
        datablock['precisions'] = {}
        for tag in datablock['types'].keys():
            precisions, _ = extract_precision(datablock['values'][tag],
                                              datablock['types'][tag])
            if precisions is not None:
                datablock['precisions'][tag] = precisions
        for saveblock in datablock['save_blocks']:
            saveblock['precisions'] = {}
            for tag in saveblock['types'].keys():
                precisions, _ = extract_precision(saveblock['values'][tag],
                                                  saveblock['types'][tag])
                if precisions is not None:
                    saveblock['precisions'][tag] = precisions

    data = [ decode_utf8_frame( _ ) for _ in data ]

    errors = []
    warnings = []

    for message in messages:
        datablock = message['addpos']
        if datablock is not None:
            datablock = "data_{0}".format(datablock)
        explanation = message['explanation']
        if explanation is not None:
            explanation = explanation[0].lower() + explanation[1:]
        lineno = None
        if 'lineno' in message:
            lineno = message['lineno']
        columnno = None
        if 'columnno' in message:
            columnno = message['columnno']
        msg = sprint_message(message['program'],
                             message['filename'],
                             datablock,
                             message['status'],
                             message['message'],
                             explanation,
                             lineno,
                             columnno,
                             message['line'])

        if message['status'] == 'ERROR':
            errors.append(msg)
        else:
            warnings.append(msg)

    if 'no_print' not in options.keys() or options['no_print'] == 0:
        for warning in warnings:
            sys.stdout.write(warning)
        for error in errors:
            sys.stdout.write(error)
        if errors:
            sys.exit(1) # Different way to exit

    return data, nerrors, [warnings + errors]

def unpack_precision(value,precision):
    """
    Adapted from:

    URL: svn://www.crystallography.net/cod-tools/branches/andrius-inline-to-swig/src/lib/perl5/Precision.pm
    Relative URL: ^/branches/andrius-inline-to-swig/src/lib/perl5/Precision.pm
    Repository Root: svn://www.crystallography.net/cod-tools
    Repository UUID: 04be6746-3802-0410-999d-98508da1e98c
    Revision: 3228
    """
    import re
    match = re.search('([-+]?[0-9]*)?(\.)?([0-9]+)?(?:e([+-]?[0-9]+))?',
                      value)

    int_part = 0
    if match.group(1):
        if match.group(1) == '+':
            int_part = 1
        elif match.group(1) == '-':
            int_part = -1
        else:
            int_part = int(match.group(1))
    dec_dot = match.group(2)
    mantissa = match.group(3)
    exponent = 0
    if match.group(4):
        exponent = int(match.group(4))
    if dec_dot and mantissa:
        precision = float(precision) / (10**len(mantissa))
    precision = float(precision) * (10**exponent)
    return precision

def extract_precision(values,types):
    import re
    if isinstance(types,list):
        precisions = []
        important = []
        for i in range(0,len(values)):
            precision, is_important = \
                extract_precision(values[i],types[i])
            precisions.append(precision)
            important.append(is_important)
        if any([x == 1 for x in important]):
            return precisions, 1
        else:
            return None, 0
    elif isinstance(types,dict):
        precisions = {}
        for i in values.keys():
            precision, is_important = \
                extract_precision(values[i],types[i])
            if is_important:
                precisions[i] = precision
        if precisions.keys():
            return precisions, 1
        else:
            return None, 0
    elif types == 'FLOAT':
        match = re.search('^(.*)(\(([0-9]+)\))$',values)
        if match is not None and match.group(1):
            return unpack_precision(match.group(1),match.group(3)), 1
        else:
            return None, 1
    elif types == 'INT':
        match = re.search('^(.*)(\(([0-9]+)\))$',values)
        if match is not None and match.group(1):
            return match.group(3), 1
        else:
            return None, 1
    else:
        return None, 0

def decode_utf8_frame(frame):
    for _ in [ 'name', 'tags', 'loops' ]:
        if _ in frame.keys():
            frame[_] = decode_utf8_values(frame[_])

    for _ in [ 'precisions', 'inloop', 'values', 'types' ]:
        if _ in frame.keys():
            frame[_] = decode_utf8_hash_keys(frame[_])

    if 'values' in frame.keys() and 'types' in frame.keys():
        frame['values'] = decode_utf8_typed_values(frame['values'],
                                                   frame['types'])

    if 'save_blocks' in frame.keys():
        frame['save_blocks'] = [ decode_utf8_frame(_) for _ in
                                        frame['save_blocks'] ]

    return frame

def decode_utf8_hash_keys(values):
    if isinstance(values,list):
        for i in range(0,len(values)):
            values[i] = decode_utf8_hash_keys(values[i])
    elif isinstance(values,dict):
        for key in values.keys():
            values[key] = decode_utf8_hash_keys(values[key])
            new_key = decode_utf8_values(key)
            if new_key != key:
                values[new_key] = values[key]
                del values[key]

    return values

def decode_utf8_values(values):
    if isinstance(values,list):
        for i in range(0,len(values)):
            values[i] = decode_utf8_values(values[i])
    elif isinstance(values,dict):
        for key in values.keys():
            values[key] = decode_utf8_hash_keys(values[key])
    else:
        values = values.decode('utf-8','replace')

    return values

def decode_utf8_typed_values(values,types):
    if isinstance(values,list):
        for i in range(0,len(values)):
            values[i] = decode_utf8_typed_values(values[i], types[i])
    elif isinstance(values,dict):
        for key in values.keys():
            values[key] = decode_utf8_typed_values(values[key], types[key])
    elif types not in [ 'INT', 'FLOAT' ]:
        values = decode_utf8_values(values)

    return values

program_escape = {
    '&': '&amp;',
    ':': '&colon;',
}
filename_escape = {
    '&': '&amp;',
    ':': '&colon;',
    ' ': '&nbsp;',
    '(': '&lpar;',
    ')': '&rpar;',
}
datablock_escape = {
    '&': '&amp;',
    ':': '&colon;',
    ' ': '&nbsp;',
}
message_escape = {
    '&': '&amp;',
    ':': '&colon;'
}

def sprint_message(program, filename, datablock, errlevel, message,
                   explanation, line, column, line_contents):
    """
    Adapted from:
    URL: svn://www.crystallography.net/cod-tools/trunk/src/lib/perl5/COD/UserMessage.pm
    Relative URL: ^/trunk/src/lib/perl5/COD/UserMessage.pm
    Repository Root: svn://www.crystallography.net/cod-tools
    Repository UUID: 04be6746-3802-0410-999d-98508da1e98c
    Revision: 3813
    """
    import re
    message = re.sub('\.?\n?$', '', message)
    if explanation is not None:
        explanation = re.sub('\.?\n?$', '', explanation)
    if line_contents is not None:
        line_contents = re.sub('\n+$', '', line_contents)

    if program == '-c':
        program = "python -c '...'"

    program     = escape_meta(program,     program_escape)
    filename    = escape_meta(filename,    filename_escape)
    datablock   = escape_meta(datablock,   datablock_escape)
    message     = escape_meta(message,     message_escape)
    explanation = escape_meta(explanation, message_escape)

    if line_contents is not None:
        line_contents = '\n'.join([ " {0}".format(x) for x in line_contents.split('\n') ])

    msg = "{0}: ".format(program)
    if filename is not None:
        msg = "{0}{1}".format(msg, filename)
        if line is not None:
            msg = "{0}({1}".format(msg, line)
            if column is not None:
                msg = "{0},{1}".format(msg, column)
            msg = "{0})".format(msg)
        if datablock is not None:
            msg = "{0} {1}".format(msg, datablock)
        msg = "{0}: ".format(msg)
    if errlevel is not None:
        msg = "{0}{1}, ".format(msg, errlevel)
    msg = "{0}{1}".format(msg, message)
    if explanation is not None:
        msg = "{0} -- {1}".format(msg, explanation)
    if line_contents is not None:
        msg = "{0}:\n{1}\n".format(msg, line_contents)
        if column is not None:
            msg = "{0} {1}^\n".format(msg, " "*(column-1))
    else:
        msg = "{0}.\n".format(msg)

    return msg

def escape_meta(text, escaped_symbols):
    """
    Adapted from:
    URL: svn://www.crystallography.net/cod-tools/trunk/src/lib/perl5/COD/UserMessage.pm
    Relative URL: ^/trunk/src/lib/perl5/COD/UserMessage.pm
    Repository Root: svn://www.crystallography.net/cod-tools
    Repository UUID: 04be6746-3802-0410-999d-98508da1e98c
    Revision: 3813
    """
    import re

    if text is None:
        return None

    symbols = "|".join(["\\{0}".format(x) for x in escaped_symbols.keys()])

    def escape_internal(matchobj):
        return escaped_symbols(matchobj.group(0))

    return re.sub("({0})".format(symbols), escape_internal, text)



def parse_cif(fname, prog, options):
    return _pycodcif.parse_cif(fname, prog, options)
parse_cif = _pycodcif.parse_cif
# This file is compatible with both classic and new-style classes.


