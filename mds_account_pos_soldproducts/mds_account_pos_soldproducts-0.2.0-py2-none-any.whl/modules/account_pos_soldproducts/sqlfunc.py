# -*- coding: utf-8 -*-
from sql.aggregate import Aggregate

class AggregateExtra:
    """ add separator
    """
    def __init__(self):
        self.separator = ''


class StringAgg(Aggregate, AggregateExtra):
    __slots__ = ()
    _sql = 'STRING_AGG'

    def __init__(self, expression, separator, distinct=False, within=None, filter_=None, window=None):
        super(StringAgg, self).__init__(expression, distinct=distinct, 
                                        within=within, filter_=filter_, window=window)
        self.separator = separator

    def __str__(self):
        quantifier = 'DISTINCT ' if self.distinct else ''
        aggregate = "%s(%s%s, '%s')" % (self._sql, quantifier, self.expression, self.separator)
        within = ''
        if self.within:
            within = (' WITHIN GROUP (ORDER BY %s)'
                % ', '.join(map(str, self.within)))
        filter_ = ''
        if self.filter_:
            filter_ = ' FILTER (WHERE %s)' % self.filter_
        window = ''
        if self.window:
            window = ' OVER "%s"' % self.window.alias
        return aggregate + within + filter_ + window
