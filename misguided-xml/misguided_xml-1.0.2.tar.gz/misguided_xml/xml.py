#!/usr/bin/env python
# encoding: utf-8
"""
xml.py

Created by Hywel Thomas on 2011-02-24.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import logging
import six
from collections import OrderedDict

from fdutil.string_scanner import StringScanner, StringScannerError
from fdutil.utf8file import UTF8File


STANDARD_XML_DECLARATION = u'<?xml version="1.0" encoding="UTF-8"?>'

ELEMENT   = u'path'
ATTRIBUTE = u'attribute'
VALUE     = u'value'
PARENT    = u'parent'
NAMESPACE = u'xmlns'
NAMESPACE_DELIMITER = u':'

TAG_SPLIT_LIMIT = 60
LINE_SPLIT_LIMIT = 50

INDENT = u' ' * 4


class NoXMLDeclarationDetected(Exception):
    pass


class InvalidXMLDeclaration(Exception):
    def __init__(self,
                 reason=u"Unknown"):
        self.reason=reason

    def __unicode__(self):

        return u"Invalid XML Declaration:%s" % self.reason

    def __str__(self):
        return unicode(self).encode(u'utf-8')


class XMLSyntaxError(Exception):
    pass


class XMLElementNotFound(Exception):
   def __init__(self,
                path):
       self.path = path

   def __unicode__(self):
       return u"No matching XML element at :%s" % self.path

   def __str__(self):
       return unicode(self).encode(u'utf-8')


class XMLTooManyElementsFound(Exception):

    def __init__(self, path):
        self.path = path

    def __unicode__(self):
        return u"Multiple elements returned for : {path}" % self.path

    def __str__(self):
        return unicode(self).encode(u'utf-8')


class XMLEndTagNotFound(Exception):
    def __init__(self,
                 tag,
                 value,
                 position):
        self.tag      = tag
        self.value    = value
        self.position = position

    def __unicode__(self):
        return (u"No end tag for <{tag}> with value '{value}' "
                u"at {position}".format(tag      = self.tag,
                                        value    = self.value,
                                        position = self.position))

    def __str__(self):
        return unicode(self).encode(u'utf-8')


class BadSearchCriteria(Exception):

    def __init__(self,
                 criteria):
        self.criteria = criteria

    def __unicode__(self):
        return u"Bad search criteria. " \
               u"Expected a dictionary, " \
               u"but got:\n{criteria}".format(criteria=self.criteria)

    def __str__(self):
        return unicode(self).encode(u'utf-8')


class UndefinedNamespace(Exception):

    def __init__(self,
                 namespace_and_tag):
        self.namespace_and_tag = namespace_and_tag

    def __unicode__(self):
        return u"Undefined namespace %s" % self.namespace_and_tag

    def __str__(self):
        return unicode(self).encode(u'utf-8')


TAG_START     = u'<'
TAG_END       = u'>'
OPEN_COMMENT  = u'<!--'
CLOSE_COMMENT = u"-->"
CDATA_START   = u'<![CDATA[['
CDATA_END     = u']]>'
DECLARATION_START = u'<?'
DECLARATION_END   = u'?>'

XML_ESCAPE_SEQUENCES = {u'"': u'&quot;',
                        u"'": u'&apos;',
                        u'<': u'&lt;',
                        u'>': u'&gt;',
                        u'&': u'&amp;'}
# Have had issues with escaping quote and apostrophe.
# Put back in 2016-04-12


def escape_syntax_markers(value):
    value = unicode(value)  # Can remove this if we can
    #                       # guarantee that values will be strings
    for escapeSequence in XML_ESCAPE_SEQUENCES:
        # Rather than be intelligent about this, do a double replace
        # 1st one changes escaped to non escaped (all will be non-escaped).
        # 2nd one changes non-escaped to escaped (all with be escaped)
        value = value.replace(XML_ESCAPE_SEQUENCES[escapeSequence],
                              escapeSequence)

        value = value.replace(escapeSequence,
                              XML_ESCAPE_SEQUENCES[escapeSequence])
    return value


def unescape_syntax_markers(value):
    value = unicode(value)  # Can remove this if we can guarantee
    #                       # that values will be strings
    for escapeSequence in XML_ESCAPE_SEQUENCES:
        # Rather than be intelligent about this, do a double replace
        # 1st one changes escaped to non escaped (all will be non-escaped).
        # 2nd one changes non-escaped to escaped (all with be escaped)
        value = value.replace(escapeSequence,
                              XML_ESCAPE_SEQUENCES[escapeSequence])

        value = value.replace(XML_ESCAPE_SEQUENCES[escapeSequence],
                              escapeSequence)
    return value


def normalise_element_path(path):
    """
    Path can be a list of element signatures or a string
    containing a list of element signatures separated by
    XML delimiters or '/'
    e.g. these are equivalent

    ['ADI3',
     'Title',
     'core:Ext',
     'ext:LocalizableTitleExt xml:lang="eng"',
     'ext:MarketingMessage']

    '<ADI3><Title><core:Ext><ext:LocalizableTitleExt xml:lang="eng"><ext:MarketingMessage>'

    'ADI3/Title/core:Ext/ext:LocalizableTitleExt xml:lang="eng"/ext:MarketingMessage'

    The Python list is the normalised version. Either string format will be converted
    to the list format.
    """
    if isinstance(path, list):
        return path

    if isinstance(path, basestring):
        path = path.strip().replace(u'\n', u'').replace(u'\t', u'')
        while u'> ' in path:
            path = path.replace(u'> ', u'>')

    if path[0] == u"<":
        path = path[1:-1].replace(u'><', u'/')

    return path.split(u'/')


def extract_attributes(attributes_string,
                       value_boundary =u'"'):
    """
    Extracts attributes from a string and constructs an
    ordered dictionary.
    e.g. ' attr1="value 1" attr2="value 2"

    :param attributes_string: ' attr1="value 1" attr2="value 2"'
    :param value_boundary: The character used to signify the start
                           and end of a value. e.g for attr="value" it's "
                           for attr=value use None
    returns OrderedDict({'attr1':'value 1',
                         'attr2':'value 2'})
    """
    attributes = OrderedDict()
    attr = StringScanner(attributes_string)
    while not attr.eos:
        attr.skip_whitespace()
        attribute_name = (attr.read_until_value_reached(u'=')).strip()
        attr.skip_over(u'=')
        attr.skip_whitespace()
        if value_boundary:
            attribute_value = attr.read_between(start = value_boundary,
                                                end   = value_boundary)
        else:
            attribute_value = attr.read_until_value_reached(u' ')
        if attribute_name != u"":
            attributes[attribute_name] = attribute_value

    return attributes


def dictionary_to_attributes_strings(attributes):
    return [u'{key}="{value}"'.format(key   = key,
                                      value = escape_syntax_markers(value))
            for key, value in six.iteritems(attributes)]


class XMLDeclaration(object):

    def __init__(self,
                 string_scanner):
        """

        :param string_scanner: StringScanner
        :return:
        """
        self.tag = u""

        try:
            string_scanner.check_and_skip(DECLARATION_START)
        except:

            string_scanner.skip_whitespace()
            try:
                string_scanner.check_and_skip(DECLARATION_START)
                string_scanner.throw(message = u'Spaces before declaration : ',
                                     exception = InvalidXMLDeclaration)
            except StringScannerError:
                raise NoXMLDeclarationDetected()

        tag = string_scanner.\
                  read_until_value_reached(DECLARATION_END).strip(u' ')

        try:
            string_scanner.check_and_skip(DECLARATION_END)
        except StringScannerError:
            raise string_scanner.throw(message=(u'Does not end with '
                                                + DECLARATION_END),
                                       exception=InvalidXMLDeclaration)

        if u'\n' in tag:
            raise string_scanner.throw(message=u'The declaration must '
                                               u'be on one line',
                                       exception=InvalidXMLDeclaration)
            
        if u' ' in tag:            
            self.tag = tag[0:tag.index(u' ')]
            try:
                self.attributes = extract_attributes(tag[tag.index(u' '):])
            except Exception as e:
                logging.exception(e)
                string_scanner.throw(u'XML Syntax Error in attributes')

        else:
            self.tag = tag
            self.attributes = OrderedDict()

        if self.tag != u'xml':
            raise InvalidXMLDeclaration(u'Header tag is not "xml"')

        # Declaration is good !

    def dictionary(self,
                   attribute_indicator):
        return {u'{attr}{key}'
                .format(attr = attribute_indicator,
                        key  = key): value
                for key, value in six.iteritems(self.attributes)}

    #
    def __unicode__(self):
        try:
            return self.__unicode
        except:
            self.__unicode = DECLARATION_START + self.tag
            attributes = u' '.join(dictionary_to_attributes_strings(
                                       self.attributes))

            if attributes:
                self.__unicode += u' ' + attributes

            self.__unicode += DECLARATION_END

            return self.__unicode

    def __str__(self):
        return unicode(self).encode(u'utf-8')


class InvalidXMLElement(Exception):
   def __init__(self, problem=u""):
       self.problem = problem

   def __str__(self):
       return unicode(self).encode(u'utf-8')

   def __unicode__(self):
       return u"Invalid XML. \n%s" % self.problem


class XMLComment(object):

    def __init__(self,
                 comment):
        self.comment = comment

    def __str__(self):
        return unicode(self).encode(u'utf-8')

    def __unicode__(self):
        try:
            return self.__unicode
        except:
            self.__unicode = OPEN_COMMENT + self.comment + CLOSE_COMMENT
            return self.__unicode


class XMLCDATA(object):

    def __init__(self,
                 cdata):
        self.cdata = cdata

    def __str__(self):
        return unicode(self).encode(u'utf-8')

    def __unicode__(self):
        try:
            return self.__unicode
        except:
            self.__unicode = CDATA_START + self.cdata + CDATA_END
            return self.__unicode


class XML(object):

    def __init__(self,
                 string     = None,
                 xml_file   = None,
                 parent     = None,
                 ignore_invalid_namespaces = False):

        if xml_file:
            self.filename = xml_file
            string = UTF8File(xml_file).contents
        elif string is None:
            raise XMLSyntaxError(u'Missing XML. '
                                 u'You must provide a string, '
                                 u'StringScanner of file reference')

        self.__parent = parent
        self.__scanner = (string
                          if isinstance(string, StringScanner)
                          else
                          StringScanner(string))
        self.tag = None
        self.namespace_value = None
        self.namespace_key = None
        self.__namespaces = {}
        self.__value = None
        self.__leading_comments = []
        self.__trailing_comments = []
        self.__children = []
        self.__tag_closed = False
        self.attributes = OrderedDict()
        self.ignore_invalid_namespaces = ignore_invalid_namespaces

        try:
            self.declaration = XMLDeclaration(self.__scanner)
        except NoXMLDeclarationDetected:
            self.declaration = u''

        self.__extract_leading_comments(self.__scanner)

        self.__get_tag(self.__scanner)

        if self.tag:
            while not self.__tag_closed and not self.__scanner.eos:

                self.__extract_value(self.__scanner)

                cdata = self.__extract_CDATA(self.__scanner)
                if cdata:
                    self.__children.append(cdata)
                    continue

                self.__extract_value(self.__scanner)

                comment = self.__extract_comment(self.__scanner)
                if comment:
                    self.__children.append(comment)
                    continue

                self.__extract_value(self.__scanner)

                self.__detect_end_tag(self.__scanner)

                if not self.__tag_closed:
                    child_element = self.__extract_child_element(
                                        self.__scanner)
                    self.__children.append(child_element)

        if self.tag is not None and self.__tag_closed is None:
            raise InvalidXMLElement(u"Missing end tag for '{tag}'"
                                    .format(tag = self.tag))
        else:
            self.__extract_trailing_comments(self.__scanner)

        pass  # Debug against this to check initialisation

    u"""          ┌────────────────────────────┐
                  │    Initialisation Support  │
                  └────────────────────────────┘           """
    @staticmethod
    def __extract_comment(scanner):
        scanner.skip_whitespace()
        if scanner.next_matches(OPEN_COMMENT):
            return XMLComment(scanner.read_between(start = OPEN_COMMENT,
                                                   end   = CLOSE_COMMENT))

    def __extract_leading_comments(self,
                                   scanner):
        while True:
            comment = self.__extract_comment(scanner)
            if comment:
                self.__leading_comments.append(comment)
            else:
                break

    def __extract_trailing_comments(self,
                                    scanner):
        while True:
            comment = self.__extract_comment(scanner)
            if comment:
                self.__trailing_comments.append(comment)
            else:
                break

    def __extract_child_element(self,
                                scanner):
        if scanner.peek() == TAG_START:
            return XML(string = scanner,
                       parent = self)

    def __extract_value(self,
                        scanner):
        value = scanner.read_until_value_reached(TAG_START).strip()
        if value:
            self.__children.append(value)
            self.__value = True

    def __extract_CDATA(self,
                        scanner):
        if scanner.next_matches(CDATA_START):
            return XMLCDATA(scanner.read_between(start = CDATA_START,
                                                 end   = CDATA_END))

    def __get_tag(self,
                  scanner):
        scanner.skip_whitespace()
        try:
            tag = scanner.read_between(start = TAG_START,
                                       end   =TAG_END).strip()
        except StringScannerError:
            scanner.throw(message   = u"Missing or malformed start tag",
                          exception = InvalidXMLElement)

        if tag:
            self.__tag_closed = tag.endswith(u'/')
            if self.__tag_closed:
                self.__self_closing = True
                tag = tag[:-1].strip()
            else:
                self.__self_closing = False

            if u' ' in tag:
                self.tag = tag[0:tag.index(u' ')]
                self.__extract_attributes(tag[tag.index(u' '):])
                self.__extract_namespaces()
            else:
                self.tag = tag

            if u"/" in self.tag:
                scanner.throw(message   = u"Invalid Start Tag ({tag})"
                                          .format(tag = self.tag),
                              exception = InvalidXMLElement)

        self.__get_namespace_key()
        self.__resolve_namespace(self.namespace_key)

        pass  # debug point

    def __detect_end_tag(self,
                         scanner):
        scanner.remember_position()
        if scanner.next_matches(u'</'):
            tag = scanner.read_between(start = u'</',
                                       end   = TAG_END).strip()
            self.__tag_closed = tag in (self.signature,
                                        self.long_signature)
            if not self.__tag_closed:
                scanner.restore_position()
                scanner.throw(exception = XMLSyntaxError,
                              message   = u'Missing end tag for "{signature}"'
                                          .format(signature = self.signature))

    def __get_namespace_key(self):
        tag_parts = self.tag.split(u':')
        namespace = u':'.join(tag_parts[:-1])
        self.namespace_key = namespace if namespace else NAMESPACE
        self.tag = tag_parts[-1]
        pass

    def __resolve_namespace_key(self,
                                namespace_key):
        try:
            return self.__namespaces[namespace_key]
        except KeyError:
            result = self.__parent.__resolve_namespace_key(namespace_key)
        return result

    def __resolve_namespace_value(self,
                                  namespace):
        for key, value in six.iteritems(self.__namespaces):
            if value == namespace:
                return key
        return self.__parent.__resolve_namespace_value(namespace)

    def __resolve_namespace(self,
                            namespace):
        try:
            self.namespace_value = self.__resolve_namespace_key(namespace)
        except AttributeError:
            try:
                key = self.__resolve_namespace_value(namespace)
                self.namespace_key = key
                self.namespace_value = namespace
            except AttributeError:
                if namespace == NAMESPACE:
                    # catch u'xmlns' special case
                    self.namespace_value = namespace
                    return
                message = (u'Unable to resolve namespace:"{namespace}"'
                           .format(namespace=namespace))

                if self.ignore_invalid_namespaces:
                    self.__scanner.log_warning(message)

                else:
                    self.__scanner.throw(exception = XMLSyntaxError,
                                         message   = message)

    def __extract_attributes(self, attributes):
        try:
            self.attributes = extract_attributes(attributes)
        except Exception as e:
            logging.exception(e)
            self.__scanner.throw(u'XML Syntax Error in attributes')

    def __extract_namespaces(self):
        for attr in self.attributes:
            try:
                namespace_indicator, namespace_name = attr.split(u':')
                if namespace_indicator == NAMESPACE:
                    self.__namespaces[namespace_name] = self.attributes[attr]
            except ValueError:
                if attr == NAMESPACE:
                    self.__namespaces[NAMESPACE] = self.attributes[attr]
                # else: attribute is not a namespace

    u"""          ┌─────────────────────┐
                  │   Other Private     │
                  └─────────────────────┘           """

    def __find(self,
               path,
               value=None):
        """
        path should be a Python list of tags
        a value to match may also be specified
        e.g. find(['MediaRequest','TranscodeAsset'],'True')
        """
        try:
            path = normalise_element_path(path)
        except TypeError:
            raise BadSearchCriteria(path)

        if len(path) == 1:
            # at a leaf node
            if self.element_match(path[0]):
                if value:
                    if value == self.__value:
                        return [self]
                else:
                    return [self]

        else:
            if self.element_match(path[0]):

                found_children = []
                for child in self.__children:
                    if isinstance(child, XML):
                        try:
                            found = child.__find(path=path[1:],
                                                 value=value)
                            found_children.extend(found)
                        except XMLElementNotFound:
                            pass

                if found_children:
                    return found_children

        raise XMLElementNotFound(path)

    u"""          ┌───────────────────┐
                  │    Properties     │
                  └───────────────────┘           """

    @property
    def signature(self):
        if self.namespace_key == NAMESPACE:
            return self.tag
        return (u'{namespace}:{tag}'
                .format(namespace=self.namespace_key,
                        tag=self.tag))

    @property
    def long_signature(self):
        if self.namespace_value:
            return (u'{namespace}:{tag}'
                    .format(namespace = self.namespace_value,
                            tag       = self.tag))
        else:
            return self.tag

    @property
    def has_children(self):
        return self.__children != []

    @property
    def has_child_elements(self):
        return [child
                for child in self.__children
                if child.__class__ == XML] != []

    def element_match(self,
                      signature):
        element_to_match = XML(u"{tag_start}{signature}/{tag_end}"
                               .format(tag_start = TAG_START,
                                       signature = signature,
                                       tag_end   = TAG_END),
                               parent = self)
        if element_to_match.tag != self.tag or \
           element_to_match.namespace_value != self.namespace_value:
            return False

        for a_key, a_val in six.iteritems(element_to_match.attributes):
            if self.attributes.get(a_key, None) != a_val:
                return False
        return True

    @property
    def xml_is_valid(self):
        valid = self.__tag_closed
        for child in self.__children:
           if child.__class__ == XML:
              valid = valid and child.xml_is_valid()
        return valid

    u"""          ┌───────────────────┐
                  │      Public       │
                  └───────────────────┘           """

    def remove(self,
               path,
               value = None):
        """
        Removes the element at path with value
        :param path: path to existing element
        :param value: value to match (useful to narrow down an individual element)
        """
        children = self.__find(path, value)
        for child in children:
            # remove element from list
            # TODO: Not sure why this is missing
            #       guessing at del child
            del child

    def add_element(self,
                    xml):
        """
        Adds an element to the element's children

        :param xml: XMLElement object or a string containing the XML fragment
        """
        if not isinstance(xml, XML):
            xml = XML(xml,
                      parent = self)
        self.__children.append(xml)

    def add_at_path(self,
                    xml,
                    path,
                    value = None):
        """
        Adds an element to the children at the given path
        :param xml: XML object or a string containing the XML fragment
        :param path:
        :param value:
        :return:
        """
        parents = self.__find(path,
                              value)
        if len(parents) > 1:
            raise XMLTooManyElementsFound(path = path)

        parents[0].add_element(xml)

    def replace(self,
                 xml,
                 path,
                 value = None):
        """
        Replaces the element at path with the new element
        :param new: new element
        :param path: path to existing element
        :param value: value to match (useful to narrow down a particular element)
        """
        path = normalise_element_path(path=path)
        parent = path[:-1]
        self.remove(path,
                    value)
        self.add_at_path(parent,
                         xml)

    @property
    def value(self):
        return u'\n'.join([unicode(child)
                           for child in self.__children
                           if isinstance(child, basestring)
                           or isinstance(child, XMLCDATA)])

    @value.setter
    def value(self,
              value):

        non_value_children = [unicode(child)
                              for child in self.__children
                              if isinstance(child, XMLComment)
                              or isinstance(child, XMLComment)]
        self.__children = []

        value_scanner = StringScanner(value)
        self.__value = False
        while not value_scanner.eos:
            self.__extract_value(value_scanner)

            cdata = self.__extract_CDATA(value_scanner)
            if cdata:
                self.__children.append(cdata)
                continue

            self.__extract_value(value_scanner)

            comment = self.__extract_comment(value_scanner)
            if comment:
               self.__children.append(comment)

        self.__children.extend(non_value_children)

    def replace_value_at_path(self,
                              new_value,
                              path,
                              value = None):

        nodes = self.__find(path = path,
                           value = value)
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node in nodes:
            node.__value = new_value

    def set_attribute(self,
                      key,
                      value):
        self.attributes[key] = value

    def find(self,
             path,
             value          = None,
             attribute      = None,
             parent         = None,
             find_in_result = None):
        u"""
        :param path: : Describes the path to the node of the XML tree
                          e.g. <MediaRequest><VersionNumber>
                          Attributes may also be added, which can help
                          narrow the search when there are many elements
                          of the same type at the same level.
                          e.g. <MediaRequest><AudioTrack trackNumber="1">
        :param value: Only nodes with this value will be matched.
                         This is useful for checking that a value
                         is present.
        :param attribute: If a particular attribute of an element is
                         what we're interested in rather than the
                         whole element, then the named attribute
                         value is returned.
        :param parent: integer number of levels to back up
        :param find_in_result: a dictionary of the above parameters to search further
        :return: XML or list of XMLs

        E.g. for the following XML
             <MediaRequest OriginatingSystem="OSCAR">
                 <VersionNumber>12345</VersionNumber>
                 <AudioTrack TrackNumber="1">
                     <Level>-23</Level>
                 </AudioTrack>
                 <AudioTrack TrackNumber="2">
                     <Level>-23</Level>
                 </AudioTrack>
             <MediaRequest>

        element:'<MediaRequest><AudioTrack trackNumber="1">'
        return : the element for
                 <AudioTrack TrackNumber="1">
                     <Level>-23</Level>
                 </AudioTrack>

        element:'<MediaRequest><VersionNumber>'},
        value  :'12345')
        return : the element for <VersionNumber>12345</VersionNumber>

        element  :'<MediaRequest>'
        attribute:'OriginatingSystem'})
        return   :"OSCAR"

        """
        hits = self.__find(path  = path,
                           value = value)

        if attribute is not None:
            hits = [path.attributes[attribute]
                    for path in hits
                    if attribute in path.attributes]

        if parent is not None:
            for _ in range(parent):
                hits = [hit.parent for hit in hits]

        if find_in_result is not None:
            hits = hits.find(**find_in_result)

        if not hits:
            raise XMLElementNotFound(path = path)

        return hits

    def exists(self,
               **search_criteria):
        try:
            self.find(**search_criteria)
            return True
        except XMLElementNotFound:
            return False

    u"""        ┌─────────────────────┐
                │    Representations  │
                └─────────────────────┘           """


    def __dictionary(self,
                     include_first_tag = True,
                     attribute_indicator = u'@'):
        """
        (u'<?xml version = "1.0" encoding = "UTF-8"?>
        <MediaRequest OriginatingSystem="OSCAR" attribute2="OSCAR">
            <VersionNumber>12345</VersionNumber>
            <AudioTrack TrackNumber="1">
                <Level someattr="x">-1</Level>
            </AudioTrack>
            <AudioTrack TrackNumber="2">
                <Level>-2</Level>
            </AudioTrack>
            <AudioTrack TrackNumber="3">
                <Level>-3</Level>
            </AudioTrack>
        </MediaRequest>

        Converts to:

        {'@OriginatingSystem': u'OSCAR',
         '@attribute2': u'OSCAR',
         u'AudioTrack': [{'@TrackNumber': u'1',
                          u'Level': {'@someattr': u'x', u'Level': u'-1'}},
                         {'@TrackNumber': u'2', u'Level': u'-2'},
                         {'@TrackNumber': u'3', u'Level': u'-3'}],
         u'VersionNumber': u'12345'}

        etc
        """
        d = {}
        for child in [child
                      for child in self.__children
                      if child.__class__ is XML]:
            child_signature = child.signature
            if child_signature in d:
                # Already have this tag
                if isinstance(d[child_signature], list):
                    # Already have a list for this signature, append it
                    child_to_add = \
                        child.__dictionary(
                            include_first_tag   = False,
                            attribute_indicator = attribute_indicator)
                    d[child_signature].append(child_to_add)
                else:
                    # 2nd instance of this tag, convert to a list
                    d[child_signature] = \
                        [d[child_signature],
                         child.__dictionary(
                                 include_first_tag   = False,
                                 attribute_indicator = attribute_indicator)]
            else:
                # 1st instance of this tag
                d[child_signature] = \
                    child.__dictionary(
                        include_first_tag   = False,
                        attribute_indicator = attribute_indicator)

        d.update({u'{attr}{key}'.format(attr = attribute_indicator,
                                        key = key) : value
                  for key, value in six.iteritems(self.attributes)})

        if self.__value is not None:
            if d:
                d[self.tag] = self.__value
            else:
                d = self.__value

        if include_first_tag:
            d = {self.tag: d}
            if self.declaration:
                d[u'?xml'] = self.declaration.attributes

        return d

    @property
    def dictionary(self):
        return self.__dictionary(attribute_indicator = u'@')

    def __str__(self):
        return unicode(self).encode(u'utf-8')

    def __unicode__(self):
        return self.__unicode()

    def __unicode(self,
                  depth  = 0,
                  parts = None):

        tag = self.tag
        indent = INDENT * depth
        newline_indent = u'\n' + indent
        parts = [] if parts is None else parts
        value_on_new_line = False

        if self.declaration and depth == 0:
            parts += unicode(self.declaration)

        for comment in self.__leading_comments:
            parts.extend([newline_indent, unicode(comment)])

        signature = self.signature
        parts.extend([newline_indent,
                      u'<',
                      signature])

        if self.attributes:
            attributes = dictionary_to_attributes_strings(self.attributes)

            width_of_tag_and_attributes = sum([len(attribute)
                                               for attribute in attributes]
                                              ) + len(signature) + 2

            if width_of_tag_and_attributes > TAG_SPLIT_LIMIT:
                indent = u''.join([newline_indent, u' ' * (len(signature) + 2)])
                parts.extend([u' ', indent.join(attributes)])
                value_on_new_line = True

            elif width_of_tag_and_attributes > LINE_SPLIT_LIMIT:
                indent = u''.join([newline_indent, u' ' * (len(signature) + 2)])
                parts.extend([indent, u' '.join(attributes)])
                value_on_new_line = True
            else:
                parts.extend([u' ',u' '.join(attributes)])

        parts += (u'/>'
                  if self.__self_closing
                  else u'>')

        indent = newline_indent + INDENT if value_on_new_line else u''

        for child in self.__children:

            if isinstance(child, XMLComment):
                parts.extend([indent, unicode(child)])
                value_on_new_line = True

            elif isinstance(child, XML):
                child.__unicode(depth = depth + 1,
                                parts = parts)
                value_on_new_line = True

            elif isinstance(child, XMLCDATA):
                value_on_new_line = True
                parts.extend([indent, unicode(child)])

            elif isinstance(child, basestring):
                parts.extend([indent, unicode(child)])

        # Todo: Comment this
        if not self.__self_closing:
            parts.extend([newline_indent
                          if value_on_new_line
                          and not (newline_indent == parts[-len(newline_indent):]
                                   or parts[-1] == u'\n')
                          else u'',
                               u'</',
                               signature,
                               u'>'])

        for comment in self.__trailing_comments:
            parts.extend([newline_indent, unicode(comment)])

        if depth == 0:
            return u''.join(parts)


    def write(self,
              filename):
        f = UTF8File(filename, mode=u'w')

        if not self.declaration:
            f.writeln(STANDARD_XML_DECLARATION)

        f.write(unicode(self))


def XMLSubsetString(subset):

    returnString = u""

    if isinstance(subset, list):
        for element in subset:
            returnString += XMLSubsetString(element)

    elif isinstance(subset, dict):
        for element in subset:
            if element != None:
                returnString += (u"Match for %s:\n%s\n"
                                 % (element, XMLSubsetString(subset[element])))
            else:
                returnString += u"No match for %s\n"%(element)
    elif isinstance(subset, XML):
        returnString += unicode(subset) + u'\n'
    elif subset == None:
        returnString += u"No Matching Element\n"
    else:
        returnString += u"%s\n"%subset
    return returnString


u"""        ┌────────────────────────────────────────┐
            │               __main__                 │
            │                                        │
            │ Move code below here into unit tests.  │
            │                                        │
            │ Use for temporary adhoc tests.         │
            └────────────────────────────────────────┘           """

if __name__ == u'__main__':
    import pprint

    x = XML(u"""<?xml version="1.0"?>
<!--Comment 1-->
<A>
    1234<![CDATA[[this is <some>
cdata!'"]]>
<!--Comment 2-->
    <B>5678</B>
    <C>6789</C>
<!--Comment 3-->
</A><!--Comment 4-->
""")
    print(unicode(x))
    pprint.pprint(x.dictionary)
    print unicode(XML(u"""<?xml version="1.0"?>
<!--Comment 1-->
<PSLinput version="20160510211557"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns="urn:NNDS:CAB:SIMetadata:PermanentSeriesLink:Input:v1"
          xsi:schemaLocation="urn:NNDS:CAB:SIMetadata:PermanentSeriesLink:Input:v1 PermanentSeriesInput.xsd">
    <permanentSeason ui_descr="b Season 1"
                     permanent_season_id="145693">
                     1 1 1
    </permanentSeason>
    <permanentSeason ui_descr="b Season 1"
                     permanent_season_id="145693">
                     2 2 2
<![CDATA[[ <cdata1>]]>
<!--Comment 2-->
<![CDATA[[ 'cdata2']]>
<!--Comment 3-->
<![CDATA[[ "cdata 4 ]]> 3 3 3
    </permanentSeason>
</PSLinput>"""))


    XML(u"""<bookEvent service_key   = "2002"
                       event_id      = "1"
                       nominal_start = "2016-05-11T10:00:00Z"
                       /><!-- Channel:101, Time: 2016-05-11T10:00:00Z (57519.4166667) -->""")

    u'xmlns = "urn:NNDS:CAB:SIMetadata:PermanentSeriesLink:Input:v1"'
    import pprint

    print XML(u"""<?xml version="1.0"?>
<PSLinput version="20160510211557"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns="urn:NNDS:CAB:SIMetadata:PermanentSeriesLink:Input:v1"
          xsi:schemaLocation="urn:NNDS:CAB:SIMetadata:PermanentSeriesLink:Input:v1 PermanentSeriesInput.xsd">
    <permanentSeason ui_descr="b Season 1"
                     permanent_season_id="145693">
        <currentSeason last_season="false" xmlns:test="test:of:namespace">
            <test:title lang="eng" use="show">b</test:title>
            <test:of:namespace:title lang="eng" use="season">b: b Season 1</test:of:namespace:title>
            <test:seriesChain  series_id="123"/>
            <seriesChain  series_id="432"/>
        </currentSeason>
        <bookEvent service_key="2002"
                   event_id="555"
                   nominal_start="2016-05-10T11:00:00Z"/>
        <!-- Channel:101, Time: 2016-05-10T11:00:00Z (57518.4583333) -->
        <bookEvent service_key="2002"
                   event_id="1356"
                   nominal_start="2016-05-10T10:00:00Z"/>
        <!-- Channel:101, Time: 2016-05-10T10:00:00Z (57518.4166667) -->
    </permanentSeason>
    <permanentSeason ui_descr="b Season 2"
                     permanent_season_id="145694">
        <currentSeason  last_season="false">
            <title  lang="eng" use="show">b</title>
            <title  lang="eng" use="season">b: b Season 2</title>
        </currentSeason>
    </permanentSeason>
</PSLinput>""")




    someXMLDeclaration = u"""<?xml version="1.0" encoding="UTF-8"?>
    <tns:MediaRequest xmlns:tns="http://rsi.com/mediarequest">
    	<tns:MediaId>MediaId</tns:MediaId>
    </tns:MediaRequest>"""
    print XML(someXMLDeclaration)
    import pprint
    pprint.pprint(XML(someXMLDeclaration).dictionary)

    someXMLDeclaration = u'<?xml version="1.0"         encoding="utf-8" ?> '
    print XMLDeclaration(StringScanner(someXMLDeclaration))

    someXMLDeclaration = StringScanner(u"""<?xml version="1.0" encoding="UTF-8"?>
    <tns:MediaRequest xmlns:tns="http://rsi.com/mediarequest">
    	<tns:MediaId>MediaId</tns:MediaId>
    </tns:MediaRequest>""")
    print XMLDeclaration(someXMLDeclaration)