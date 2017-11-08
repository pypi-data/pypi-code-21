from eventlet.green import urllib2
from os import path
from mock import patch
import tempfile

GET_LANGS = """\
SELECT ?lang_url WHERE {
  ?lang_url a <http://rdfdata.eionet.europa.eu/eea/ontology/Language> .
}
"""

GET_LANG_NAMES = """\
PREFIX eea_ontology: <http://rdfdata.eionet.europa.eu/eea/ontology/>
SELECT * WHERE {
  ?lang_url a eea_ontology:Language .
  ?lang_url eea_ontology:name ?name .
  FILTER (lang(?name) = "en") .
}
"""

GET_LANG_BY_NAME = """\
PREFIX eea_ontology: <http://rdfdata.eionet.europa.eu/eea/ontology/>
PREFIX rdf_schema: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?lang_url WHERE {
  ?lang_url a eea_ontology:Language .
  ?lang_url rdf_schema:label ?lang_label .
FILTER (?lang_label = ${lang_name})
}
"""

GET_LANG_BY_NAME_DA = GET_LANG_BY_NAME.replace('${lang_name}', '"Danish"')

def pack(q):
    return q.replace("\n", " ").encode('utf-8')

def read_response_xml(name):
    xml_path = path.join(path.dirname(__file__), 'sparql-%s.xml' % name)
    f = open(xml_path, 'rb')
    data = f.read()
    f.close()
    return data

QUERIES = {
        pack(GET_LANGS): read_response_xml('get_languages'),
        pack(GET_LANG_NAMES): read_response_xml('get_lang_names'),
        pack(GET_LANG_BY_NAME_DA): read_response_xml('get_lang_by_name-da'),
    }

class MockCurl(object):
    def setopt(self, opt, value):
        buf = tempfile.NamedTemporaryFile()
        if opt == buf.write:
            self.writefunction = value
        if opt == urllib2.urlopen:
            self.url = value

    def perform(self):
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        querystring = self.url.split('?', 1)[1]
        query = parse_qs(querystring).get('query', [''])[0]

        self.writefunction(QUERIES[query])
        return

    def getinfo(self, info):
        return 200

class MockSparql(object):
    def start(self):
        self.pycurl_patch = patch('sparql.query')
        mock_pycurl = self.pycurl_patch.start()
        mock_pycurl.Curl = self.mock_Curl
        buf = tempfile.NamedTemporaryFile()
        mock_pycurl.WRITEFUNCTION = buf.write
        mock_pycurl.URL = urllib2.urlopen

    def stop(self):
        self.pycurl_patch.stop()

    def mock_Curl(self):
        return MockCurl()
