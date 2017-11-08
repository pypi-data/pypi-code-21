from time import time
from datetime import datetime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from OFS.SimpleItem import SimpleItem
from OFS.History import html_diff, Historical
from OFS.Cache import Cacheable
import DateTime
import sparql

try:
    import simplejson as json
except ImportError:
    import json


class QueryTimeout(Exception):
    pass


sparql_converters = {
    sparql.XSD_DATE: DateTime.DateTime,
    sparql.XSD_DATETIME: DateTime.DateTime,
}


manage_addZSPARQLMethod_html = PageTemplateFile('zpt/method_add.zpt', globals())

def manage_addZSPARQLMethod(parent, id, title, endpoint_url="", REQUEST=None):
    """ Create a new ZSPARQLMethod """
    if not endpoint_url:
        endpoint_url = getattr(parent, 'ZSPARQLMETHOD_DEFAULT_ENDPOINT', "")

    ob = ZSPARQLMethod(id, title, endpoint_url)
    parent._setObject(id, ob)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(parent.absolute_url() + '/manage_workspace')

class ZSPARQLMethod(SimpleItem, Historical, Cacheable):
    """
    Persistent SPARQL parametrized query.
    """

    meta_type = "Z SPARQL Method"
    manage_options = (
        ({'label': 'Edit', 'action': 'manage_edit_html'},
        {'label': 'Test', 'action': 'test_html'})
        + Historical.manage_options
        + SimpleItem.manage_options
        + Cacheable.manage_options)

    security = ClassSecurityInfo()

    __ac_permissions__ = (
        # security.declareProtected does not seem to work on __call__
        ('View', ('__call__','')),
    )

    icon = 'misc_/ZSPARQLMethod/method.gif'

    def __init__(self, id, title, endpoint_url):
        super(ZSPARQLMethod, self).__init__()
        self._setId(id)
        self.title = title
        self.endpoint_url = endpoint_url
        self.timeout = None
        self.arg_spec = ""
        self.query = ""

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/method_edit.zpt', globals())

    security.declareProtected(view_management_screens, 'manage_edit')
    def manage_edit(self, REQUEST):
        """ Edit this query """
        self.title = REQUEST.form['title']
        self.endpoint_url= REQUEST.form['endpoint_url']
        timeout = REQUEST.form['timeout'] or None
        if timeout is not None:
            timeout = int(timeout)
        self.timeout = timeout
        self.query = REQUEST.form['query']
        self.arg_spec = REQUEST.form['arg_spec']
        self.ZCacheable_invalidate()
        REQUEST.SESSION['messages'] = ["Saved changes. (%s)" % (datetime.now())]
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')

    security.declareProtected(view, 'document_src')
    def document_src(self, REQUEST=None, **kwargs):
        """ Return processed document source. """
        if REQUEST is not None:
            kwargs.update(REQUEST.form)
        arg_values = self.map_arguments(**kwargs)

        return interpolate_query_html(self.query, arg_values)

    def manage_historyCompare(self, rev1, rev2, REQUEST,
                              historyComparisonResults=''):
        return ZSPARQLMethod.inheritedAttribute('manage_historyCompare')(
            self, rev1, rev2, REQUEST,
            historyComparisonResults = html_diff(rev1.query, rev2.query))

    security.declareProtected(view, 'execute')
    def execute(self, **arg_values):
        """
        Execute the query and return values in the format specified by
        :py:func:`.query_and_get_result`.
        """
        cooked_query = interpolate_query(self.query, arg_values)
        cache_key = {'query': cooked_query}
        result = self.ZCacheable_get(keywords=cache_key)

        if result is None:
            args = (self.endpoint_url, cooked_query)
            result = run_with_timeout(self.timeout, query_and_get_result, *args)
            if not result.get('exception'):
                self.ZCacheable_set(result, keywords=cache_key)

        #result is a mapping with possible keys 'exception' and 'result'
        return result

    _test_html = PageTemplateFile('zpt/method_test.zpt', globals())

    def index_html(self, REQUEST=None, **kwargs):
        """
        REST API

        Request format is the same as for the `test_html` method.

        Response will be JSON, with values encoded as strings in N3 format.
        """

        if REQUEST is not None:
            kwargs.update(REQUEST.form)

        arg_values = self.map_arguments(**kwargs)
        result = self.execute(**arg_values)

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result['result'], default=rdf_values_to_json)

    security.declareProtected(view, 'map_arguments')
    def map_arguments(self, **kwargs):
        """ Map the given arguments to our arg_spec """
        arg_spec = parse_arg_spec(self.arg_spec)
        missing, arg_values = map_arg_values(arg_spec, kwargs)
        if missing:
            raise KeyError("Missing arguments: %r" % missing)
        else:
            return arg_values

    security.declareProtected(view, 'test_html')
    def test_html(self, REQUEST):
        """
        Execute the query and pretty-print the results as an HTML table.
        """

        arg_spec = parse_arg_spec(self.arg_spec)
        missing, arg_values = map_arg_values(arg_spec, REQUEST.form)
        error = None

        if missing:
            # missing argument
            data = None
            dt = 0

        else:
            t0 = time()

            result = self.execute(**arg_values)
            data = result.get('result')
            error = result.get('exception')

            dt = time() - t0

        options = {
            'query': interpolate_query_html(self.query, arg_values),
            'data': data,
            'duration': dt,
            'arg_spec': arg_spec,
            'error': error,
        }
        return self._test_html(REQUEST, **options)

    # __call__ requires the "View" permission, see __ac_permissions__ above.
    def __call__(self, **kwargs):
        """
        Map the given arguments to our arg_spec and execute the query.
        Returns a :class:`MethodResult` object.
        """
        return MethodResult(self.execute(**self.map_arguments(**kwargs)))

