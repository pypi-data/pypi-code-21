# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from datetime import datetime
import re
import struct
from pywikibot.xmlreader import XmlDump

from ..expand import tools


rTIME = re.compile(r'[\-\:TZ]')
TIME_FORMAT = "%Y%m%d%H%M%S"


class XMLPage(object):

    def __init__(self, entry):
        if isinstance(entry, dict):
            self._entry = entry
        else:
            ts = rTIME.sub('', entry.timestamp)
            ts = datetime.strptime(ts, TIME_FORMAT)
            self._entry = {}

            self.id = entry.id
            self.title = entry.title
            self.ns = int(entry.ns)
            self.timestamp = ts
            self.revisionid = int(entry.revisionid)
            self.isredirect = entry.isredirect
            self.text = entry.text

    def __getattr__(self, key):
        return self._entry[key]

    @property
    def clean_title(self):
        return tools.clean_title(self.title)

    @property
    def redirect_target(self):
        return tools.clean_title(tools.redirect_target(self.text))


def xml_generator(xml_filename, namespaces=None):
    """
    yield (<dump index>, XMLPage)
    """
    dump = XmlDump(xml_filename)

    gen = dump.parse()

    if not namespaces:
        for idx, page in enumerate(gen):
            yield idx, XMLPage(page)
    else:
        for idx, page in enumerate(gen):
            if int(page.ns) in namespaces:
                yield idx, XMLPage(page)


def iter_index_file(filename):
    fmt = struct.Struct("I")

    with open(filename, "rb") as fd:
        while True:
            data = fd.read(fmt.size)
            if not data:
                break

            index, = fmt.unpack(data)

            yield index


def indexed_xml_generator(xml_filename, index_file=None):
    if not index_file:
        index_file = "%s.idx" % xml_filename

    it_next_page = iter(iter_index_file(index_file))

    try:
        dump = XmlDump(xml_filename)
        gen = dump.parse()

        next_page = next(it_next_page)

        for idx, page in enumerate(gen):
            pid = int(page.id)

            if next_page == pid:
                yield idx, XMLPage(page)
                next_page = next(it_next_page)
            else:
                yield idx, None
    except StopIteration:
        pass
