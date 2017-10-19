"""Compile ASN.1 specifications to Python objects that can be used to
encode and decode types.

"""

from .parser import parse_files, parse_string, convert_type_tokens
from .codecs import ber
from .codecs import der
from .codecs import jer
from .codecs import per
from .codecs import uper
from .codecs import xer
from .errors import CompileError


class Specification(object):
    """This class is used to encode and decode ASN.1 types found in an
    ASN.1 specification.

    Instances of this class are created by the factory functions
    :func:`~asn1tools.compile_files()`,
    :func:`~asn1tools.compile_string()` and
    :func:`~asn1tools.compile_dict()`.

    """

    def __init__(self, modules):
        self._modules = modules
        self._types = {}

        try:
            for module_name in modules:
                types = modules[module_name]

                for type_name in types:
                    if type_name in self._types:
                        raise CompileError()

                    self._types[type_name] = types[type_name]

        except CompileError:
            self._types = None

    @property
    def types(self):
        """A dictionary of all types in the specification, or ``None`` if a
        type name was found in two or more modules.

        """

        return self._types

    @property
    def modules(self):
        """A dictionary of all modules in the specification.

        """

        return self._modules

    def encode(self, name, data):
        """Encode given dictionary `data` as given type `name` and return the
        encoded data as a bytes object.

        See `Types`_ for a mapping table from ASN.1 types to Python
        types.

        >>> foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
        b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?'

        """

        return self._types[name].encode(data)

    def decode(self, name, data):
        """Decode given bytes object `data` as given type `name` and return
        the decoded data as a dictionary.

        >>> foo.decode('Question', b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?')
        {'id': 1, 'question': 'Is 1+1=3?'}

        """

        return self._types[name].decode(data)


def _compile_any_defined_by_type(type_, choices):
    type_['choices'] = {}

    for key, value in choices.items():
        tokens = ['Dummy', '::=', [], value, []]
        type_['choices'][key] = convert_type_tokens(tokens)


def _compile_any_defined_by_choices(specification,
                                    any_defined_by_choices):
    for location, choices in any_defined_by_choices.items():
        module_name = location[0]
        type_names = location[1:-1]
        member_name = location[-1]
        types = specification[module_name]['types']

        if len(type_names) == 0:
            _compile_any_defined_by_type(types[member_name], choices)
        else:
            for type_name in type_names:
                types = types[type_name]

            for member in types['members']:
                if member['name'] != member_name:
                    continue

                _compile_any_defined_by_type(member, choices)
                break


def compile_dict(specification, codec='ber', any_defined_by_choices=None):
    """Compile given ASN.1 specification dictionary and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``jer``,
    ``'per'``, ``'uper'`` and ``'xer'``.

    >>> foo = asn1tools.compile_dict(asn1tools.parse_files('foo.asn'))

    """

    codecs = {
        'ber': ber,
        'der': der,
        'jer': jer,
        'per': per,
        'uper': uper,
        'xer': xer
    }

    try:
        codec = codecs[codec]
    except KeyError:
        raise CompileError("unsupported codec '{}'".format(codec))

    if any_defined_by_choices:
        _compile_any_defined_by_choices(specification,
                                        any_defined_by_choices)

    return Specification(codec.compile_dict(specification))


def compile_string(string, codec='ber', any_defined_by_choices=None):
    """Compile given ASN.1 specification string and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``jer``,
    ``'per'``, ``'uper'`` and ``'xer'``.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.compile_string(fin.read())

    """

    return compile_dict(parse_string(string),
                        codec,
                        any_defined_by_choices)


def compile_files(filenames, codec='ber', any_defined_by_choices=None):
    """Compile given ASN.1 specification file(s) and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``jer``,
    ``'per'``, ``'uper'`` and ``'xer'``.

    >>> foo = asn1tools.compile_files('foo.asn')

    """

    return compile_dict(parse_files(filenames),
                        codec,
                        any_defined_by_choices)
