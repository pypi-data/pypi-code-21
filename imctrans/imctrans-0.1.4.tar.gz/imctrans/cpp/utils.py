# -*- coding: utf-8 -*-
############################################################################
# Copyright 2017 OceanScan - Marine Systems & Technology, Lda.             #
############################################################################
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
# http://www.apache.org/licenses/LICENSE-2.0                               #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
# Author: Ricardo Martins                                                  #
############################################################################

import hashlib
import os.path
from xml.dom.minidom import Node, parseString
from xml.etree import ElementTree as Et

BASE_FOLDER = 'Base'
SPEC_FOLDER = 'Spec'


def get_enum_name(name):
    """ Sanitize the name of enumerations."""
    return name.replace(' ', '') + 'Enum'


def get_bfield_name(name):
    """Sanitize the name of bitfields."""
    return name.replace(' ', '') + 'Bits'


def get_name(node):
    """Retrieve the name of a field."""
    return node.get('abbrev').lower()


def comment(text, dox=True, nl='\n'):
    """Convert text to C++ comment."""
    c = ''
    if dox:
        c = '!'
    return '//' + c + ' ' + text + '.' + nl


def get_cxx_copyright(xml_md5, skip_md5=False):
    """Extract copyright from this script and convert it to a format suitable to be used in C++ files."""

    fd = open(os.path.abspath(__file__).replace('.pyc', '.py'))
    result = []
    header = False
    for line in fd.readlines():
        line = line.strip()
        if len(line) == 0:
            break
        if line.startswith('##') and not header:
            header = True
            result.append(line)
        elif header:
            result.append(line)

    result = [l[1:] for l in result]
    result = ['//' + l for l in result]
    result = [l.replace('#', '*') for l in result]
    result.append('// Automatically generated.'.ljust(len(result[0]) - 1) + '*')
    result.append(result[0])
    if not skip_md5:
        result.append(('// IMC XML MD5: ' + xml_md5).ljust(len(result[0]) - 1) + '*')
        result.append(result[0])
    return '\n'.join(result) + '\n'


def beautify(text):
    """Cleanup and indent source file."""
    indent = 0
    blank = False
    list0 = []

    # Remove extra empty lines and indent.
    lines = text.splitlines()
    for line in lines:
        strip = line.strip()
        if len(strip) == 0:
            if blank:
                continue
            else:
                blank = True
                list0.append('')
                continue
        else:
            blank = False

        if strip == '};' and len(list0[-1]) == 0:
            list0.pop()

        if strip == '{':
            list0.append(' ' * indent + strip)
            indent += 2
        elif strip == '}' or strip == '};':
            indent -= 2
            list0.append(' ' * indent + strip)
        elif strip == 'public:' or strip == 'protected:' or strip == 'public:':
            list0.append(' ' * (indent - 2) + strip)
        else:
            list0.append(' ' * indent + strip)

    # Remove empty lines between blocks.
    list1 = []
    for line in list0:
        strip = line.strip()
        if (strip == '}' or strip == '};') and len(list1[-1]) == 0:
            list1.pop()
        list1.append(line)

    # Remove extra empty lines at EOF.
    while len(list1[-1]) == 0:
        list1.pop()

    return '\n'.join(list1) + '\n'


def abbrev_to_var(abbrev, prefix=''):
    """Convert camel case abbrev to proper variable name."""
    name = ''
    for c in abbrev:
        if c.isupper():
            name += '_' + c
        else:
            name += c

    if prefix == '':
        return name
    else:
        return prefix + '_' + name[1:].lower()


def abbrev_to_macro(abbrev, prefix=''):
    """Convert camel case abbrev to proper macro name."""
    name = ''
    for c in abbrev:
        if c.isupper():
            name += '_' + c
        else:
            name += c

    if prefix == '':
        return name
    else:
        return prefix + '_' + name[1:].upper()


def compute_md5(imc_xml):
    """Compute MD5 sum."""
    m = hashlib.md5()
    m.update(open(imc_xml, 'rb').read())
    return m.hexdigest()


def file_md5_matches(file_name, xml_md5):
    try:
        with open(file_name, 'r') as fd:
            cpp_md5 = ''
            for line in fd:
                if line.strip().startswith('// IMC XML MD5:'):
                    parts = line.split(':')
                    cpp_md5 = parts[1].split()
                    cpp_md5 = cpp_md5[0]

            return xml_md5 == cpp_md5
    except IOError:
        return False


def get_first_level_deps(root, abbrev):
    msg = root.find("message[@abbrev='%s']" % abbrev)

    if msg is None:
        return []

    return [field.get('message-type') for field in msg.findall('field[@message-type]')]


