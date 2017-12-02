"""
This module provides the interface definitions for defining and parsing search requests.
It abstracts queries using a specific query language, heavily based on Python syntax.
"""

# pylint: disable=invalid-name

import enum
import io
import typing
import tokenize

from relevance import loggers


# Logging
logger = loggers.getLogger('relevance.query')


class SortOrder(enum.Enum):
    """
    Operators for sort orders.
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
    This class is used to represent a query. A query is the part of the search
    request that includes terms and facet filters.
    """
    def __init__(self, logic: LogicalOperator = LogicalOperator.AND) -> None:
        """
        :param logic: the logical operator for the query, one of :class:`LogicalOperator`.
        """
        self.logic = logic
        self.terms: typing.List[str] = []
        self.facets: typing.List[typing.Tuple[str, ComparisonOperator, typing.Any]] = []
        self.queries: typing.List['Query'] = []

    def term(self, term: str):
        """
        Add a term to the query.

        :param term: the term to add to the query.
        """
        self.terms.append(term)

    def facet(self, field: str, comp: ComparisonOperator, value: typing.Any):
        """
        Add a facet filter to the query.

        :param field: the name of the field to filter by.
        :param comp: the comparison operator to use, one of :class:`ComparisonOperator`.
        :param value: the value to filter by.
        """
        self.facets.append((field, comp, value))

    def query(self, query: 'Query'):
        """
        Add a nested query to the query.

        :param query: the query object to add.
        """
        self.queries.append(query)

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Transform the query object into a dictionary.

        :return: a dictionary object for the query.
        """
        result = {'logic': self.logic.value}

        if self.terms:
            result['terms'] = self.terms

        if self.facets:
            result['facets'] = [[x[0], x[1].value, x[2]] for x in self.facets]

        if self.queries:
            result['queries'] = [x.to_dict() for x in self.queries]

        return result

    def to_str(self) -> str:
        """
        Transform the query object into a string.

        :return: a string for the query.
        """
        result = []

        for term in self.terms:
            result.append(repr(term))

        for facet in self.facets:
            result.append('{0}{1}{2}'.format(facet[0], facet[1].value, repr(facet[2])))

        for query in self.queries:
            result.append('({0})'.format(query.to_str()))

        return ' {0} '.format(self.logic.value).join(result)

    def __str__(self) -> str:
        """
        Implementation of the :func:`str` function.
        """
        return self.to_str()

    def __eq__(self, other: object) -> bool:
        """
        Implementation of the operator for comparison.
        """
        return str(self) == str(other)


class Search(object):
    """
    The search class is used to represent a search request. A search request is
    usually comprised of a query and other options, such a sorting, slicing, etc.
    """
    def __init__(self):
        """
        :var list queries: a list of subqueries to this one, or `None`.
        :var list sorts: a list of sorting tuples for the query, in order
            of priority.
        :var tuple slices: the slice (offset and limit) to apply on the result set.
        :var list facets: a list of facets to return. `None` means all defined facets
            are returned. An empty list means no facets are returned.
        :var list doc_types: a list of document types to search against, or `None` for
            all document types.
        """
        self.queries = None
        self.sorts = []
        self.slices = (0, 10)
        self.facets = None
        self.doc_types = None

    def query(self, query: Query):
        """
        Add a query to the search object.

        :param query: the query object to add.
        """
        self.queries = query

    def sort(self, field: str, order: SortOrder = SortOrder.ASC):
        """
        Add a sort to the search object.

        :param field: the field to sort by.
        :param order: the sort order to use for that field, one of :class:`SortOrder`.
        """
        if not isinstance(order, SortOrder):
            order = SortOrder(order)
        self.sorts.append((field, order))

    def slice(self, offset: int, limit: int):
        """
        Add a slice to the search object.

        :param offset: the offset of the slice.
        :param limit: the maximum number of results to return.
        """
        self.slices = (offset, limit)

    def facet(self, *names):
        """
        Add or disable facets in the search object.

        :param names: a list of facets to return. When empty, disables facets completely.
        """
        self.facets = names

    def type(self, *names):
        """
        Set the document types for the search object.

        :param names: a list of document types to search into.
        """
        self.doc_types = names

    def to_dict(self) -> typing.Dict[str, object]:
        """
        Transform the search object into a dictionary.

        :return: the search object as a dictionary.
        """
        result = {
            'offset': self.slices[0],
            'limit': self.slices[1],
            'type': self.doc_types,
            'facet': self.facets,
        }

        if self.queries is not None:
            result['query'] = self.queries.to_dict()

        if self.sorts:
            result['sort'] = [{field: order.value} for field, order in self.sorts]

        return result

    def to_str(self) -> str:
        """
        Tranform the search object into a string.

        :return: the search string.
        """
        result = []

        if self.queries is not None:
            result.append(self.queries.to_str())

        if self.sorts:
            for field, order in self.sorts:
                result.append('with sort({0}, {1})'.format(field, order.value))

        if self.facets is not None:
            result.append('with facet({0})'.format(', '.join(self.facets)))

        if self.doc_types is not None:
            result.append('with type({0})'.format(', '.join(self.doc_types)))

        result.append('with slice({0}, {1})'.format(*self.slices))

        return ' '.join(result)

    def __str__(self) -> str:
        """
        Implementation of the :func:`str` function.
        """
        return self.to_str()

    def __eq__(self, other: object) -> bool:
        """
        Implementation of the comparison operator.
        """
        return str(self) == str(other)


class QueryParser(object):  # pylint: disable=too-few-public-methods
    """
    This class provides an interface for parsing queries and search requests.
    """
    def loads(self, data: str, *, query_only: bool = False) -> typing.Union[Search, Query]:  # pylint: disable-all
        """
        Parse a query or a search request.

        :param data: the input request data.
        :param query_only: when `True`, only the query will be parsed. `False` will
            parse additional search options as well.
        :return: a search object if `query_only` is `False`, otherwise a query object.
        :raises: :class:`QueryParserError`: when a parsing error occurs.
        """
        logger.info('received query', query_only=query_only, data=data)

        tokens = tokenize.tokenize(io.BytesIO(data.encode('utf-8')).readline)
        tokens = list(tokens)  # type: ignore

        search = Search()
        query = Query(None)

        buffers: typing.List[str] = []
        nesting = 0
        negated = False

        comp_operators = ['==', '>', '<', '>=', '<=', '!=']

        for i, token in enumerate(tokens[1:]):  # type: ignore
            try:
                next_token = tokens[i + 2]  # type: ignore
            except IndexError:
                next_token = None

            logger.debug('token',
                         id=id(token), type=token.type, string=token.string,
                         start_x=token.start[0], start_y=token.start[1],
                         end_x=token.end[0], end_y=token.end[1])

            # Option start
            if token.type == tokenize.NAME and token.string == 'with':
                logger.debug('option start', id=id(token))

                if nesting > 0 or buffers:
                    raise QueryParserError(token)

                buffers.append(token.string)

            elif 'with' in buffers:
                # Function arguments
                if token.type == tokenize.OP and token.string in ['(', ',', '.']:
                    logger.debug('function argument', id=id(token))
                    buffers.append(token.string)

                # Function end
                elif token.type == tokenize.OP and token.string == ')':
                    logger.debug('function end', id=id(token))

                    buffers.append(token.string)
                    func = buffers[1]
                    bufs: typing.List[str] = []
                    args: typing.List[str] = []

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
                        getattr(search, func)(*args)
                    except TypeError as e:
                        raise QueryParserError(str(e))
                    except AttributeError:
                        raise QueryParserError('unknown option {0}'.format(func))

                    buffers.clear()

                # Function name
                elif token.type == tokenize.NAME and len(buffers) == 1:
                    logger.debug('function name', id=id(token))
                    buffers.append(token.string)

                elif token.type in [tokenize.NAME, tokenize.NUMBER]:
                    logger.debug('function argument', id=id(token))
                    buffers.append(token.string)

                else:
                    raise QueryParserError(token)

            elif (token.type == tokenize.NAME and nesting == 0 and
                  token.string not in ('None', 'True', 'False')):
                # Logical operator
                if token.string == 'and':
                    logger.debug('logical operator', id=id(token))
                    if query.logic is not None and query.logic != LogicalOperator.AND:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Logical operator
                elif token.string == 'or':
                    logger.debug('logical operator', id=id(token))
                    if query.logic is not None and query.logic != LogicalOperator.OR:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Logical operator
                elif token.string == 'not':
                    logger.debug('logical operator', id=id(token))
                    if query.logic is not None and query.logic != LogicalOperator.NOT:
                        raise QueryParserError(token)
                    query.logic = LogicalOperator(token.string)

                # Other operator or field name
                else:
                    logger.debug('field name', id=id(token))
                    buffers.append(token.string)

            elif token.type == tokenize.OP:
                # Sub queries start
                if token.string == '(':
                    logger.debug('sub query start', id=id(token))
                    nesting += 1

                    if nesting > 1:
                        buffers.append(token.string)

                # Sub queries end
                elif token.string == ')':
                    logger.debug('sub query end', id=id(token))
                    nesting -= 1

                    if nesting > 0:
                        buffers.append(token.string)
                    else:
                        value = ' '.join(buffers)
                        sub = self.loads(value, query_only=True)  # type: ignore
                        query.query(sub)  # type: ignore
                        buffers.clear()

                # Facet nested names
                elif token.string == '.' and nesting == 0:
                    logger.debug('nested facet', id=id(token))
                    buffers.append(token.string)

                # Comparison operators
                elif token.string in comp_operators and nesting == 0:
                    logger.debug('comparison operator', id=id(token))
                    buffers.append(token.string)

                elif (token.string == '-' and nesting == 0 and
                      next_token.type == tokenize.NUMBER):
                    logger.debug('negative number operator', id=id(token))
                    negated = True

                elif nesting == 0:
                    raise QueryParserError(token)  # type: ignore

                else:
                    logger.debug('value', id=id(token))
                    buffers.append(token.string)

            elif (token.type in [tokenize.NAME, tokenize.STRING, tokenize.NUMBER] and
                  nesting == 0):
                # Terms
                if len(buffers) == 0:
                    logger.debug('value', id=id(token))
                    value = eval(token.string)
                    query.term(value)
                    buffers.clear()

                # Facet values
                elif len(set(buffers).intersection(comp_operators)) > 0:
                    logger.debug('as facet value', id=id(token))
                    field = ''.join(buffers[0:-1])
                    comp = buffers[-1]
                    value = eval(token.string)
                    if negated:
                        value = 0 - value  # type: ignore
                        negated = False
                    query.facet(field, ComparisonOperator(comp), value)
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

        search.query(query)
        return search


class QueryParserError(SyntaxError):
    """
    This exception class is raised when the :class:`QueryParser` encounters an error
    during parsing.
    """
    def __init__(self, token: typing.Union[str, typing.Tuple[str, tokenize.TokenInfo]]) -> None:
        """
        :param token: a message or the token object that caused the error.
        """
        if not isinstance(token, str):
            super().__init__('unexpected token "{0}" at offset {1}'
                             .format(token.string, token.start[1]))  # type: ignore
        else:
            super().__init__(token)
