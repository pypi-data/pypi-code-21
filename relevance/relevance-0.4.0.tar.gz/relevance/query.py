"""
Relevance query module.

This module provides the interface definitions for defining and parsing search requests.
"""

import enum
import copy
import io
import typing
import tokenize
import logging


# Logging
logger = logging.getLogger('relevance.query')


class SortOrder(enum.Enum):
    """
    Operators for sort order.
    """
    ASC = 'asc'
    DESC = 'desc'


class LogicalOperator(enum.Enum):
    """
    Operators for logical expressions.
    """
    AND = 'and'
    OR = 'or'
    NOT = 'not'


class ComparisonOperator(enum.Enum):
    """
    Operators for comparison expressions.
    """
    EQ = '=='
    NEQ = '!='
    GT = '>'
    LT = '<'
    GTE = '>='
    LTE = '<='


class Query(object):
    """
    Query class.

    This class provides a filtering interface for search queries.
    """
    def __init__(self, logic: LogicalOperator=LogicalOperator.AND):
        """
        Initialize the query.

        :param logic: the logical operator for the query.
        """
        self.logic = logic
        self.terms = []
        self.facets = []
        self.queries = []

    def term(self, term: str) -> 'Query':
        """
        Add a term to the query.

        :param term: the term to add to the query.
        :returns: a new updated query object.
        """
        self = copy.deepcopy(self)
        self.terms.append(term)
        return self

    def facet(self, field: str, comp: ComparisonOperator, value) -> 'Query':
        """
        Add a facet filter to the query.

        :param field: the field to filter by.
        :param value: the value to filter by.
        :returns: a new updated query object.
        """
        self = copy.deepcopy(self)
        self.facets.append((field, comp, value))
        return self

    def query(self, query) -> 'Query':
        """
        Add a nested query to the query.

        :param query: the query object to add.
        :returns: a new updated query object.
        """
        self = copy.deepcopy(self)
        self.queries.append(query)
        return self

    def to_dict(self) -> typing.Dict[str, list]:
        """
        Transform the query object into a dictionary.

        :returns: a dictionary object for the query.
        """
        result = {'logic': self.logic.value}

        if len(self.terms) > 0:
            result['terms'] = self.terms

        if len(self.facets) > 0:
            result['facets'] = [[x[0], x[1].value, x[2]] for x in self.facets]

        if len(self.queries) > 0:
            result['queries'] = [x.to_dict() for x in self.queries]

        return result

    def to_str(self) -> str:
        """
        Transform the query object into a string.

        :returns: a string for the query.
        """
        result = []

        for x in self.terms:
            result.append(repr(x))

        for x in self.facets:
            result.append('{0}{1}{2}'.format(x[0], x[1].value, repr(x[2])))

        for x in self.queries:
            result.append('({0})'.format(x.to_str()))

        return ' {0} '.format(self.logic.value).join(result)

    def __str__(self) -> str:
        """
        Overload operator for string comparison.
        """
        return self.to_str()

    def __eq__(self, other: object) -> bool:
        """
        Overload operator for comparison.
        """
        return str(self) == str(other)


