import os
import shutil
import unittest
import xml.etree.ElementTree as ETree

from fdutil import parse_xml


class TestParseXmlGeneral(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))
        self.out_dir = u'{base}{s}test_data{s}parse_xml{s}output{s}'.format(base=self.test_base_dir,
                                                                            s=os.sep)

        self.example_xml = ETree.parse(u'{base}{s}test_data{s}parse_xml{s}test_data.xml'.format(base=self.test_base_dir,
                                                                                                s=os.sep))
        self.example_string = u'<?xml version="1.0" encoding="utf-8"?><test_data><test_id_node id="1">' \
                              u'<content_node>A</content_node><id_content_node id="1.1">ID_A</id_content_node>' \
                              u'</test_id_node></test_data>'

        os.makedirs(self.out_dir)

    def tearDown(self):
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)


class TestXmlToDict(TestParseXmlGeneral):

    def test_xml_to_dict(self):

        output_dict = parse_xml._xml_to_dict(element=ETree.XML(self.example_string))
        self.assertIn(u'test_id_node', output_dict)

        node = output_dict.get(u'test_id_node')
        self.assertIn(u'content_node', node)
        self.assertIn(u'id_content_node', node)
        self.assertIn(u'id', node)

        content_node = node.get(u'content_node')
        id_content_node = node.get(u'id_content_node')
        self.assertEqual(node.get(u'id'), u'1')

        self.assertIn(u'element_value', content_node)
        self.assertEqual(content_node.get(u'element_value'), u'A')

        self.assertIn(u'element_value', id_content_node)
        self.assertEqual(id_content_node.get(u'element_value'), u'ID_A')
        self.assertEqual(id_content_node.get(u'id'), u'1.1')


class TestParseXml(TestParseXmlGeneral):

    def test_parse_xml_defaults(self):

        output_dict = parse_xml.parse_xml(xml_string=self.example_string)

        self.assertIs(type(output_dict), dict)

    def test_parse_xml_bad_output_type(self):
        with self.assertRaises(LookupError):
            parse_xml.parse_xml(xml_string=self.example_string, output_type=u'FAIL_ME')


class TestFormatElementTree(TestParseXmlGeneral):

    def test_format_element_tree_defaults(self):

        element = ETree.XML(self.example_string)
        parse_xml.format_element_tree(element)

        output = ETree.tostring(element, encoding=u'utf8', method=u'xml')

        expected_output = u'<?xml version=\'1.0\' encoding=\'utf8\'?>\n' \
                          u'<test_data>\n' \
                          u'    <test_id_node id="1">\n' \
                          u'        <content_node>A</content_node>\n' \
                          u'        <id_content_node id="1.1">ID_A</id_content_node>\n' \
                          u'    </test_id_node>\n' \
                          u'</test_data>\n'

        self.assertEqual(output, expected_output)

    def test_format_element_tree_different_level(self):

        element = ETree.XML(self.example_string)
        parse_xml.format_element_tree(element, level=2)

        output = ETree.tostring(element, encoding=u'utf8', method=u'xml')

        expected_output = u'<?xml version=\'1.0\' encoding=\'utf8\'?>\n' \
                          u'<test_data>\n' \
                          u'            <test_id_node id="1">\n' \
                          u'                <content_node>A</content_node>\n' \
                          u'                <id_content_node id="1.1">ID_A</id_content_node>\n' \
                          u'            </test_id_node>\n' \
                          u'        </test_data>\n' \
                          u'        '

        self.assertEqual(output, expected_output)


class TestWriteXmlToFile(TestParseXmlGeneral):

    def test_write_xml_to_file_defaults(self):

        parse_xml.write_xml_to_file(element_tree=self.example_xml.getroot(),
                                    filename=os.path.join(self.out_dir, u'example_output.xml'))

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.xml')))

    def test_write_xml_to_file_prolog(self):

        xml_prolog = u'<?xml version="1.0"?>'

        parse_xml.write_xml_to_file(element_tree=self.example_xml.getroot(),
                                    filename=os.path.join(self.out_dir, u'example_output.xml'),
                                    xml_prolog=xml_prolog)

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.xml')))

        with open(os.path.join(self.out_dir, u'example_output.xml')) as f:
            prolog_line = f.readline().replace(u'\n', u'')
            self.assertEqual(prolog_line, xml_prolog)

    def test_write_xml_to_file_doctype(self):

        xml_doctype = u'<!DOCTYPE test_data SYSTEM "test.dtd">'

        parse_xml.write_xml_to_file(element_tree=self.example_xml.getroot(),
                                    filename=os.path.join(self.out_dir, u'example_output.xml'),
                                    xml_doctype=xml_doctype)

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.xml')))

        with open(os.path.join(self.out_dir, u'example_output.xml')) as f:
            f.readline().replace(u'\n', u'')  # Read the prolog line
            doctype_line = f.readline().replace(u'\n', u'')

            self.assertEqual(doctype_line, xml_doctype)
