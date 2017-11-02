# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Grid Filters
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

import six
import sqlalchemy as sa

from rattail.gpc import GPC
from rattail.util import OrderedDict
from rattail.core import UNSPECIFIED
from rattail.time import localtime, make_utc
from rattail.util import prettify

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from webhelpers2.html import HTML, tags


log = logging.getLogger(__name__)


class FilterValueRenderer(object):
    """
    Base class for all filter renderers.
    """

    @property
    def name(self):
        return self.filter.key

    def render(self, value=None, **kwargs):
        """
        Render the filter input element(s) as HTML.  Default implementation
        uses a simple text input.
        """
        return tags.text(self.name, value=value, **kwargs)


class DefaultValueRenderer(FilterValueRenderer):
    """
    Default / fallback renderer.
    """


class NumericValueRenderer(FilterValueRenderer):
    """
    Input renderer for numeric values.
    """

    def render(self, value=None, **kwargs):
        kwargs.setdefault('step', '0.001')
        return tags.text(self.name, value=value, type='number', **kwargs)


class DateValueRenderer(FilterValueRenderer):
    """
    Input renderer for date values.
    """

    def render(self, value=None, **kwargs):
        return tags.text(self.name, value=value, type='date', **kwargs)


class ChoiceValueRenderer(FilterValueRenderer):
    """
    Renders value input as a dropdown/selectmenu of available choices.
    """

    def __init__(self, options):
        self.options = options

    def render(self, value=None, **kwargs):
        return tags.select(self.name, [value], self.options, **kwargs)


class EnumValueRenderer(ChoiceValueRenderer):
    """
    Renders value input as a dropdown/selectmenu of available choices.
    """

    def __init__(self, enum):
        sorted_keys = sorted(enum, key=lambda k: enum[k].lower())
        self.options = [tags.Option(enum[k], six.text_type(k)) for k in sorted_keys]


class GridFilter(object):
    """
    Represents a filter available to a grid.  This is used to construct the
    'filters' section when rendering the index page template.
    """
    verb_labels = {
        'is_any':               "is any",
        'equal':                "equal to",
        'not_equal':            "not equal to",
        'greater_than':         "greater than",
        'greater_equal':        "greater than or equal to",
        'less_than':            "less than",
        'less_equal':           "less than or equal to",
        'is_null':              "is null",
        'is_not_null':          "is not null",
        'is_true':              "is true",
        'is_false':             "is false",
        'contains':             "contains",
        'does_not_contain':     "does not contain",
        'is_me':                "is me",
        'is_not_me':            "is not me",
    }

    valueless_verbs = ['is_any', 'is_null', 'is_not_null', 'is_true', 'is_false',
                       'is_me', 'is_not_me']

    value_renderer_factory = DefaultValueRenderer

    def __init__(self, key, label=None, verbs=None, value_renderer=None,
                 default_active=False, default_verb=None, default_value=None, **kwargs):
        self.key = key
        self.label = label or prettify(key)
        self.verbs = verbs or self.get_default_verbs()
        self.set_value_renderer(value_renderer or self.value_renderer_factory)
        self.default_active = default_active
        self.default_verb = default_verb
        self.default_value = default_value
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.key))

    def get_default_verbs(self):
        """
        Returns the set of verbs which will be used by default, i.e.  unless
        overridden by constructor args etc.
        """
        verbs = getattr(self, 'default_verbs', None)
        if verbs:
            if callable(verbs):
                return verbs()
            return verbs
        return ['equal', 'not_equal', 'is_null', 'is_not_null', 'is_any']

    def set_value_renderer(self, renderer):
        """
        Set the value renderer for the filter, post-construction.
        """
        if not isinstance(renderer, FilterValueRenderer):
            renderer = renderer()
        renderer.filter = self
        self.value_renderer = renderer

    def filter(self, data, verb=None, value=UNSPECIFIED):
        """
        Filter the given data set according to a verb/value pair.  If no verb
        and/or value is specified by the caller, the filter will use its own
        current verb/value by default.
        """
        verb = verb or self.verb
        value = self.get_value(value)
        filtr = getattr(self, 'filter_{0}'.format(verb), None)
        if not filtr:
            raise ValueError("Unknown filter verb: {0}".format(repr(verb)))
        return filtr(data, value)

    def get_value(self, value=UNSPECIFIED):
        return value if value is not UNSPECIFIED else self.value

    def filter_is_any(self, data, value):
        """
        Special no-op filter which does no actual filtering.  Useful in some
        cases to add an "ineffective" option to the verb list for a given grid
        filter.
        """
        return data

    def render_value(self, value=UNSPECIFIED, **kwargs):
        """
        Render the HTML needed to expose the filter's value for user input.
        """
        if value is UNSPECIFIED:
            value = self.value
        kwargs['filtr'] = self
        return self.value_renderer.render(value=value, **kwargs)


