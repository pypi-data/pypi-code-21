# encoding: utf-8

import json
import random
import re
from functools import wraps
from collections import OrderedDict
from pyhttpintercept.config.constants import ModifierConstant

from tableutil.table import Table

import logging_helper

logging = logging_helper.setup_logging()


def parse_dictionary_parameters(parameters):

    def key(parameter):
        return parameter.split(u':')[0]

    def value(parameter):
        return u':'.join(parameter.split(u':')[1:])

    if not parameters[ModifierConstant.params]:
        parameters[ModifierConstant.params] = {}

    else:
        parameters[ModifierConstant.params] = re.sub(r",\s*(\w)",         # Remove Whitespace
                                                     r',\1',              # after comma
                                                     parameters[ModifierConstant.params])

        try:
            parameters[ModifierConstant.params] = {key(parameter): value(parameter)
                                                   for parameter
                                                   in parameters[ModifierConstant.params].split(u',')}

        except (IndexError, ValueError):
            raise ValueError(u"Bad parameters "
                             u"(probably a missing or extra ',' or ':') "
                             u"in {parameters}".format(parameters=parameters[ModifierConstant.params]))

    logging.debug(u'params: {p}'.format(p=parameters))

    return parameters

# ------------------------------------------------------------------------------
TRUE = u'true'
FALSE = u'false'
BOOLEANS = (TRUE, FALSE)


def get_parameter(parameter,
                  parameters,
                  default=None):
    value = None
    try:
        value = parameters[parameter]

    except:
        pass

    try:
        value = parameters[parameter.lower()]

    except:
        pass

    try:
        value = parameters[ModifierConstant.params][parameter]

    except:
        pass

    try:
        value = parameters[ModifierConstant.params][parameter.lower()]

    except:
        pass

    if value is None:
        return default

    return value if value.lower() not in BOOLEANS else value.lower() == TRUE

if __name__ == u"__main__":
    assert get_parameter(u'a',
                         {u'a': u'True', ModifierConstant.params: {u'b': u'signed'}},
                         None)
    assert get_parameter(u'a',
                         {u'a': u'true', ModifierConstant.params: {u'b': u'Signed'}},
                         u'x')
    assert get_parameter(u'a',
                         {u'a': u'False', ModifierConstant.params: {u'b': u'signed'}},
                         None) is False
    assert get_parameter(u'a',
                         {u'a': u'false', ModifierConstant.params: {u'b': u'signed'}},
                         None) is False
    assert get_parameter(u'a',
                         {u'a': u'flAnge', ModifierConstant.params: {u'b': u'signed'}},
                         None) == u'flAnge'
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'True'}},
                         None)
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'true'}},
                         u'x')
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'False'}},
                         None) is False
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'false'}},
                         None) is False
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'flAnge'}},
                         None) == u'flAnge'
    assert get_parameter(u'c',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'false'}}) is None

    assert get_parameter(u'c',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'flAnge'}},
                         u'default') == u'default'


# -----------------------------------------------------------------------------


def parse_list_parameters(parameters):

    if not parameters[ModifierConstant.params]:
        parameters[ModifierConstant.params] = []
        return
    if not isinstance(parameters[ModifierConstant.params], list):
        parameters[ModifierConstant.params] = re.sub(r",\s*(\w)",             # Remove Whitespace
                                                     r',\1',                  # after comma
                                                     parameters[ModifierConstant.params])
        try:
            parameters[ModifierConstant.params] = [value.strip()
                                                   for value
                                                   in parameters[ModifierConstant.params].split(u',')]
        except ValueError:
            raise ValueError(u"Bad parameters (probably a missing"
                             u" or extra ',') in {parameters}".format(parameters=parameters[ModifierConstant.params]))

# -----------------------------------------------------------------------------


def parse_json_parameters(parameters):

    if isinstance(parameters[ModifierConstant.params], basestring):
        if not parameters[ModifierConstant.params]:
            parameters[ModifierConstant.params] = []
            return

        try:
            parameters[ModifierConstant.params] = json.loads(parameters[ModifierConstant.params])

        except ValueError:
            raise ValueError(u"Bad parameters (probably malformed JSON) "
                             u"in {parameters}".format(parameters=parameters[ModifierConstant.params]))

