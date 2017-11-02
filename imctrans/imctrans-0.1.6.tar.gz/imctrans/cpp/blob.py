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

import binascii
import gzip
import os.path
import tempfile
import xml.etree.ElementTree as Et

from . import utils

STRIP_ATTRS = ['flags', 'source']


def create_imc_blob(xml_fname, dst_folder, dst_file, force):
    dst_fname = os.path.join(dst_folder, dst_file)
    xml_md5 = utils.compute_md5(xml_fname)

    # Create destination folder.
    try:
        os.makedirs(dst_folder, exist_ok=True)
    except OSError as e:
        print('ERROR: failed to create destination folder: ' + e.strerror)
        return 1

    if not force:
        if utils.file_md5_matches(dst_fname, xml_md5):
            print('* ' + dst_fname + ' [Skipped]')
            return 0

    # Parse XML specification.
    tree = Et.parse(xml_fname)

    # Remove 'description' and unneeded attributes tags.
    for parent in tree.getiterator():
        map(lambda a: parent.attrib.pop(a, None), STRIP_ATTRS)
        for child in parent:
            map(lambda a: child.attrib.pop(a, None), STRIP_ATTRS)
            if child.tag == 'description':
                parent.remove(child)

    # Create output document.
    root = tree.getroot()
    text = b'<?xml version="1.0" encoding="UTF-8"?>\n' + Et.tostring(root, encoding='utf-8')

    # Compress to temporary file.
    tmp = tempfile.NamedTemporaryFile(delete=False)
    f_out = gzip.GzipFile(tmp.name, 'wb', compresslevel=9, mtime=0)
    f_out.write(text)
    f_out.close()

    # Create HPP file.
    hpp = utils.File(dst_file, dst_folder, ns=True, md5=xml_md5)
    hpp.add_isoc_headers('cstddef')

    # Byte array.
    hpp.append('const unsigned char c_imc_blob[] = \n{')
    octets = []
    with open(tmp.name, 'rb') as f_gz:
        h = binascii.hexlify(f_gz.read())
        octets += ['0x' + h[i: i + 2].decode() for i in range(0, len(h), 2)]
    octets_per_line = 12
    for i in range(0, len(octets), octets_per_line):
        ol = octets[i: i + octets_per_line]
        s = ','
        if i + octets_per_line >= len(octets):
            s = ''
        hpp.append(', '.join(ol) + s)

    hpp.append('};\n')

    hpp.append('class Blob')
    hpp.append('{')
    hpp.append('public:')

    # getData()
    f = utils.Function('getData', 'const unsigned char*', static=True)
    f.body('return c_imc_blob;')
    hpp.append(f)

    # getSize()
    f = utils.Function('getSize', 'size_t', static=True)
    f.body('return sizeof(c_imc_blob);')
    hpp.append(f)

    hpp.append('};')

    # Write files.
    hpp.write()
