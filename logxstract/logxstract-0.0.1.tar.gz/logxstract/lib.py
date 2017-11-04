# -*- coding:utf-8 -*-

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


from lxml import etree


OPTIONS = [
    (('-p', '--path'), {'help': 'xml contains xpath criteria will be extracted', 'type': str}),
    (('-b', '--body'), {'help': 'xpath element to extract when matching is found', 'type': str}),
    (('-f', '--file'),  {'help': 'input file', 'type': str}),
    (('-o', '--output'),  {'help': 'output file', 'type': str}),
    (('-e', '--encoding'),  {'help': 'output xml encoding (iso-8859-2, utf-8, ..)', 'type': str})
]


def add_arguments(parser):
    for option, kwargs in OPTIONS:
        parser.add_argument(*option, **kwargs)


def get_xml_lines(file):
    xml_lines = []
    with open(file) as logfile:
        for line in logfile:
            line = line.strip()
            if line.startswith('<?xml'):
                line = '<break/>'
                xml_lines.append(line)
            elif line.startswith('<'):
                xml_lines.append(line)
    return xml_lines


def make_xml_list(file):
    return (xml for xml in ''.join(get_xml_lines(file)).split('<break/>'))


def encode_reply(reply):
    try:
        return reply.decode('utf-8')
    except AttributeError:
        return reply


def extract_xml_from_file(path=None, body=None, input_file=None, output_file=None, encoding=None):
    encoding = encoding or 'iso-8859-2'

    with open(output_file, 'ab') as output:
        for xml in make_xml_list(input_file):

            try:
                root = etree.parse(StringIO(encode_reply(xml)))
            except etree.XMLSyntaxError:
                continue

            found = root.xpath(path)

            if found:
                reply_tag = root.xpath(body)

                if reply_tag:
                    output.write(etree.tostring(
                        root,
                        encoding=encoding,
                        xml_declaration=True,
                        pretty_print=True
                    ))
