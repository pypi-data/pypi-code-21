import unittest
from mock import Mock, patch
import mock_db

import sparql

from Products.ZSPARQLMethod.Method import QueryTimeout


EIONET_RDF = 'http://rdfdata.eionet.europa.eu/eea'
SPARQL_URL = "http://cr.eionet.europa.eu/sparql"

def _mock_request():
    mock_request = Mock()
    mock_request.form = dict((k,'') for k in [
        'title', 'endpoint_url', 'timeout', 'query', 'arg_spec'])
    mock_request.SESSION = {}
    return mock_request

class SimpleMockResult(object):
    def __init__(self, variables, rows):
        self.variables = variables
        self.rows = rows
        self._hasResult = True

    def fetchall(self):
        return self.rows

class QueryTest(unittest.TestCase):
    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod
        self.method = ZSPARQLMethod('sq', "Test Method", SPARQL_URL)
        self.mock_db = mock_db.MockSparql()
        self.mock_db.start()

    def tearDown(self):
        self.mock_db.stop()

    def test_simple_query(self):
        from sparql import IRI
        self.mock_db.stop()
        self.method.query = mock_db.GET_LANGS
        result = self.method.execute()

        self.mock_db.start()
        self.assertEqual(result['result']['rows'], [
            (IRI(EIONET_RDF + '/languages/az'),),
            (IRI(EIONET_RDF + '/languages/be'),),
            (IRI(EIONET_RDF + '/languages/bg'),),
            (IRI(EIONET_RDF + '/languages/bs'),),
            (IRI(EIONET_RDF + '/languages/cs'),),
            (IRI(EIONET_RDF + '/languages/da'),),
            (IRI(EIONET_RDF + '/languages/de'),),
            (IRI(EIONET_RDF + '/languages/el'),),
            (IRI(EIONET_RDF + '/languages/en'),),
            (IRI(EIONET_RDF + '/languages/es'),),
            (IRI(EIONET_RDF + '/languages/et'),),
            (IRI(EIONET_RDF + '/languages/fi'),),
            (IRI(EIONET_RDF + '/languages/fr'),),
            (IRI(EIONET_RDF + '/languages/ga'),),
            (IRI(EIONET_RDF + '/languages/hr'),),
            (IRI(EIONET_RDF + '/languages/hu'),),
            (IRI(EIONET_RDF + '/languages/hy'),),
            (IRI(EIONET_RDF + '/languages/is'),),
            (IRI(EIONET_RDF + '/languages/it'),),
            (IRI(EIONET_RDF + '/languages/ka'),),
            (IRI(EIONET_RDF + '/languages/kk'),),
            (IRI(EIONET_RDF + '/languages/lb'),),
            (IRI(EIONET_RDF + '/languages/lt'),),
            (IRI(EIONET_RDF + '/languages/lv'),),
            (IRI(EIONET_RDF + '/languages/me'),),
            (IRI(EIONET_RDF + '/languages/mk'),),
            (IRI(EIONET_RDF + '/languages/mt'),),
            (IRI(EIONET_RDF + '/languages/nl'),),
            (IRI(EIONET_RDF + '/languages/no'),),
            (IRI(EIONET_RDF + '/languages/pl'),),
            (IRI(EIONET_RDF + '/languages/pt'),),
            (IRI(EIONET_RDF + '/languages/rm'),),
            (IRI(EIONET_RDF + '/languages/ro'),),
            (IRI(EIONET_RDF + '/languages/ru'),),
            (IRI(EIONET_RDF + '/languages/sk'),),
            (IRI(EIONET_RDF + '/languages/sl'),),
            (IRI(EIONET_RDF + '/languages/sq'),),
            (IRI(EIONET_RDF + '/languages/sr'),),
            (IRI(EIONET_RDF + '/languages/sv'),),
            (IRI(EIONET_RDF + '/languages/tr'),),
            (IRI(EIONET_RDF + '/languages/uk'),),
            (IRI(EIONET_RDF + '/languages/ca'),),
            (IRI(EIONET_RDF + '/languages/ky'),),
            (IRI(EIONET_RDF + '/languages/tg'),),
            (IRI(EIONET_RDF + '/languages/tk'),),
        ])

    @patch('Products.ZSPARQLMethod.Method.sparql')
    def test_timeout(self, mock_pycurl):
        class MockCurl(object):
            def perform(self):
                import sparql
                raise sparql.SparqlException(28, "timeout")

            def setopt(self, value, opt):
                pass

        def mock_Curl():
            return MockCurl()

        mock_pycurl.Curl = mock_Curl
        self.method.query = mock_db.GET_LANGS
        mock_pycurl.query.side_effect = QueryTimeout

        result = self.method.execute()
        if QueryTimeout.__name__ not in result['exception']:
            raise self.failureException, "%s not raised" % QueryTimeout.__name__

    @patch('Products.ZSPARQLMethod.Method.sparql')
    def test_error(self, mock_sparql):
        self.method.query = mock_db.GET_LANGS
        class MyError(Exception): pass
        mock_sparql.query.side_effect = MyError

        result = self.method.execute()
        if MyError.__name__ not in result['exception']:
            raise self.failureException, "%s not raised" % MyError.__name__

    def test_query_with_arguments(self):
        self.mock_db.stop()
        self.method.query = mock_db.GET_LANG_BY_NAME

        result = self.method.execute(lang_name=sparql.Literal("Danish"))

        danish_iri = sparql.IRI(EIONET_RDF+'/languages/da')
        self.mock_db.start()

        self.assertEqual(result['result']['rows'], [(danish_iri,)])

    def test_call(self):
        self.mock_db.stop()
        self.method.query = mock_db.GET_LANG_BY_NAME
        self.method.arg_spec = u"lang_name:n3term"
        result = self.method(lang_name='"Danish"')

        self.mock_db.start()
        self.assertEqual(result[0], [EIONET_RDF+'/languages/da'])


