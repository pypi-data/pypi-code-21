
import os
import logging_helper
import xml.etree.ElementTree as ETree

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'

logging = logging_helper.setup_logging()

AVAILABLE_TYPES = [u'dict']


def _xml_to_dict(element):

    """ Convert XML Element to dictionary recursively

    Args:
        element: An xml.etree.ElementTree Element

    Returns: dict

    """

    d = {}

    # Deal with attributes & values for this element
    attributes = element.attrib
    logging.debug(u'attributes: {a}'.format(a=attributes))
    d.update(attributes)

    text = element.text
    logging.debug(u'text: {a}'.format(a=text))

    if text:
        text_pairs = text.strip().split(u'  ')
        logging.debug(u'text_pairs: {a}'.format(a=text_pairs))

        for text_pair in text_pairs:
            if text_pair:

                tp_count = text_pair.count(u'=')

                #logging.debug(u'text_pairs \'=\' count: {a}'.format(a=tp_count))

                # TODO: Add handling of key value pairs & separate test values in the element value
                # Multiple Key value pairs found in element value
                if tp_count > 1:
                    for t in text_pair.split(u' '):
                        logging.debug(t)
                        key, value = t.split(u'=', 1)
                        d[key] = value

                # One Key value pairs found in element value
                elif tp_count == 1:
                    key, value = text_pair.split(u'=', 1)
                    d[key] = value

                # No Key value pairs found in element value
                else:
                    d[u'element_value'] = text_pair

    # Deal with nested elements for this element
    for i in element:
        if i.tag not in d:
            d[i.tag] = _xml_to_dict(i)

        else:
            if type(d.get(i.tag)) == list:
                d[i.tag].append(_xml_to_dict(i))

            else:
                d[i.tag] = [d.get(i.tag), _xml_to_dict(i)]

    return d


def parse_xml(xml_string,
              output_type=u'dict',
              unbound_prefixes=None):

    """ Parse XML into requested format

    Args:
        xml_string:  xml string to be converted
        output_type: The output type expected, currently available:
                        dict
        unbound_prefixes: List of prefixes to remove from xml

    Returns: parsed xml

    """

    logging.debug(xml_string)

    if unbound_prefixes is None:
        unbound_prefixes = []

    # Deal with unbound prefixes
    for prefix in unbound_prefixes:
        xml_string = xml_string.replace(prefix, u'')

    logging.debug(xml_string)

    tree = ETree.XML(xml_string)

    if output_type in AVAILABLE_TYPES:

        function = eval(u'_xml_to_{t}'.format(t=output_type))

        output = function(tree)

        return output

    else:
        raise LookupError(u'output_type ({t}) not in available types!'.format(t=output_type))


def format_element_tree(elem,
                        level=0):

    """ Format Element Tree recursively ready for writing to xml file

    :param elem:  root element
    :param level: starting indent level
    """

    spacer = u'    '

    i = u'\n{sp}'.format(sp=level * spacer)

    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + spacer

        if not elem.tail or not elem.tail.strip():
            elem.tail = i

        for elem in elem:
            format_element_tree(elem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i

    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def write_xml_to_file(element_tree,
                      filename,
                      xml_prolog='<?xml version="1.0" encoding="utf-8" standalone="no"?>',
                      xml_doctype=''):

    """ Write XML to file.

    :param element_tree: XML tree to be written
    :param filename:     full XML file path
    :param xml_prolog:   proglog to be used for the XML
    :param xml_doctype:  doctype to be used for the XML
    """

    logging.info(u'Writing XML to {f}'.format(f=filename))

    path, _ = os.path.split(filename)

    if not os.path.exists(path):
        os.makedirs(path)

    format_element_tree(element_tree)

    with open(filename, u'wb') as xml_file:
        xml_file.write(xml_prolog + '\n')

        if xml_doctype:
            xml_file.write(xml_doctype + '\n')

        ETree.ElementTree(element_tree).write(xml_file, encoding='utf-8')

    return filename


def load_xml_file(xml_file,
                  unbound_prefixes=None):

    # Read in the file
    f = open(xml_file, 'r')
    filedata = f.read()
    f.close()

    # Parse XML file
    xml = parse_xml(filedata,
                    unbound_prefixes=unbound_prefixes)

    return xml