# -----------------------------------------------------------------------------


def decorate_for_dictionary_parameters(modifier):

    """
    Calls the modifier after extracting the parameters as a dictionary.

    e.g. parameters[u'parameters'] == u"start:1300, interval:60"
    is converted to parameters[u'parameters'] == {u'start':    u'1300',
                                                  u'interval': u'60"}
    """
    @wraps(modifier)
    def wrapper(request,
                response,
                parameters):

        # logging.debug(u'in decorate_for dictionary parameters')

        parse_dictionary_parameters(parameters)

        modifier(request,
                 response,
                 parameters)

        return response

    return wrapper

# ------------------------------------------------------------------------------


def decorate_for_list_parameters(modifier):

    """
    Calls the modifier after extracting the parameters as a list.

    e.g. parameters[u'parameters'] == u"1, 2, 3, 4"
    is converted to parameters[u'parameters'] == [u"1", u"2", u"3", u"4"]
    """
    @wraps(modifier)
    def wrapper(request,
                response,
                parameters):

        # logging.debug(u'in decorate_for list parameters')

        parse_list_parameters(parameters)

        modifier(request,
                 response,
                 parameters)

        return response

    return wrapper
# ------------------------------------------------------------------------------


def decorate_for_json_parameters(modifier):

    """
    Calls the modifier after extracting the parameters as a json string and
    converting to a python object (integer, float, string, list or dictionary)

    e.g. parameters[u'parameters'] == '{"a": [1, 2, 3], "b": "some string"}'
    is converted to parameters[u'parameters'] == {u'a': [1, 2, 3], u'b': u'some string'}
    """
    @wraps(modifier)
    def wrapper(request,
                response,
                parameters):

        # logging.debug(u'in decorate_for list parameters')

        parse_json_parameters(parameters)

        modifier(request,
                 response,
                 parameters)

        return response

    return wrapper


# ------------------------------------------------------------------------------


def decorate_for_json_modifier(modifier):

    u"""
    calls the modifier with the response content
    already extracted from JSON as an ordered dictionary
    """
    @wraps(modifier)
    def wrapper(request,
                response,
                parameters):

        # logging.debug(u'in decorate_for_json_modifier')

        try:
            response._content = json.loads(response.content,
                                           object_pairs_hook = OrderedDict)
        except (TypeError, ValueError) as err:
            logging.error(u'Failed loading response to JSON')
            logging.error(err)
            return response

        modifier(request,
                 response,
                 parameters)

        if not isinstance(response.content, basestring):
            response._content = json.dumps(response.content)

        return response

    return wrapper


# ------------------------------------------------------------------------------


def get_hostname_from_url(url):
    return url.split(u'//:')[-1].split(u'/')[0]


def get_hostname_from_response(response):
    return get_hostname_from_url(response.url)


def unicodify(string):

    u"""
    Replaces ASCII characters in a string with
    a random similar Unicode character

    e.g. 'utf8ify' -> 'ūtf8ífŷ'
    """

    unicode_lookup = {u'A': u'AÀÁÂÄÆÃÅĀ',
                      u'C': u'CĆČ',
                      u'E': u'EÈÉÊËĒĖĘ',
                      u'I': u'IÌĮĪÍÏÎ',
                      u'L': u'LŁ',
                      u'N': u'NŃÑ',
                      u'O': u'OÕŌØŒÓÒÖÔ',
                      u'S': u'SŚŠ',
                      u'U': u'UŪÚÙÜÛ',
                      u'W': u'WŴ',
                      u'Y': u'YŶ',
                      u'Z': u'ZŽŹŻ',

                      u'a': u'aàáâäæãåā',
                      u'c': u'cçćč',
                      u'e': u'eèéêëēėę',
                      u'i': u'iìįīíïî',
                      u'l': u'lł',
                      u'n': u'nńñ',
                      u'o': u'oõōøœóòöô',
                      u's': u'sßśš',
                      u'u': u'uūúùüû',
                      u'w': u'wŵ',
                      u'y': u'yŷ',
                      u'z': u'zžźż',
                      }

    def lookup(character):
        try:
            return random.choice(unicode_lookup[character])

        except KeyError:
            return character

    return u''.join([lookup(c) for c in string])