class MobileFilter(GridFilter):
    """
    Base class for mobile grid filters.
    """
    default_verbs = ['equal']

    def __init__(self, key, **kwargs):
        kwargs.setdefault('default_active', True)
        kwargs.setdefault('default_verb', 'equal')
        super(MobileFilter, self).__init__(key, **kwargs)


class AlchemyGridFilter(GridFilter):
    """
    Base class for SQLAlchemy grid filters.
    """

    def __init__(self, *args, **kwargs):
        self.column = kwargs.pop('column')
        super(AlchemyGridFilter, self).__init__(*args, **kwargs)

    def filter_equal(self, query, value):
        """
        Filter data with an equal ('=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column == value)

    def filter_not_equal(self, query, value):
        """
        Filter data with a not eqaul ('!=') query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not equal' to something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            self.column != value,
        ))

    def filter_is_null(self, query, value):
        """
        Filter data with an 'IS NULL' query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == None)

    def filter_is_not_null(self, query, value):
        """
        Filter data with an 'IS NOT NULL' query.  Note that this filter does
        not use the value for anything.
        """
        return query.filter(self.column != None)

    def filter_greater_than(self, query, value):
        """
        Filter data with a greater than ('>') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column > value)

    def filter_greater_equal(self, query, value):
        """
        Filter data with a greater than or equal ('>=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column >= value)

    def filter_less_than(self, query, value):
        """
        Filter data with a less than ('<') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column < value)

    def filter_less_equal(self, query, value):
        """
        Filter data with a less than or equal ('<=') query.
        """
        if value is None or value == '':
            return query
        return query.filter(self.column <= value)


class AlchemyStringFilter(AlchemyGridFilter):
    """
    String filter for SQLAlchemy.
    """

    def default_verbs(self):
        """
        Expose contains / does-not-contain verbs in addition to core.
        """
        return ['contains', 'does_not_contain',
                'equal', 'not_equal', 'is_null', 'is_not_null', 'is_any']

    def filter_contains(self, query, value):
        """
        Filter data with a full 'ILIKE' query.
        """
        if value is None or value == '':
            return query
        return query.filter(sa.and_(
            *[self.column.ilike('%{}%'.format(v)) for v in value.split()]))

    def filter_does_not_contain(self, query, value):
        """
        Filter data with a full 'NOT ILIKE' query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not like' something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            sa.and_(
                *[~self.column.ilike('%{0}%'.format(v)) for v in value.split()]),
        ))


class AlchemyEmptyStringFilter(AlchemyStringFilter):
    """
    String filter with special logic to treat empty string values as NULL
    """

    def filter_is_null(self, query, value):
        return query.filter(
            sa.or_(
                self.column == None,
                sa.func.trim(self.column) == ''))

    def filter_is_not_null(self, query, value):
        return query.filter(
            sa.and_(
                self.column != None,
                sa.func.trim(self.column) != ''))


class AlchemyByteStringFilter(AlchemyStringFilter):
    """
    String filter for SQLAlchemy, which encodes value as bytestring before
    passing it along to the query.  Useful when querying certain databases
    (esp. via FreeTDS) which like to throw the occasional segfault...
    """
    value_encoding = 'utf-8'

    def get_value(self, value=UNSPECIFIED):
        value = super(AlchemyByteStringFilter, self).get_value(value)
        if isinstance(value, unicode):
            value = value.encode(self.value_encoding)
        return value

    def filter_contains(self, query, value):
        """
        Filter data with a full 'ILIKE' query.
        """
        if value is None or value == '':
            return query
        return query.filter(sa.and_(
            *[self.column.ilike(b'%{}%'.format(v)) for v in value.split()]))

    def filter_does_not_contain(self, query, value):
        """
        Filter data with a full 'NOT ILIKE' query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not like' something else, we must also
        # include things which are nothing at all, in our result set.
        return query.filter(sa.or_(
            self.column == None,
            sa.and_(
                *[~self.column.ilike(b'%{}%'.format(v)) for v in value.split()]),
        ))


