# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface


class ISuperfishSettings(Interface):
    """ """

    add_portal_tabs = schema.Bool(
        title=u'Add portal_tabs from portal_actions',
        default=False,
    )

    menu_depth = schema.Int(
        title=u'Menu depth',
        default=2,
    )

    superfish_options = schema.Text(
        title=u'Options for Superfish call',
    )
