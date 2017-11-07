from lxml import etree
from lxml.builder import ElementMaker
from ._lxml import makeelement
from .constants import NS_MAP
from collections import namedtuple
from .exceptions import *
from .record import *

XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

comp_elem = namedtuple('CompElem', 'parent')
complex_elem = {'subject': 'some stuff',
                'title': comp_elem('titleInfo'),
                'name': comp_elem('name')}

# class MODSWriter:


class MODSMaker(object):
    """

    """

    def __init__(self, version="3.6", collection=False):
        """
        
        :param version: 
        :param collection: 
        """
        # if version == "3.6":
        #     MODS_SCHEMA_LOC = 'http://www.loc.gov/standards/mods/v3/mods-3-6.xsd'
        # elif version == "3.4":
        #     MODS_SCHEMA_LOC = 'http://www.loc.gov/standards/mods/v3/mods-3-4.xsd'
        # self._me = ElementMaker(
        #             namespace=NAMESPACES['mods'],
        #             nsmap=NAMESPACES,
        #             makeelement=makeelement)
        # if collection:
        #     self._root = self._me.modsCollection()
        # else:
        #     self._root = self._me.mods()
        # self._root.set(
        #         '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
        #         '{} {}'.format(NAMESPACES['mods'], MODS_SCHEMA_LOC))

        # if version == "3.6":
        #     NAMESPACES['mods_schema'] = 'http://www.loc.gov/standards/mods/v3/mods-3-6.xsd'
        # else:
        #     NAMESPACES['mods_schema'] = 'http://www.loc.gov/standards/mods/v3/mods-3-4.xsd'
        if collection is False:
            self._root = etree.Element('mods', xmlns=NS_MAP['mods'], nsmap=NS_MAP)
            if version == "3.6":
                self._root.set(
                    '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
                    '{} {}'.format(NS_MAP['mods'], 'http://www.loc.gov/standards/mods/v3/mods-3-6.xsd'))
            else:
                self._root.set(
                    '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
                    '{} {}'.format(NS_MAP['mods'], 'http://www.loc.gov/standards/mods/v3/mods-3-4.xsd'))
        if collection is True:
            self._root = etree.Element('modsCollection', xmlns=NS_MAP['mods'], nsmap=NS_MAP)
            if version == "3.6":
                self._root.set(
                    '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
                    '{} {}'.format(NS_MAP['mods'], 'http://www.loc.gov/standards/mods/v3/mods-3-6.xsd'))
            else:
                self._root.set(
                    '{{{}}}schemaLocation'.format(XSI_NAMESPACE),
                    '{} {}'.format(NS_MAP['mods'], 'http://www.loc.gov/standards/mods/v3/mods-3-4.xsd'))

    @property
    def tree(self):
        return self._root

    def as_xml(self, xml_declaration=False, pretty_print=True):
        return etree.tostring(
                self._root,
                xml_declaration=xml_declaration,
                pretty_print=pretty_print,
                encoding='utf-8')

    def dump(self):
        return etree.dump(self._root)


class RecordMaker(MODSMaker):

    def __init__(self):
        """

        """
        super(RecordMaker, self).__init__()

    def add_title(self, content):
        title_info = etree.SubElement(self._root, 'titleInfo')
        title = etree.SubElement(title_info, 'title')
        title.text = content

    def add_elem(self, elem, text, **kwargs):
        if elem not in complex_elem.keys():
            elem = etree.SubElement(self._root, elem, kwargs)
            elem.text = text
        else:
            raise ComplexElement

    def add_subject(self, text, uri=None, authority=None, authority_uri=None):
        # sub = Subject(text, uri, authority, authority_uri)
        subject = etree.SubElement(self._root, 'subject', authority=authority, valueURI=uri, authorityURI=authority_uri)
        topic = etree.SubElement(subject, 'topic')
        topic.text = text