InitializeClass(ZSPARQLMethod)


def query_and_get_result(*args, **kwargs):
    """
    Helper function that calls `sparql.query` with the given arguments and
    returns its results as an easy-to-cache dictionary.
    """
    result = sparql.query(*args, timeout = kwargs.get("timeout", 0))
    return {
        'var_names': [unicode(name) for name in result.variables],
        'rows': result.fetchall(),
        'has_result': result._hasResult,
    }


def raw_query_and_get_result(*args, **kwargs):
    """
    Returns unparsed query results for xml, xmlschema, json formats
    """
    timeout = kwargs.get("timeout", 0)
    accept = kwargs.get("accept", "application/sparql-results+xml")
    result = sparql.query(*args, timeout=timeout, accept=accept, raw=True)
    return result


class MethodResult(object):
    """
    MethodResult Encapsulates a query result. It provides convenient
    access to unpacked pythonic values instead of raw `RDFTerm` objects.
    You can iterate through it like a list. Also, the following
    properties are available:

    `var_names`
        A list of the requested query variables.

    `has_result`
        If the query was `ASK`, `has_result` is a boolean, indicating
        whether the query would return any rows. Otherwise it's `None`.

    `rdfterm_rows`
        Original `RDFTerm` values returned by the SPARQL query.

    """

    __allow_access_to_unprotected_subobjects__ = {'rdfterm_rows': 1,
        'var_names': 1, 'has_result': 1, '__iter__': 1, '__getitem__': 1}

    def __init__(self, result_dict):
        self.var_names = result_dict['result']['var_names']
        self.rdfterm_rows = result_dict['result']['rows']
        self.has_result = result_dict['result']['has_result']

    def __iter__(self):
        return (sparql.unpack_row(r, convert_type=sparql_converters)
                for r in self.rdfterm_rows)

    def __getitem__(self, n):
        return sparql.unpack_row(self.rdfterm_rows[n],
                                 convert_type=sparql_converters)

    def __len__(self):
        return len(self.rdfterm_rows)


import traceback

def run_with_timeout(timeout, func, *args, **kwargs):
    """
    Run the given callable in a separate thread; if it does not return within
    `timeout` seconds, ignore the result and raise `QueryTimeout`. The thread
    will keep running until either the socket times out or a result is
    received.
    """

    kwargs['timeout'] = timeout
    result = {}
    try:
        ret = func(*args, **kwargs)
    except sparql.SparqlException, e:
        if e.code == 28:
            raise QueryTimeout
        result['exception'] = e.message
    except Exception, e:
        result['exception'] = traceback.format_exc()
    else:
        result['result'] = ret

    return result