class MapArgumentsTest(unittest.TestCase):

    def _test(self, raw_arg_spec, arg_data, expected):
        from Products.ZSPARQLMethod.Method import map_arg_values, parse_arg_spec
        missing, result = map_arg_values(parse_arg_spec(raw_arg_spec), arg_data)
        self.assertEqual(missing, [])
        self.assertEqual(result, expected)
        self.assertEqual(map(type, result.values()),
                         map(type, expected.values()))

    def test_map_zero(self):
        self._test(u'', (), {})

    def test_map_one_iri(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:iri',
                   {'lang_url': en},
                   {'lang_url': sparql.IRI(en)})

    def test_map_one_parsed_iri(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'lang_url:n3term',
                   {'lang_url': '<%s>' % en},
                   {'lang_url': sparql.IRI(en)})

    def test_map_one_literal(self):
        self._test(u'name:string',
                   {'name': u"Joe"},
                   {'name': sparql.Literal(u"Joe")})

    def test_map_one_float(self):
        self._test(u'lang_url:float',
                   {'lang_url': '1.23'},
                   {'lang_url': sparql.Literal('1.23', sparql.XSD_FLOAT)})

    def test_map_one_parsed_typed_literal(self):
        self._test(u'lang_url:n3term',
                   {'lang_url': '"12:33"^^<'+sparql.XSD_TIME+'>'},
                   {'lang_url': sparql.Literal('12:33', sparql.XSD_TIME)})

    def test_map_two_values(self):
        en = EIONET_RDF + '/languages/en'
        self._test(u'name:string lang_url:n3term',
                   {'name': u"Joe", 'lang_url': '<%s>' % en},
                   {'name': sparql.Literal(u"Joe"),
                    'lang_url': sparql.IRI(en)})

class InterpolateQueryTest(unittest.TestCase):

    def _test(self, query_spec, var_data, expected):
        from Products.ZSPARQLMethod.Method import interpolate_query
        result = interpolate_query(query_spec, var_data)
        self.assertEqual(result, expected)

    def test_no_variables(self):
        self._test(u"SELECT * WHERE { ?s ?p ?u }",
                   {},
                   u"SELECT * WHERE { ?s ?p ?u }")

    def test_one_iri(self):
        onto_name = EIONET_RDF + '/ontology/name'
        self._test(u'SELECT * WHERE { ?s ${pred} "Joe" }',
                   {'pred': sparql.IRI(onto_name)},
                   u'SELECT * WHERE { ?s <%s> "Joe" }' % onto_name)

    def test_one_literal(self):
        self._test(u"SELECT * WHERE { ?s ?p ${value} }",
                   {'value': sparql.Literal("Joe")},
                   u'SELECT * WHERE { ?s ?p "Joe" }')

