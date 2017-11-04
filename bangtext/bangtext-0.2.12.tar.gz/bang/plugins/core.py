"""
in theory this is for core plugins that will be imported in bang __init__
"""
from __future__ import absolute_import
import os
import codecs

from .. import event, echo


#@event.bind('dom.pre')
#def make_hilightable(event_name, parent, elem, config):
#    pout.v(elem.tag)
#