# ------------------------------------------------------------------------------


def warn_on_invalid_json(json_object):
    try:
        json.loads(json_object)

    except ValueError:
        logging.warning(u'Content is not JSON')

# ------------------------------------------------------------------------------


def make_modifier_tooltip_from_docstring(mod):

    u"""
    converts a module's docstring to containing a tabulated representation

    e.g.
    docstring:
        ============================================================
        Delays the response for a number of seconds.
        ------------------------------------------------------------
        Filter     : N/A
        Override   : N/A
        Parameters : wait value in seconds
        ============================================================

    Result:
        ┌──────────────────────────────────────────────┐
        │            body.generate_timeout             │
        ├──────────────────────────────────────────────┤
        │ Delays the response for a number of seconds. │
        ├──────────────────────────────────────────────┤
        │    ┌────────────┬───────────────────────┐    │
        │    │ filter     │ N/A                   │    │
        │    │ override   │ N/A                   │    │
        │    │ parameters │ wait value in seconds │    │
        │    └────────────┴───────────────────────┘    │
        └──────────────────────────────────────────────┘

    :param mod: a python module object
    :return: unicode string
    """

    def extract_field(lines,
                      join_lines=True):

        line_parts = lines[0].split(u':')
        if len(line_parts) == 1 or not line_parts:
            return u'\n'.join(lines) if join_lines else lines
        lines.pop(0)
        indent = len(line_parts[0]) + 1
        key = line_parts[0].strip().lower()
        value = u':'.join(line_parts[1:])
        if value:
            indent += len(value[0]) - len(value[0].lstrip(u' '))
        value = [value.strip()]
        while lines:
            if lines[0].startswith(u' '):
                start_char = len(lines[0]) - len(lines[0].lstrip(u' '))
                if start_char < indent:
                    value.append(lines.pop(0).strip())
                else:
                    value.append(lines.pop(0)[indent:])
            else:
                break
        return key, u'\n'.join(value) if join_lines else value

    def extract_fields(lines,
                       join_lines=True):
        fields = OrderedDict()
        line_count = len(lines)
        while lines:
            key, value = extract_field(lines=lines,
                                       join_lines=join_lines)
            fields[key] = value
            if len(lines) == line_count:
                raise ValueError(u'Field expected. Got {lines}'
                                 .format(lines=lines))
            line_count = len(lines)
        return fields

    def strip_leading_and_trailing_blank_lines(section):
        while section and not section[0]:
            section.pop(0)
        while section and not section[-1]:
            section.pop()
        return section

    def extract_sections_from_docstring(docstring_lines):

        sections = []
        line = docstring_lines.pop(0)
        while docstring_lines:
            section = []
            while docstring_lines and not(line.startswith(u'--') or
                                          line.startswith(u'==')):
                section.append(line)
                try:
                    line = docstring_lines.pop(0)
                except IndexError:
                    pass
            section = strip_leading_and_trailing_blank_lines(section)
            if section:
                sections.append(section)
            try:
                line = docstring_lines.pop(0)
            except IndexError:
                pass  # Empty list

        return sections

    docstring = (mod.__doc__
                 if mod.__doc__
                 else u'No documentation available\nfor {modifier}'
                      .format(modifier=mod))
    try:
        unicode(docstring)
    except UnicodeDecodeError:
        raise ValueError(u"Docstring contains unicode."
                         u"Add a 'u' to the front of the string!")

    if u'\t' in docstring:
        raise ValueError(u"Docstring contains tabs. "
                         u"Don't use tabs, you knobend, this is Python!")

    docstring_lines = docstring.splitlines()

    sections = [[mod.__name__]]
    sections.extend(extract_sections_from_docstring(docstring_lines))

    for i, section in enumerate(sections):
        try:
            fields = extract_fields(section)
            sections[i] = Table.init_from_tree(fields).text()
        except ValueError:
            sections[i] = u'\n'.join(section)
            # sections[i] = make_table(sections[i])

    tooltip_text = Table.init_as_grid(sections,
                                      columns=1).text()
    return tooltip_text


if __name__ == u"__main__":
    from pyhttpintercept.intercept.modifiers.body import generate_timeout
    T = make_modifier_tooltip_from_docstring(module=generate_timeout)
    print T
    pass