class CachingTest(unittest.TestCase):

    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod
        self.method = ZSPARQLMethod('sq', "Test Method", SPARQL_URL)

        from Products.StandardCacheManagers.RAMCacheManager import RAMCache
        self.cache = RAMCache()
        self.cache.__dict__.update({
            'threshold': 100, 'cleanup_interval': 300, 'request_vars': ()})
        self.method.ZCacheable_getCache = Mock(return_value=self.cache)
        self.method.ZCacheable_setManagerId('_cache_for_test')

    def test_invalidate(self):
        self.cache.ZCache_invalidate = Mock()
        self.method.manage_edit(_mock_request())
        self.cache.ZCache_invalidate.assert_called_once_with(self.method)

    @patch('Products.ZSPARQLMethod.Method.query_and_get_result')
    def test_cached_queries(self, mock_query):
        onto_name = EIONET_RDF + '/ontology/name'
        self.method.query = "SELECT * WHERE {$subject <%s> ?value}" % onto_name
        self.method.arg_spec = u"subject:iri"
        mock_query.return_value = {
            'rows': [], 'var_names': [], 'has_result': True}

        self.method(subject=EIONET_RDF + '/languages/en')
        self.method(subject=EIONET_RDF + '/languages/da')
        self.method(subject=EIONET_RDF + '/languages/da')
        self.method(subject=EIONET_RDF + '/languages/en')
        self.method(subject=EIONET_RDF + '/languages/fr')
        self.method(subject=EIONET_RDF + '/languages/fr')
        self.method(subject=EIONET_RDF + '/languages/fr')
        self.method(subject=EIONET_RDF + '/languages/fr')
        self.method(subject=EIONET_RDF + '/languages/da')

        self.assertEqual(len(mock_query.call_args_list), 3)


class ResultsUnpackingTest(unittest.TestCase):

    def setUp(self):
        from Products.ZSPARQLMethod.Method import ZSPARQLMethod
        self.method = ZSPARQLMethod('sq', "Test Method", SPARQL_URL)
        self.method.query = "SELECT ?o WHERE {?s ?p ?o}"

    @patch('Products.ZSPARQLMethod.Method.sparql')
    def do_query(self, sparql_result, mock_sparql):
        mock_sparql.unpack_row = sparql.unpack_row
        mock_sparql.query.return_value = SimpleMockResult(['o'], sparql_result)
        return self.method()

    def test_var_names(self):
        result = self.do_query([ [sparql.Literal("hello")] ])
        self.assertEqual(result.var_names, ["o"])

    def test_getitem(self):
        result = self.do_query([ [sparql.Literal("hello")] ])
        self.assertEqual(result[0][0], "hello")

    def test_iter(self):
        result = self.do_query([ [sparql.Literal("hello")] ])
        self.assertEqual(iter(result).next()[0], "hello")

    def test_length(self):
        result = self.do_query([
            [sparql.Literal("tomato")],
            [sparql.Literal("apple")],
        ])
        self.assertEqual(len(result), 2)

    def test_float(self):
        result = self.do_query([
            [sparql.Literal("13.5", sparql.XSD_FLOAT)],
        ])

        value0 = result[0][0]
        self.assertEqual(value0, 13.5)
        self.assertTrue(isinstance(value0, float))

    def test_dates_times(self):
        from DateTime import DateTime
        result = self.do_query([
            [sparql.Literal("2009-11-02", sparql.XSD_DATE)],
            [sparql.Literal("2009-11-02 14:31:40", sparql.XSD_DATETIME)],
        ])

        date_value = result[0][0]
        self.assertEqual(date_value, DateTime("2009-11-02"))

        datetime_value = result[1][0]
        self.assertEqual(datetime_value, DateTime("2009-11-02 14:31:40"))
