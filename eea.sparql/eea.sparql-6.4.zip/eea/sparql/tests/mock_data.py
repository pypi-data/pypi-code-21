""" Mock data for testing
"""

from eea.sparql.content.sparql import Sparql
from eea.sparql.tests.base import PORT
from Products.ZSPARQLMethod.Method import parse_arg_spec, \
                                            map_arg_values, \
                                            run_with_timeout, \
                                            interpolate_query, \
                                            query_and_get_result

def mock_sparql_query():
    """ mock query for sparql """
    return "mock"

def loadSparql():
    """ Load data from mock http
    """
    sparql = Sparql(0)
    sparql.endpoint_url = "http://localhost:"+str(PORT)+"/sparql-results.xml"
    sparql.sparql_query = mock_sparql_query
    sparql.timeout = None
    sparql.arg_spec = ""

    args = ""
    arg_spec = parse_arg_spec(sparql.arg_spec)
    arg_values = map_arg_values(arg_spec, args)[1]

    cooked_query = interpolate_query(sparql.query, arg_values)

    query_args = (sparql.endpoint_url, cooked_query)

    data = run_with_timeout(
                10,
                query_and_get_result,
                *query_args)
    return data