RDF_TERM_FACTORY = {
    'n3term':   sparql.parse_n3_term,
    'iri':      sparql.IRI,
    'string':   sparql.Literal,
    'integer':  lambda v: sparql.Literal(v, sparql.XSD_INTEGER),
    'long':     lambda v: sparql.Literal(v, sparql.XSD_LONG),
    'double':   lambda v: sparql.Literal(v, sparql.XSD_DOUBLE),
    'float':    lambda v: sparql.Literal(v, sparql.XSD_FLOAT),
    'decimal':  lambda v: sparql.Literal(v, sparql.XSD_DECIMAL),
    'datetime': lambda v: sparql.Literal(v, sparql.XSD_DATETIME),
    'date':     lambda v: sparql.Literal(v, sparql.XSD_DATE),
    'time':     lambda v: sparql.Literal(v, sparql.XSD_TIME),
    'boolean':  lambda v: sparql.Literal(v, sparql.XSD_BOOLEAN),
}

def parse_arg_spec(raw_arg_spec):
    """
    Parse the arguments for a ZSPARQLMethod. `raw_arg_spec` should be a
    space-separated string of variable definitions in the format
    ``<name>:<type>`` where `type` is one of the following:

    ============    ==================================
    Type            Meaning
    ============    ==================================
    ``n3term``      parse the value assuming N3 syntax
    ``iri``         IRI
    ``string``      plain literal
    ``integer``     typed literal, XSD_INTEGER
    ``long``        typed literal, XSD_LONG
    ``double``      typed literal, XSD_DOUBLE
    ``float``       typed literal, XSD_FLOAT
    ``decimal``     typed literal, XSD_DECIMAL
    ``datetime``    typed literal, XSD_DATETIME
    ``date``        typed literal, XSD_DATE
    ``time``        typed literal, XSD_TIME
    ``boolean``     typed literal, XSD_BOOLEAN
    ============    ==================================
    """
    arg_spec = {}
    for one_arg_spec in raw_arg_spec.split():
        name, type_spec = one_arg_spec.split(':')
        factory = RDF_TERM_FACTORY[type_spec]
        arg_spec[str(name)] = factory
    return arg_spec

def map_arg_values(arg_spec, arg_data):
    """
    Box all values in `arg_data` according to `arg_spec`. Returns a tuple
    of (`missing`, `arg_values`).
    """
    arg_values = {}
    missing = []
    for name, factory in arg_spec.iteritems():
        if name in arg_data:
            arg_values[name] = factory(arg_data[name])
        else:
            missing.append(name)

    return missing, arg_values

def interpolate_query(query_spec, var_data):
    """
    Parse the given query using `string.Template`, then perform variable
    substitution. `var_data` should be a dictionary, keyed with the template's
    variables, and its values are assumed to be `sparql.RDFTerm` instances.
    """
    from string import Template
    var_strings = dict( (k, v.n3()) for (k, v) in var_data.iteritems() )
    return Template(query_spec).substitute(**var_strings)

def html_quote(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def interpolate_query_html(query_spec, var_data):
    """
    Debugging version of interpolate_query. The result is a SPARQL method
    that contains HTML markup highlighting where variable substitutions take
    place.
    """
    from string import Template
    var_strings = dict( (k, v.n3()) for (k, v) in var_data.iteritems() )
    tmpl = Template(html_quote(query_spec))
    def convert(mo): # Simplified version of Template's helper function
        named = mo.group('named') or mo.group('braced')
        if named is not None:
            css_class = ['variable']
            if named in var_strings:
                css_class.append('interpolated')
                text = var_strings[named]
            else:
                text = mo.group()
            return '<span class="%(css_class)s">%(text)s</span>' % {
                'css_class': ' '.join(css_class),
                'text': html_quote(text),
            }
            # TODO return '%s' % var_strings.get(named, mo.group())
        if mo.group('escaped') is not None:
            return tmpl.delimiter
        if mo.group('invalid') is not None:
            tmpl._invalid(mo)
        raise ValueError('Unrecognized named group in pattern', tmpl.pattern)
    return tmpl.pattern.sub(convert, tmpl.template)

def rdf_values_to_json(value):
    if isinstance(value, sparql.RDFTerm):
        return value.n3()
    raise TypeError