class Search(object):
    """
    Search class.

    This class provides an interface for building query requests.
    """
    def __init__(self):
        """
        Initialize the search object.
        """
        self.queries = None
        self.sorts = []
        self.slices = (0, 10)
        self.facets = None
        self.doc_types = None

    def query(self, query: Query) -> 'Search':
        """
        Add a query to the search object.

        :param query: the query object to add.
        :returns: a new updated search object.
        """
        self = copy.deepcopy(self)
        self.queries = query
        return self

    def sort(self, field: str, order: SortOrder=SortOrder.ASC) -> 'Search':
        """
        Add a sort to the search object.

        :param field: the field to sort by.
        :param order: the sort order to use for that field.
        :returns: a new updated search object.
        """
        self = copy.deepcopy(self)
        self.sorts.append((field, order))
        return self

    def slice(self, offset: int, limit: int) -> 'Search':
        """
        Add a slice to the search object.

        :param offset: the offset of the slice.
        :param limit: the maximum number of results.
        :returns: a new updated search object.
        """
        self = copy.deepcopy(self)
        self.slices = (offset, limit)
        return self

    def facet(self, *names) -> 'Search':
        """
        Add or disable facets in the search object.

        :param names: a list of facets to return.
        :returns: a new updated search object.
        """
        self = copy.deepcopy(self)
        self.facets = names
        return self

    def type(self, *names) -> 'Search':
        """
        Set the document types for the search object.

        :param names: a list of document types to search into.
        :returns: a new updated search object.
        """
        self = copy.deepcopy(self)
        self.doc_types = names
        return self

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Transform the search object into a dictionary.

        :returns: the search object as a dictionary.
        """
        result = {
            'offset': self.slices[0],
            'limit': self.slices[1],
            'type': self.doc_types,
            'facet': self.facets,
        }

        if self.queries is not None:
            result['query'] = self.queries.to_dict()

        if len(self.sorts) > 0:
            result['sort'] = self.sorts

        return result

    def to_str(self) -> str:
        """
        Tranform the search object into a string.

        :returns: the search string.
        """
        result = []

        if self.queries is not None:
            result.append(self.queries.to_str())

        if len(self.sorts) > 0:
            for x in self.sorts:
                result.append('with sort({0}, {1})'.format(*x))

        if self.facets is not None:
            result.append('with facet({0})'.format(', '.join(self.facets)))

        if self.doc_types is not None:
            result.append('with type({0})'.format(', '.join(self.doc_types)))

        result.append('with slice({0}, {1})'.format(*self.slices))

        return ' '.join(result)

    def __str__(self) -> str:
        """
        Overload operator for string comparison.
        """
        return self.to_str()

    def __eq__(self, other: object) -> bool:
        """
        Overload operator for comparison.
        """
        return str(self) == str(other)


class QueryParserError(SyntaxError):
    """
    Exception class for parser errors.
    """
    def __init__(self, token: typing.Tuple[str, tokenize.TokenInfo]):
        """
        Initialize the object.

        :param token: a message or the token object that caused the error.
        """
        if not isinstance(token, str):
            super().__init__('unexpected token "{0}" at offset {1}'
                             .format(token.string, token.start[1]))
        else:
            super().__init__(token)


class QueryParser(object):
    """
    Query parser class.

    This class provides an interface for parsing queries and search requests.
    """
    def loads(self, data: str, *, query_only=False) -> (Search, Query):
        """
        Parse a query from a search.

        :param data: the input data.
        :param query_only: whether to parse the query only or additional options as well.
        :returns: a search object if query_only is False, otherwise a query object.
        :raises: QueryParserError: when a parsing error occurs.
        """
        logger.info('received query (qo={1}): {0}'.format(data, int(query_only)))

        tokens = tokenize.tokenize(io.BytesIO(data.encode('utf-8')).readline)
        tokens = list(tokens)

        search = Search()
        query = Query(None)

        buffers = []
        nesting = 0
        negated = False

        comp_operators = ['==', '>', '<', '>=', '<=', '!=']

        for i, token in enumerate(tokens[1:]):
            try:
                next_token = tokens[i+2]
            except IndexError:
                next_token = None

            logger.debug('found token type {0} at {1},{2}:{3},{4}: {5}'.format(
                token.type, token.start[0], token.start[1], token.end[0], token.end[1],
                token.string,
            ))

            # Option start
            if token.type == tokenize.NAME and token.string == 'with':
                logger.debug('-- as option start')

                if nesting > 0 or len(buffers) > 0:
                    raise QueryParserError(token)

                buffers.append(token.string)

            elif 'with' in buffers:
                # Function arguments
                if token.type == tokenize.OP and token.string in ['(', ',', '.']:
                    logger.debug('-- as function argument')
                    buffers.append(token.string)

                # Function end
                elif token.type == tokenize.OP and token.string == ')':
                    logger.debug('-- as function end')

                    buffers.append(token.string)
                    func = buffers[1]
                    bufs = []
                    args = []

                    for x in buffers[3:]:
                        if x in [',', ')']:
                            try:
                                if len(bufs) > 1:
                                    val = ''.join(bufs)
                                else:
                                    val = bufs[0]
                                args.append(val)
                            except IndexError:
                                pass
                            bufs.clear()
                        elif x == '.':
                            bufs.append(x)
                        else:
                            try:
                                val = eval(x)
                                bufs.append(val)
                            except NameError:
                                bufs.append(x)

                    try:
                        search = getattr(search, func)(*args)
                    except TypeError as e:
                        raise QueryParserError(str(e))
                    except AttributeError:
                        raise QueryParserError('unknown option {0}'.format(func))

                    buffers.clear()

                # Function name
                elif token.type == tokenize.NAME and len(buffers) == 1:
                    logger.debug('-- as function name')
                    buffers.append(token.string)

                elif token.type in [tokenize.NAME, tokenize.NUMBER]:
                    logger.debug('-- as function argument')
                    buffers.append(token.string)

                else:
                    raise QueryParserError(token)

            elif (token.type == tokenize.NAME and nesting == 0 and
                  token.string not in ('None', 'True', 'False')):
                # Logical operator
                if token.string == 'and':
                    logger.debug('-- as logical operator')
                    if query.logic is not None and query.logic != LogicalOperator.AND:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Logical operator
                elif token.string == 'or':
                    logger.debug('-- as logical operator')
                    if query.logic is not None and query.logic != LogicalOperator.OR:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Logical operator
                elif token.string == 'not':
                    logger.debug('-- as logical operator')
                    if query.logic is not None and query.logic != LogicalOperator.NOT:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Other operator or field name
                else:
                    logger.debug('-- as operator or field name')
                    buffers.append(token.string)

            elif token.type == tokenize.OP:
                # Sub queries start
                if token.string == '(':
                    logger.debug('-- as sub query start')
                    nesting += 1

                    if nesting > 1:
                        buffers.append(token.string)

                # Sub queries end
                elif token.string == ')':
                    logger.debug('-- as sub query end')
                    nesting -= 1

                    if nesting > 0:
                        buffers.append(token.string)
                    else:
                        value = ' '.join(buffers)
                        sub = self.loads(value, query_only=True)
                        query = query.query(sub)
                        buffers.clear()

                # Facet nested names
                elif token.string == '.' and nesting == 0:
                    logger.debug('-- nested facet operator')
                    buffers.append(token.string)

                # Comparison operators
                elif token.string in comp_operators and nesting == 0:
                    logger.debug('-- as comparison operator')
                    buffers.append(token.string)

                elif (token.string == '-' and nesting == 0 and
                      next_token.type == tokenize.NUMBER):
                    logger.debug('-- as negative number operator')
                    negated = True

                elif nesting == 0:
                    raise QueryParserError(token)

                else:
                    logger.debug('-- as value')
                    buffers.append(token.string)

            elif (token.type in [tokenize.NAME, tokenize.STRING, tokenize.NUMBER] and
                  nesting == 0):
                # Terms
                if len(buffers) == 0:
                    logger.debug('-- as query term')
                    value = eval(token.string)
                    query = query.term(value)
                    buffers.clear()

                # Facet values
                elif len(set(buffers).intersection(comp_operators)) > 0:
                    logger.debug('-- as facet value')
                    field = ''.join(buffers[0:-1])
                    comp = buffers[-1]
                    value = eval(token.string)
                    if negated:
                        value = 0 - value
                        negated = False
                    query = query.facet(field, ComparisonOperator(comp), value)
                    buffers.clear()

                else:
                    raise QueryParserError(token)

            elif nesting > 0:
                buffers.append(token.string)

            elif token.type != 0 or len(buffers) > 0 or nesting > 0:
                raise QueryParserError(token)

        if query.logic is None:
            query.logic = LogicalOperator.AND

        if query_only:
            return query

        return search.query(query)
