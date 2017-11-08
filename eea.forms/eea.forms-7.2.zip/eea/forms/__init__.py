""" Widgets
"""
from eea.forms import validators
from eea.forms import fields
from eea.forms import widgets

validators.register()
fields.register()
widgets.register()


def initialize(context):
    """ Zope 2 initialize
    """
    return