class AlchemyNumericFilter(AlchemyGridFilter):
    """
    Numeric filter for SQLAlchemy.
    """
    value_renderer_factory = NumericValueRenderer

    # expose greater-than / less-than verbs in addition to core
    default_verbs = ['equal', 'not_equal', 'greater_than', 'greater_equal',
                     'less_than', 'less_equal', 'is_null', 'is_not_null', 'is_any']

    # TODO: what follows "works" in that it prevents an error...but from the
    # user's perspective it still fails silently...need to improve on front-end

    # try to detect (and ignore) common mistake where user enters UPC as search
    # term for integer field...

    def value_invalid(self, value):
        return bool(value and len(unicode(value)) > 8)

    def filter_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_equal(query, value)

    def filter_not_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_not_equal(query, value)

    def filter_greater_than(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_greater_than(query, value)

    def filter_greater_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_greater_equal(query, value)

    def filter_less_than(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_less_than(query, value)

    def filter_less_equal(self, query, value):
        if self.value_invalid(value):
            return query
        return super(AlchemyNumericFilter, self).filter_less_equal(query, value)


class AlchemyBooleanFilter(AlchemyGridFilter):
    """
    Boolean filter for SQLAlchemy.
    """
    default_verbs = ['is_true', 'is_false', 'is_any']

    def filter_is_true(self, query, value):
        """
        Filter data with an "is true" query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == True)

    def filter_is_false(self, query, value):
        """
        Filter data with an "is false" query.  Note that this filter does not
        use the value for anything.
        """
        return query.filter(self.column == False)


class AlchemyNullableBooleanFilter(AlchemyBooleanFilter):
    """
    Boolean filter for SQLAlchemy which is NULL-aware.
    """
    default_verbs = ['is_true', 'is_false', 'is_null', 'is_not_null', 'is_any']


class AlchemyDateFilter(AlchemyGridFilter):
    """
    Date filter for SQLAlchemy.
    """
    value_renderer_factory = DateValueRenderer

    verb_labels = {
        'equal':                "on",
        'not_equal':            "not on",
        'greater_than':         "after",
        'greater_equal':        "on or after",
        'less_than':            "before",
        'less_equal':           "on or before",
        'is_null':              "is null",
        'is_not_null':          "is not null",
        'is_any':               "is any",
    }

    def default_verbs(self):
        """
        Expose greater-than / less-than verbs in addition to core.
        """
        return ['equal', 'not_equal', 'greater_than', 'greater_equal',
                'less_than', 'less_equal', 'is_null', 'is_not_null', 'is_any']

    def make_date(self, value):
        """
        Convert user input to a proper ``datetime.date`` object.
        """
        if value:
            try:
                dt = datetime.datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                log.warning("invalid date value: {}".format(value))
            else:
                return dt.date()


class AlchemyDateTimeFilter(AlchemyDateFilter):
    """
    SQLAlchemy filter for datetime values.
    """

    def filter_equal(self, query, value):
        """
        Find all dateimes which fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = make_utc(localtime(self.config, start))

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = make_utc(localtime(self.config, stop))

        return query.filter(self.column >= start)\
                    .filter(self.column < stop)

    def filter_not_equal(self, query, value):
        """
        Find all dateimes which do *not* fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = make_utc(localtime(self.config, start))

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = make_utc(localtime(self.config, stop))

        return query.filter(sa.or_(
            self.column < start,
            self.column <= stop))

    def filter_greater_than(self, query, value):
        """
        Find all datetimes which fall after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column >= time)

    def filter_greater_equal(self, query, value):
        """
        Find all datetimes which fall on or after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column >= time)

    def filter_less_than(self, query, value):
        """
        Find all datetimes which fall before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column < time)

    def filter_less_equal(self, query, value):
        """
        Find all datetimes which fall on or before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = make_utc(localtime(self.config, time))
        return query.filter(self.column < time)


class AlchemyLocalDateTimeFilter(AlchemyDateTimeFilter):
    """
    SQLAlchemy filter for *local* datetime values.  This assumes datetime
    values in the database are for local timezone, as opposed to UTC.
    """

    def filter_equal(self, query, value):
        """
        Find all dateimes which fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = localtime(self.config, start, tzinfo=False)

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = localtime(self.config, stop, tzinfo=False)

        return query.filter(self.column >= start)\
                    .filter(self.column < stop)

    def filter_not_equal(self, query, value):
        """
        Find all dateimes which do *not* fall on the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        start = datetime.datetime.combine(date, datetime.time(0))
        start = localtime(self.config, start, tzinfo=False)

        stop = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        stop = localtime(self.config, stop, tzinfo=False)

        return query.filter(sa.or_(
            self.column < start,
            self.column <= stop))

    def filter_greater_than(self, query, value):
        """
        Find all datetimes which fall after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column >= time)

    def filter_greater_equal(self, query, value):
        """
        Find all datetimes which fall on or after the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column >= time)

    def filter_less_than(self, query, value):
        """
        Find all datetimes which fall before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date, datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column < time)

    def filter_less_equal(self, query, value):
        """
        Find all datetimes which fall on or before the given date.
        """
        date = self.make_date(value)
        if not date:
            return query

        time = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time(0))
        time = localtime(self.config, time, tzinfo=False)
        return query.filter(self.column < time)


