# -*- coding: utf-8 -*-
from plone.app.z3cform.widget import IQueryStringWidget
from plone.app.z3cform.widget import QueryStringWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


__author__ = 'Tom Gross <itconsense@gmail.com>'


class ISortableQueryStringWidget(IQueryStringWidget):
    """

    """


@implementer_only(ISortableQueryStringWidget)
class SortableQueryStringWidget(QueryStringWidget):
    """QueryString widget for z3c.form."""

    pattern = 'sortablequerystring'
    pattern_options = QueryStringWidget.pattern_options.copy()

    def _base_args(self):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(SortableQueryStringWidget, self)._base_args()
        previewURL = args['pattern_options']['previewURL']
        args['pattern_options']['previewURL'] = previewURL.replace(
            '@@querybuilder_html_results',
            '@@sortable_querybuilder_html_results',
            1
        )
        return args


@implementer(IFieldWidget)
def SortableQueryStringFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra   # pragma: no cover
    return FieldWidget(field, SortableQueryStringWidget(request))


# EOF