def get_msg_groups(root, abbrev):
    groups = root.findall("message-groups/message-group")
    for group in groups:
        type_id = group.find('message-type[@abbrev="%s"]' % abbrev)
        if type_id is not None:
            return [group.get('abbrev')]

    return []


def get_cxx_type(field_node):
    """Retrieve the C++ type of a message field node"""
    xtype = field_node.get('type')
    msg_type = field_node.get('message-type', 'Message')
    if xtype == 'plaintext':
        return 'std::string'
    elif xtype == 'rawdata':
        return 'std::vector<char>'
    elif xtype == 'message':
        return 'InlineMessage<%s>' % msg_type
    elif xtype == 'message-list':
        return 'MessageList<%s>' % msg_type
    elif xtype == 'fp64_t':
        return 'double'
    elif xtype == 'fp32_t':
        return 'float'
    else:
        return xtype


def is_fixed(field_node):
    t = field_node.get('type')
    if t == 'message':
        return False
    elif t == 'plaintext':
        return False
    elif t == 'rawdata':
        return False
    elif t == 'message-list':
        return False
    return True


def get_clear(field_node):
    rv = get_name(field_node)
    if is_fixed(field_node):
        rv += ' = 0'
    else:
        rv += '.clear()'
    return rv + ';'


def get_not_equal(field_node):
    name = get_name(field_node)
    return 'if ({0} != other__.{0}) return false;'.format(name)


def get_field_names(message):
    return [get_name(field) for field in message.findall('field')]


def call_inline_message_function(name, func, args):
    return 'if (!' + name + '.isNull())\n{\n' + \
           name + '.get()->' + func + '(' + args + ');\n' + \
           '}\n'


def call_message_list_function(name, func, args):
    return name + '.' + func + '(' + args + ');\n'


class Macro:
    def __init__(self, name, value, desc):
        self._data = {'name': 'IMC_' + name, 'value': value, 'desc': desc}

    def __str__(self):
        return comment(self._data['desc']) + \
               '#define %(name)s %(value)s' % self._data


class Var:
    def __init__(self, name, xtype, desc=''):
        self._data = {'name': name, 'type': xtype, 'desc': desc}

    def as_func_arg(self):
        return '%(type)s %(name)s' % self._data

    def as_decl(self):
        return comment(self._data['desc']) + \
               '%(type)s %(name)s;' % self._data

    def __str__(self):
        return '%(type)s %(name)s' % self._data


class StructField:
    def __init__(self, name, xtype, desc):
        self._data = {'name': name, 'type': xtype, 'desc': desc}

    def __str__(self):
        return comment(self._data['desc']) + \
               '%(type)s %(name)s' % self._data


class Struct:
    def __init__(self, name, desc):
        self._name = name
        self._desc = desc
        self._fields = []

    def add_field(self, field):
        self._fields.append(field)

    def __str__(self):
        out = comment(self._desc)
        out += 'struct ' + self._name + '\n'
        out += '{\n'
        out += ';\n'.join([str(f) for f in self._fields]) + ';\n'
        out += '};\n'
        return out


class EnumField:
    def __init__(self, name, value, desc):
        self._data = {'name': name, 'value': value, 'desc': desc}

    def __str__(self):
        if self._data['value'] == '':
            return comment(self._data['desc']) + '%(name)s' % self._data
        return comment(self._data['desc']) + '%(name)s = %(value)s' % self._data


class Enum:
    def __init__(self, name, desc):
        self._name = name
        self._desc = desc
        self._fields = []

    def add_field(self, field):
        self._fields.append(field)

    def __str__(self):
        out = comment(self._desc)
        out += 'enum ' + self._name + '\n'
        out += '{\n'
        out += ',\n'.join([str(f) for f in self._fields]) + '\n'
        out += '};\n'
        return out


class Function:
    def __init__(self, name, rett=None, args=None, const=False, inline=False, static=False):
        self._data = {}
        self._name = name
        self._rett = rett
        self._args = args
        self._const = const
        self._inline = inline
        self._body = ''
        self._class = None
        self._static = static

        if self._args is None:
            self._args_str = 'void'
        else:
            self._args_str = ', '.join([v.as_func_arg() for v in self._args])

        if self._const:
            self._const_str = ' const'
        else:
            self._const_str = ''

    def is_inline(self):
        return self._inline

    def set_class(self, name):
        self._class = name

    def body(self, text):
        self._body = text

    def add_body(self, text):
        self._body += text + '\n'

    def decl(self):
        out = ''

        if self._static:
            out += 'static '

        if self._rett is not None:
            out += self._rett + '\n'

        return out + self._name + '(' + self._args_str + ')' + self._const_str + ';\n'

    def __str__(self):
        out = ''

        if self._static:
            out += 'static '

        if self._rett is not None:
            out += self._rett + '\n'

        if self._class is not None:
            name = self._class + '::' + self._name
        else:
            name = self._name

        return out + name + '(' + self._args_str + ')' + self._const_str + '\n' + '{\n' + self._body + '\n}\n'


