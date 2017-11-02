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

import os.path
import random
import string
import xml.etree.ElementTree as Et

from . import utils


def gen_random_number_array():
    max_size = random.randrange(10, 255)
    return ', '.join([str(random.randrange(-128, 127)) for _ in range(0, max_size)])


def gen_random_number(field):
    xtype = field.get('type')
    if xtype.startswith('int'):
        width = int(xtype.replace('int', '').replace('_t', '')) - 1
        return str(random.randrange(-2 ** width, 2 ** width - 1))
    if xtype.startswith('uint'):
        width = int(xtype.replace('uint', '').replace('_t', ''))
        return str(random.randrange(0, 2 ** width - 1)) + 'U'
    if xtype == 'fp32_t':
        return str(random.random()) + 'f'
    if xtype == 'fp64_t':
        return str(random.random())


class MessageTestGenerator:
    def __init__(self, fd, var, abbrev, root, test_nr=0):
        self._fd = fd
        self._var = var
        self._abbrev = abbrev
        self._root = root
        self._node = root.find("message[@abbrev='%s']" % abbrev)
        self._fields = self._node.findall('field')
        self._temp_var = -1
        self._test_nr = test_nr

    def make_temp(self):
        self._temp_var += 1
        return 'tmp_%s_%d' % (self._var, self._temp_var)

    def fill_header_field(self, func, field_name):
        field = self._root.find("header/field[@abbrev='%s']" % field_name)
        value = gen_random_number(field)
        self._fd.append('{0}.{1}({2});'.format(self._var, func, value))

    def fill_header(self):
        self.fill_header_field('setTimeStamp', 'timestamp')
        self.fill_header_field('setSource', 'src')
        self.fill_header_field('setSourceEntity', 'src_ent')
        self.fill_header_field('setDestination', 'dst')
        self.fill_header_field('setDestinationEntity', 'dst_ent')

    def declare(self):
        self._fd.append('IMC::%s %s;' % (self._abbrev, self._var))

    def fill_fields(self):
        for field in self._fields:
            self.fill_field(field)

    def declare_and_fill(self):
        self.declare()
        self.fill_fields()

    def marshall(self):
        self._fd.append('')
        self._fd.append('try\n{')
        self._fd.append('IMC::ByteBuffer bfr;')
        self._fd.append('IMC::Packet::serialize(&%s, bfr);' % self._var)
        self._fd.append('IMC::Message* msg_d = IMC::Packet::deserialize(bfr.getBuffer(), bfr.getSize());')
        self._fd.append('REQUIRE({0} == *msg_d);'.format(self._var))
        self._fd.append('delete msg_d;')
        self._fd.append('}\ncatch (IMC::InvalidMessageSize& e)\n{\n(void)e;')
        self._fd.append('REQUIRE({0}.getSerializationSize() > IMC::Message::maxSerializedSize());'.format(self._var))
        self._fd.append('}')

    def test_other(self):
        self._fd.append('')
        self._fd.append('std::ostringstream ss;')
        self._fd.append('msg.toJSON(ss);')
        self._fd.append('msg.getSubId();')
        self._fd.append('msg.setSubId(1);')
        self._fd.append('delete msg.clone();')

    # Test if message type is a group.
    def is_group(self, abbrev):
        return self._root.find("message-groups/message-group[@abbrev='%s']" % abbrev) is not None

    # Retrieve a list of message abbreviations matching a certain type.
    def get_abbrevs(self, xtype=None):
        if xtype is None:
            return [m.get('abbrev') for m in self._root.findall('message')]
        if self.is_group(xtype):
            return [m.get('abbrev') for m in
                    self._root.findall("message-groups/message-group[@abbrev='%s']/message-type" % xtype)]
        return [xtype]

    # Choose a random message abbrev suitable for a given field.
    def rand_message(self, field):
        types = self.get_abbrevs(field.get('message-type'))
        return random.choice(types)

    def push_message(self, name, field):
        tname = self.make_temp()
        msg = MessageTestGenerator(self._fd, tname, self.rand_message(field), self._root)
        msg.declare_and_fill()
        self._fd.append('{0}.{1}.push_back({2});'.format(self._var, name, tname))

    def set_message(self, name, field):
        tname = self.make_temp()
        msg = MessageTestGenerator(self._fd, tname, self.rand_message(field), self._root)
        msg.declare_and_fill()
        self._fd.append('{0}.{1}.set({2});'.format(self._var, name, tname))

    def fill_field(self, field):
        xtype = field.get('type')
        name = utils.get_name(field)
        if xtype == 'plaintext':
            chars = string.ascii_uppercase * 10
            value = ''.join(random.sample(chars, random.randrange(10, 255)))
            self._fd.append('%s.%s.assign("%s");' % (self._var, name, value))
        elif xtype == 'rawdata':
            tname = self.make_temp()
            self._fd.append('const char %s[] = {%s};' % (tname, gen_random_number_array()))
            self._fd.append('{0}.{1}.assign({2}, {2} + sizeof({2}));'.format(self._var, name, tname))
        elif xtype == 'message':
            self.set_message(name, field)
        elif xtype == 'message-list':
            imsgs = random.randrange(0, 2)
            for x in range(0, imsgs):
                self.push_message(name, field)
        else:
            value = gen_random_number(field)
            self._fd.append('%s.%s = %s;' % (self._var, name, value))


def gen_test_file(xml_fname, dst_fname, force):
    xml_md5 = utils.compute_md5(xml_fname)
    dst_file = os.path.basename(dst_fname)
    dst_folder = os.path.dirname(dst_fname)

    # Create destination folder.
    if len(dst_folder) > 0:
        try:
            os.makedirs(dst_folder, exist_ok=True)
        except OSError as e:
            print('ERROR: failed to create destination folder:', dst_folder, ':', e.strerror)
            return 1

    if not force:
        if utils.file_md5_matches(dst_fname, xml_md5):
            print('* ' + dst_fname + ' [Skipped]')
            return 0

    # Parse XML specification.
    tree = Et.parse(xml_fname)
    root = tree.getroot()

    fd = utils.File(dst_file, dst_folder, ns=False, md5=xml_md5)
    fd.add_imc_header('%s/ByteBuffer.hpp' % utils.BASE_FOLDER)
    fd.add_imc_header('%s/Packet.hpp' % utils.BASE_FOLDER)
    fd.add_imc_header('%s/AllMessages.hpp' % utils.SPEC_FOLDER)
    fd.append('')
    fd.append('#define CATCH_CONFIG_MAIN')
    fd.append('#include "catch.hpp"')
    fd.append('')
    abbrevs = [msg.get('abbrev') for msg in root.findall('message')]
    for abbrev in abbrevs:
        for test in range(0, 3):
            fd.append('TEST_CASE("%s - Serialization/Deserialization #%d")' % (abbrev, test))
            fd.append('{')
            msg = MessageTestGenerator(fd, 'msg', abbrev, root, test)
            msg.declare()
            msg.fill_header()
            msg.fill_fields()
            msg.marshall()
            msg.test_other()
            fd.append('}\n')
    fd.write()