class AlchemyGPCFilter(AlchemyGridFilter):
    """
    GPC filter for SQLAlchemy.
    """
    default_verbs = ['equal', 'not_equal']

    def filter_equal(self, query, value):
        """
        Filter data with an equal ('=') query.
        """
        if value is None or value == '':
            return query
        try:
            return query.filter(self.column.in_((
                GPC(value),
                GPC(value, calc_check_digit='upc'))))
        except ValueError:
            return query

    def filter_not_equal(self, query, value):
        """
        Filter data with a not eqaul ('!=') query.
        """
        if value is None or value == '':
            return query

        # When saying something is 'not equal' to something else, we must also
        # include things which are nothing at all, in our result set.
        try:
            return query.filter(sa.or_(
                ~self.column.in_((
                    GPC(value),
                    GPC(value, calc_check_digit='upc'))),
                self.column == None))
        except ValueError:
            return query


class GridFilterSet(OrderedDict):
    """
    Collection class for :class:`GridFilter` instances.
    """


class GridFiltersForm(Form):
    """
    Form for grid filters.
    """

    def __init__(self, request, filters, *args, **kwargs):
        super(GridFiltersForm, self).__init__(request, *args, **kwargs)
        self.filters = filters

    def iter_filters(self):
        return self.filters.itervalues()


class GridFiltersFormRenderer(FormRenderer):
    """
    Renderer for :class:`GridFiltersForm` instances.
    """

    @property
    def filters(self):
        return self.form.filters

    def iter_filters(self):
        return self.form.iter_filters()

    def tag(self, *args, **kwargs):
        """
        Convenience method which passes all args to the
        :meth:`webhelpers2:webhelpers2.html.builder.HTMLBuilder.tag()` method.
        """
        return HTML.tag(*args, **kwargs)

    # TODO: This seems hacky..?
    def checkbox(self, name, checked=None, **kwargs):
        """
        Custom checkbox implementation.
        """
        if name.endswith('-active'):
            return tags.checkbox(name, checked=checked, **kwargs)
        if checked is None:
            checked = False
        return super(GridFiltersFormRenderer, self).checkbox(name, checked=checked, **kwargs)

    def filter_verb(self, filtr):
        """
        Render the verb selection dropdown for the given filter.
        """
        options = [(v, filtr.verb_labels.get(v, "unknown verb '{0}'".format(v)))
                   for v in filtr.verbs]
        hide_values = [v for v in filtr.valueless_verbs
                       if v in filtr.verbs]
        return self.select('{0}.verb'.format(filtr.key), options, **{
            'class_': 'verb',
            'data-hide-value-for': ' '.join(hide_values)})

    def filter_value(self, filtr, **kwargs):
        """
        Render the value input element(s) for the filter.
        """
        style = 'display: none;' if filtr.verb in filtr.valueless_verbs else None
        return HTML.tag('div', class_='value', style=style,
                        c=filtr.render_value(**kwargs))