class Dependencies:
    def __init__(self, root):
        self._root = root
        self._abbrevs = []

    def append(self, abbrev):
        if abbrev in self._abbrevs:
            return
        self._abbrevs.append(abbrev)

    def get_deps(self, abbrev):
        msg = self._root.find("message[@abbrev='%s']" % abbrev)

        if msg is None:
            return

        if msg.get('abbrev') in self._abbrevs:
            return

        types = [field.get('message-type') for field in msg.findall('field[@message-type]')]
        for xtype in types:
            if xtype not in self._abbrevs:
                self.get_deps(xtype)

        self.append(abbrev)

    def get_list(self):
        for msg in self._root.findall('message'):
            self.get_deps(msg.get('abbrev'))
        return self._abbrevs


class File:
    def __init__(self, name, folder, ns, stdout=False, md5=None, skip_md5=False):
        self.path = os.path.join(folder, name)
        self.path_file = os.path.split(self.path)[1]
        self.path_ext = os.path.splitext(self.path)[1]
        self.name = os.path.splitext(self.path_file)[0]
        self.isoc_hdrs = []
        self.imc_hdrs = []
        self.local_hdrs = []
        self.text = ''
        self._ns = ns
        self._stdout = stdout
        self._skip_md5 = skip_md5
        self._macros = []
        if md5 is None:
            self.md5 = 'unknown'
        else:
            self.md5 = md5

        if len(folder) > 0:
            os.makedirs(folder, exist_ok=True)

    def append(self, text):
        self.text += str(text) + '\n'

    def add_isoc_headers(self, *headers):
        self.isoc_hdrs += headers

    def add_imc_headers(self, *headers):
        self.imc_hdrs += ['IMC/' + h for h in headers]

    def add_imc_header(self, header):
        self.imc_hdrs.append('IMC/' + header)

    def add_local_headers(self, *headers):
        self.local_hdrs += headers

    def add_local_header(self, header):
        self.local_hdrs.append(header)

    def add_macro(self, macro):
        self._macros.append(macro)

    def write(self):
        print('* ' + self.path)
        text = get_cxx_copyright(self.md5, self._skip_md5) + '\n'
        if self.path_ext == '.hpp':
            prefix = 'IMC'
            guard = prefix + '_' + self.name.upper() + '_HPP_INCLUDED_'
            text += '#ifndef ' + guard + '\n'
            text += '#define ' + guard + '\n\n'

        if len(self.isoc_hdrs) > 0:
            text += comment('ISO C++ 98 headers', dox=False)
            for hdr in self.isoc_hdrs:
                text += '#include <' + hdr + '>\n'
            text += '\n'

        if len(self.imc_hdrs) > 0:
            text += comment('IMC headers', dox=False)
            for hdr in self.imc_hdrs:
                text += '#include <' + hdr + '>\n'
            text += '\n'

        if len(self.local_hdrs) > 0:
            text += comment('Local headers', dox=False)
            for hdr in self.local_hdrs:
                text += '#include "' + hdr + '"\n'
            text += '\n'

        for macro in self._macros:
            text += str(macro) + "\n\n"

        if self._ns:
            text += 'namespace IMC\n{\n'

        text += self.text

        if self._ns:
            text += '}\n'

        if self.path_ext == '.hpp':
            text += '\n#endif'

        text += '\n'
        new_text = beautify(text)
        try:
            old_text = open(self.path).read()
        except IOError:
            old_text = ''

        if self._stdout:
            import sys
            sys.stdout.write(new_text)
            return

        if new_text != old_text:
            fd = open(self.path, 'w')
            fd.write(new_text)
            fd.close()


def xml_node_remove_blanks(xml_node):
    for x in xml_node.childNodes:
        if x.nodeType == Node.TEXT_NODE:
            if x.nodeValue:
                x.nodeValue = x.nodeValue.strip()
        elif x.nodeType == Node.ELEMENT_NODE:
            xml_node_remove_blanks(x)


def xml_node_md5(xml_node):
    xml = Et.tostring(xml_node, encoding='utf-8')
    node = parseString(xml)
    xml_node_remove_blanks(node)
    node.normalize()
    text = node.toprettyxml(indent='', newl='', encoding="utf-8")
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()
