import unittest
from mock import patch
import wsgi_intercept
import wsgi_intercept.mechanize_intercept
from zope_wsgi import WsgiApp, css, csstext, parse_html
import mock_db

try:
    import simplejson as json
except ImportError:
    import json


class BrowserTest(unittest.TestCase):
    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod

        self.method = ZSPARQLMethod('sq', "Test Method", "")
        self.method.endpoint_url = "http://cr.eionet.europa.eu/sparql"
        self.method.query = mock_db.GET_LANG_BY_NAME
        self.method.arg_spec = u"lang_name:string"

        self.app = WsgiApp(self.method)

        wsgi_intercept.add_wsgi_intercept('test', 80, lambda: self.app)
        self.browser = wsgi_intercept.mechanize_intercept.Browser()

        self.validate_patch = patch('AccessControl.SecurityManagement'
                                    '.SecurityManager.validate')
        self.validate_patch.start().return_value = True

        self.mock_db = mock_db.MockSparql()
        self.mock_db.start()


    def tearDown(self):
        self.mock_db.stop()
        self.validate_patch.stop()
        wsgi_intercept.remove_wsgi_intercept('test', 80)

    def test_manage_edit(self):
        br = self.browser
        br.open('http://test/manage_edit_html')
        br.select_form(name='edit-method')
        br['title:utf8:ustring'] = "My awesome method"
        br['endpoint_url:utf8:ustring'] = "http://dbpedia.org/sparql"
        br['query:utf8:ustring'] = "New query value"
        br['arg_spec:utf8:ustring'] = "confirm:boolean"
        br.submit()

        self.assertEqual(self.method.title, "My awesome method")
        self.assertEqual(self.method.endpoint_url, "http://dbpedia.org/sparql")
        self.assertEqual(self.method.query, "New query value")
        self.assertEqual(self.method.arg_spec, "confirm:boolean")

    def test_query_test_page(self):
        self.method.query = mock_db.GET_LANG_NAMES
        self.method.arg_spec = u""
        br = self.browser

        self.mock_db.stop()
        page = parse_html(br.open('http://test/test_html').read())
        self.mock_db.start()
        table = css(page, 'table.sparql-results')[0]

        table_headings = [e.text for e in css(table, 'thead th')]
        self.assertEqual(table_headings, ['lang_url', 'name'])

        table_data = [[td.text for td in css(tr, 'td')]
                      for tr in css(table, 'tbody tr')]
        self.assertEqual(len(table_data), 45)
        lang_da_url = 'http://rdfdata.eionet.europa.eu/eea/languages/da'
        self.assertEqual(table_data[7], ['<'+lang_da_url+'>', '"Danish"@en'])

    def test_with_literal_argument(self):
        br = self.browser
        br.open('http://test/test_html')
        br.select_form(name='method-arguments')
        br['lang_name:utf8:ustring'] = "Danish"

        self.mock_db.stop()
        page = parse_html(br.submit().read())

        self.mock_db.start()
        self.assertEqual(csstext(page, 'table.sparql-results tbody td'),
                         u"<http://rdfdata.eionet.europa.eu/eea/languages/da>")

    def test_autofill_submitted_argument(self):
        br = self.browser
        br.open('http://test/test_html')
        br.select_form(name='method-arguments')
        br['lang_name:utf8:ustring'] = "Danish"
        br.submit()

        br.select_form(name='method-arguments')
        self.assertEqual(br['lang_name:utf8:ustring'], "Danish")

    def test_REST_query(self):
        from webob import Request
        import sparql
        from test_method import EIONET_RDF

        req = Request.blank('http://test/?lang_name=Danish')
        self.mock_db.stop()
        response = req.get_response(self.app)
        self.mock_db.start()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_response = json.loads(response.body)
        danish_iri = sparql.IRI(EIONET_RDF+'/languages/da')
        self.assertEqual(json_response['rows'], [[danish_iri.n3()]])
