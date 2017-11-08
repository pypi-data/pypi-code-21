""" Custom AT Validators
"""
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation.interfaces.IValidator import IValidator
from Products.ZSPARQLMethod.Method import run_with_timeout
from Products.ZSPARQLMethod.Method import query_and_get_result
from zope.annotation import IAnnotations
from zope.interface import implements

sparql = __import__('sparql')


class SparqlQueryValidator(object):
    """ Validator
    """
    implements(IValidator)

    def __init__(self, name, title='Sparql Query result size',
                 description='Check if sparql_query result is too big'):
        self.name = name
        self.title = title or name
        self.description = description

    def count_sparql_results(self, timeout, func, *query):
        """
        :param timeout: Sparql query timeout
        :type timeout: int
        :param func: query_and_get_result function used to query Sparql
        :type func: function
        :param query: Endpoint url and sparql query
        :type query: tuple
        :return: Dict with Sparql results
        :rtype: dict
        """
        endpoint = query[0]
        sparql_query = query[1]
        split_query = sparql_query.split("SELECT")
        # attempt to wrap original select within a count in order to get
        # row length without having to save them since we are only concerned
        # with results count and not the results themselves
        count_query = split_query[0] + "SELECT (COUNT (*) as ?row_count) " \
                                 "WHERE{{ SELECT" + "".join(split_query[1:]) \
                      + "}}"
        result_len = 0
        try:
            result = sparql.query(endpoint, count_query, timeout=timeout)
            fetched_results = result.fetchall()
            for entry in fetched_results:
                first_result = entry[0]
                result_len = int(first_result.value)
                break
        except Exception:
            result = run_with_timeout(timeout, func, *query)
            result_len = len(result.get('result', {}).get('rows', {}))
        return result_len



    def run_query(self, request, func, query):
        """
        :param request: Object request
        :type request: object
        :param func: query_and_get_result function used to query Sparql
        :type func: function
        :param query: Endpoint url and sparql query
        :type query: tuple
        :return: Dict with Sparql results
        :rtype: dict
        """
        cache = IAnnotations(request)
        key = 'query_result'
        data = cache.get('query_result', None)
        if data is None:
            data = self.count_sparql_results(15, func, *query)
            cache[key] = data
        return data

    def __call__(self, value, *args, **kwargs):
        """ Check if provided query is within size limit """
        obj = kwargs.get('instance')
        request = kwargs['REQUEST']
        if 'atct_edit' not in request.URL0:
            return 1

        arg_spec = (obj.endpoint_url, value)
        results_len = self.run_query(request, query_and_get_result, arg_spec)
        pprop = obj.portal_properties
        site_props = getattr(pprop, 'site_properties', None)
        max_rows = site_props.getProperty('sparql_max_row_length', 9000)
        sparql_msg = site_props.getProperty('sparql_max_row_msg', "%s %s")
        msg = sparql_msg % (results_len, max_rows)
        if results_len > max_rows:
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            return 1
        return 1
